# GutIntel Ingredient Template Documentation

## Overview
This document provides comprehensive information about the GutIntel ingredient template system for structured data entry.

## Template Structure

### Core Components

#### 1. Ingredient (Core Data)
- **name**: Primary ingredient name
- **slug**: URL-friendly identifier
- **aliases**: Alternative names
- **category**: Ingredient category (prebiotic, probiotic, fiber, etc.)
- **description**: Detailed description
- **gut_score**: Health score (0-10)
- **confidence_score**: Confidence level (0-1)
- **dosage_info**: Structured dosage information
- **safety_notes**: Safety and contraindication information

#### 2. Microbiome Effects
- **bacteria_name**: Specific bacteria affected
- **bacteria_level**: Effect direction (increase/decrease/modulate)
- **effect_type**: Type of bacterial effect
- **effect_strength**: Strength of effect (weak/moderate/strong)
- **mechanism**: Biological mechanism

#### 3. Metabolic Effects
- **effect_name**: Name of metabolic effect
- **effect_category**: Category of metabolic impact
- **impact_direction**: Direction of effect (positive/negative/neutral)
- **effect_strength**: Strength of effect
- **mechanism**: Biological mechanism

#### 4. Symptom Effects
- **symptom_name**: Affected symptom
- **symptom_category**: Category of symptom
- **effect_direction**: Effect direction
- **effect_strength**: Strength of effect
- **population_notes**: Population-specific notes

#### 5. Citations
- **pmid**: PubMed ID
- **doi**: DOI identifier
- **title**: Study title
- **authors**: Study authors
- **journal**: Journal name
- **publication_year**: Publication year
- **study_type**: Type of study
- **sample_size**: Study sample size
- **study_quality**: Quality score

#### 6. Interactions
- **ingredient_1_id**: First ingredient
- **ingredient_2_id**: Second ingredient
- **interaction_type**: Type of interaction
- **effect_description**: Description of interaction
- **confidence**: Confidence level

## Categories

### Prebiotic
- Focus on bacterial growth promotion
- Emphasize SCFA production
- Include fermentation mechanisms

### Probiotic
- Include strain-specific information
- Focus on colonization and survival
- Include CFU dosing information

### Fiber
- Emphasize mechanical and fermentation benefits
- Include soluble/insoluble properties
- Focus on digestive health outcomes

### Additive
- Include negative effects where applicable
- Focus on inflammatory responses
- Include avoidance recommendations

## Usage Examples

### Basic Template Generation
```bash
python template_generator.py generate --name "psyllium-husk" --category "fiber"
```

### Validation
```bash
python template_generator.py validate --file "inulin.json" --dry-run
```

### Batch Processing
```bash
python template_generator.py batch --directory "./ingredients/"
```

## Best Practices

1. **Always validate templates** before database insertion
2. **Use realistic examples** in placeholder text
3. **Include confidence scores** for all effects
4. **Provide comprehensive safety notes**
5. **Link to high-quality citations**
6. **Use specific bacterial strain names** when possible
7. **Include population-specific notes** for effects

## Validation Rules

- Gut scores: 0-10 (1 decimal place)
- Confidence scores: 0-1 (2 decimal places)
- Slugs: lowercase, hyphens, alphanumeric only
- PMIDs: 1-8 digits
- DOIs: Must start with "10."

## Error Handling

The system provides detailed error messages for:
- Missing required fields
- Invalid data types
- Constraint violations
- Malformed identifiers
- Placeholder text detection

## Support

For questions or issues, refer to the main GutIntel documentation or contact the development team.
