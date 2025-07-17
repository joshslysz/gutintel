-- GutIntel Database Schema
-- PostgreSQL database schema for gut health API

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types for enums
CREATE TYPE effect_direction AS ENUM ('positive', 'negative', 'neutral');
CREATE TYPE effect_strength AS ENUM ('weak', 'moderate', 'strong');
CREATE TYPE bacteria_level AS ENUM ('increase', 'decrease', 'modulate');
CREATE TYPE interaction_type AS ENUM ('synergistic', 'antagonistic', 'neutral', 'unknown');
CREATE TYPE study_type AS ENUM ('rct', 'observational', 'meta_analysis', 'review', 'case_study', 'in_vitro', 'animal');
CREATE TYPE ingredient_category AS ENUM ('probiotic', 'prebiotic', 'postbiotic', 'fiber', 'polyphenol', 'fatty_acid', 'vitamin', 'mineral', 'herb', 'other');

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 1. Ingredients table
CREATE TABLE ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    aliases TEXT[], -- Array of alternative names
    category ingredient_category NOT NULL,
    description TEXT,
    gut_score DECIMAL(3,1) CHECK (gut_score >= 0 AND gut_score <= 10),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    dosage_info JSONB, -- Flexible dosage information
    safety_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Microbiome effects table
CREATE TABLE microbiome_effects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    bacteria_name VARCHAR(255) NOT NULL,
    bacteria_level bacteria_level NOT NULL,
    effect_type VARCHAR(100), -- e.g., 'growth', 'inhibition', 'metabolism'
    effect_strength effect_strength NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    mechanism TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Metabolic effects table
CREATE TABLE metabolic_effects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    effect_name VARCHAR(255) NOT NULL,
    effect_category VARCHAR(100), -- e.g., 'inflammation', 'metabolism', 'immunity'
    impact_direction effect_direction NOT NULL,
    effect_strength effect_strength NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    dosage_dependent BOOLEAN DEFAULT FALSE,
    mechanism TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Symptom effects table
CREATE TABLE symptom_effects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    symptom_name VARCHAR(255) NOT NULL,
    symptom_category VARCHAR(100), -- e.g., 'digestive', 'mood', 'immune'
    effect_direction effect_direction NOT NULL,
    effect_strength effect_strength NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    dosage_dependent BOOLEAN DEFAULT FALSE,
    population_notes TEXT, -- Notes about specific populations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Citations table
CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pmid VARCHAR(20) UNIQUE, -- PubMed ID
    doi VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    journal VARCHAR(255),
    publication_year INTEGER CHECK (publication_year >= 1900 AND publication_year <= EXTRACT(year FROM CURRENT_DATE)),
    study_type study_type NOT NULL,
    sample_size INTEGER CHECK (sample_size > 0),
    study_quality DECIMAL(3,2) CHECK (study_quality >= 0 AND study_quality <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Effect citations linking table
CREATE TABLE effect_citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citation_id UUID NOT NULL REFERENCES citations(id) ON DELETE CASCADE,
    effect_type VARCHAR(50) NOT NULL, -- 'microbiome', 'metabolic', 'symptom'
    effect_id UUID NOT NULL, -- References the specific effect record
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0 AND relevance_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_effect_type CHECK (effect_type IN ('microbiome', 'metabolic', 'symptom')),
    UNIQUE(citation_id, effect_type, effect_id)
);

-- 7. Ingredient interactions table
CREATE TABLE ingredient_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_1_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    ingredient_2_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    interaction_type interaction_type NOT NULL,
    effect_description TEXT,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT no_self_interaction CHECK (ingredient_1_id != ingredient_2_id),
    CONSTRAINT ordered_interaction CHECK (ingredient_1_id < ingredient_2_id),
    UNIQUE(ingredient_1_id, ingredient_2_id)
);

-- Create indexes for performance optimization
CREATE INDEX idx_ingredients_slug ON ingredients(slug);
CREATE INDEX idx_ingredients_category ON ingredients(category);
CREATE INDEX idx_ingredients_gut_score ON ingredients(gut_score);
CREATE INDEX idx_ingredients_aliases ON ingredients USING GIN(aliases);

CREATE INDEX idx_microbiome_effects_ingredient_id ON microbiome_effects(ingredient_id);
CREATE INDEX idx_microbiome_effects_bacteria_name ON microbiome_effects(bacteria_name);
CREATE INDEX idx_microbiome_effects_effect_strength ON microbiome_effects(effect_strength);

CREATE INDEX idx_metabolic_effects_ingredient_id ON metabolic_effects(ingredient_id);
CREATE INDEX idx_metabolic_effects_category ON metabolic_effects(effect_category);
CREATE INDEX idx_metabolic_effects_direction ON metabolic_effects(impact_direction);

CREATE INDEX idx_symptom_effects_ingredient_id ON symptom_effects(ingredient_id);
CREATE INDEX idx_symptom_effects_symptom_name ON symptom_effects(symptom_name);
CREATE INDEX idx_symptom_effects_category ON symptom_effects(symptom_category);

CREATE INDEX idx_citations_pmid ON citations(pmid);
CREATE INDEX idx_citations_doi ON citations(doi);
CREATE INDEX idx_citations_publication_year ON citations(publication_year);
CREATE INDEX idx_citations_study_type ON citations(study_type);

CREATE INDEX idx_effect_citations_citation_id ON effect_citations(citation_id);
CREATE INDEX idx_effect_citations_effect_type ON effect_citations(effect_type);
CREATE INDEX idx_effect_citations_effect_id ON effect_citations(effect_id);

CREATE INDEX idx_ingredient_interactions_ingredient_1 ON ingredient_interactions(ingredient_1_id);
CREATE INDEX idx_ingredient_interactions_ingredient_2 ON ingredient_interactions(ingredient_2_id);
CREATE INDEX idx_ingredient_interactions_type ON ingredient_interactions(interaction_type);

-- Create updated_at triggers for all tables
CREATE TRIGGER update_ingredients_updated_at BEFORE UPDATE ON ingredients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_microbiome_effects_updated_at BEFORE UPDATE ON microbiome_effects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_metabolic_effects_updated_at BEFORE UPDATE ON metabolic_effects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_symptom_effects_updated_at BEFORE UPDATE ON symptom_effects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_citations_updated_at BEFORE UPDATE ON citations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ingredient_interactions_updated_at BEFORE UPDATE ON ingredient_interactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW ingredient_summary AS
SELECT 
    i.id,
    i.name,
    i.slug,
    i.category,
    i.gut_score,
    i.confidence_score,
    COUNT(DISTINCT me.id) as microbiome_effects_count,
    COUNT(DISTINCT met.id) as metabolic_effects_count,
    COUNT(DISTINCT se.id) as symptom_effects_count
FROM ingredients i
LEFT JOIN microbiome_effects me ON i.id = me.ingredient_id
LEFT JOIN metabolic_effects met ON i.id = met.ingredient_id
LEFT JOIN symptom_effects se ON i.id = se.ingredient_id
GROUP BY i.id, i.name, i.slug, i.category, i.gut_score, i.confidence_score;

-- Add comments for documentation
COMMENT ON TABLE ingredients IS 'Core ingredient information with gut health scoring';
COMMENT ON TABLE microbiome_effects IS 'Effects of ingredients on specific gut bacteria';
COMMENT ON TABLE metabolic_effects IS 'Metabolic effects of ingredients on gut health';
COMMENT ON TABLE symptom_effects IS 'Effects of ingredients on gut health symptoms';
COMMENT ON TABLE citations IS 'Scientific citations supporting the effects data';
COMMENT ON TABLE effect_citations IS 'Many-to-many linking table between citations and all effect types';
COMMENT ON TABLE ingredient_interactions IS 'Interactions between different ingredients';

COMMENT ON COLUMN ingredients.gut_score IS 'Overall gut health score from 0-10';
COMMENT ON COLUMN ingredients.confidence_score IS 'Confidence in the gut_score from 0-1';
COMMENT ON COLUMN ingredients.dosage_info IS 'JSONB field for flexible dosage information';
COMMENT ON COLUMN effect_citations.effect_type IS 'Type of effect: microbiome, metabolic, or symptom';
COMMENT ON COLUMN effect_citations.effect_id IS 'UUID reference to the specific effect record';