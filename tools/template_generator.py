#!/usr/bin/env python3
"""
GutIntel Ingredient Template Generator

A comprehensive tool for generating, validating, and managing JSON templates
for ingredient data entry in the GutIntel database.

Usage:
    python template_generator.py generate --name "psyllium-husk" --category "fiber"
    python template_generator.py validate --file "inulin.json"
    python template_generator.py batch --directory "./ingredients/"
"""

import json
import csv
import click
import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from enum import Enum


class IngredientCategory(str, Enum):
    """Valid ingredient categories."""
    PROBIOTIC = "probiotic"
    PREBIOTIC = "prebiotic"
    POSTBIOTIC = "postbiotic"
    FIBER = "fiber"
    POLYPHENOL = "polyphenol"
    FATTY_ACID = "fatty_acid"
    VITAMIN = "vitamin"
    MINERAL = "mineral"
    HERB = "herb"
    OTHER = "other"


class EffectDirection(str, Enum):
    """Effect direction values."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EffectStrength(str, Enum):
    """Effect strength values."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class BacteriaLevel(str, Enum):
    """Bacteria level change values."""
    INCREASE = "increase"
    DECREASE = "decrease"
    MODULATE = "modulate"


class InteractionType(str, Enum):
    """Ingredient interaction types."""
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class StudyType(str, Enum):
    """Study type values."""
    RCT = "rct"
    OBSERVATIONAL = "observational"
    META_ANALYSIS = "meta_analysis"
    REVIEW = "review"
    CASE_STUDY = "case_study"
    IN_VITRO = "in_vitro"
    ANIMAL = "animal"


class TemplateGenerator:
    """Main template generator class."""
    
    def __init__(self):
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
    def generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from ingredient name."""
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def generate_template(self, ingredient_name: str, category: str) -> Dict[str, Any]:
        """
        Generate a structured JSON template for ingredient data entry.
        
        Args:
            ingredient_name: Name of the ingredient
            category: Category of the ingredient
            
        Returns:
            Dictionary containing the complete ingredient template
        """
        if category not in [c.value for c in IngredientCategory]:
            raise ValueError(f"Invalid category: {category}. Must be one of: {[c.value for c in IngredientCategory]}")
        
        slug = self.generate_slug(ingredient_name)
        current_time = datetime.now().isoformat()
        
        template = {
            "ingredient": {
                "id": str(uuid.uuid4()),
                "name": ingredient_name,
                "slug": slug,
                "aliases": [
                    f"[Example: Alternative name for {ingredient_name}]",
                    f"[Example: Common name for {ingredient_name}]"
                ],
                "category": category,
                "description": f"[Description of {ingredient_name}. Include origin, properties, and general health benefits. Example: {ingredient_name} is a natural compound that...]",
                "gut_score": "[Enter gut health score from 0-10, rounded to 1 decimal place. Example: 8.5]",
                "confidence_score": "[Enter confidence score from 0-1, rounded to 2 decimal places. Example: 0.85]",
                "dosage_info": {
                    "min_dose": "[Minimum effective dose. Example: 500]",
                    "max_dose": "[Maximum safe dose. Example: 2000]",
                    "unit": "[Unit of measurement. Example: mg, g, CFU]",
                    "frequency": "[Dosing frequency. Example: daily, twice daily]",
                    "duration": "[Treatment duration. Example: 4-8 weeks]",
                    "form": "[Form of supplement. Example: capsule, powder, liquid]",
                    "timing": "[When to take. Example: with meals, on empty stomach]",
                    "notes": "[Additional dosing notes. Example: Start with lower dose]"
                },
                "safety_notes": f"[Safety information for {ingredient_name}. Include contraindications, side effects, and precautions. Example: Generally safe for most adults...]",
                "created_at": current_time,
                "updated_at": current_time
            },
            "microbiome_effects": [
                {
                    "id": str(uuid.uuid4()),
                    "ingredient_id": "[Will be populated with ingredient ID]",
                    "bacteria_name": "[Name of affected bacteria. Example: Bifidobacterium longum]",
                    "bacteria_level": "[increase/decrease/modulate]",
                    "effect_type": "[Type of effect. Example: growth promotion, inhibition]",
                    "effect_strength": "[weak/moderate/strong]",
                    "confidence": "[Confidence score 0-1. Example: 0.75]",
                    "mechanism": "[Description of how it works. Example: Provides substrate for bacterial fermentation]",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            ],
            "metabolic_effects": [
                {
                    "id": str(uuid.uuid4()),
                    "ingredient_id": "[Will be populated with ingredient ID]",
                    "effect_name": "[Name of metabolic effect. Example: SCFA production]",
                    "effect_category": "[Category. Example: short-chain fatty acids, inflammation]",
                    "impact_direction": "[positive/negative/neutral]",
                    "effect_strength": "[weak/moderate/strong]",
                    "confidence": "[Confidence score 0-1. Example: 0.80]",
                    "dosage_dependent": "[true/false - whether effect depends on dosage]",
                    "mechanism": "[How it affects metabolism. Example: Enhances butyrate production through bacterial fermentation]",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            ],
            "symptom_effects": [
                {
                    "id": str(uuid.uuid4()),
                    "ingredient_id": "[Will be populated with ingredient ID]",
                    "symptom_name": "[Symptom affected. Example: bloating, constipation]",
                    "symptom_category": "[Category. Example: digestive, inflammatory]",
                    "effect_direction": "[positive/negative/neutral]",
                    "effect_strength": "[weak/moderate/strong]",
                    "confidence": "[Confidence score 0-1. Example: 0.70]",
                    "dosage_dependent": "[true/false]",
                    "population_notes": "[Notes about specific populations. Example: More effective in adults over 50]",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            ],
            "citations": [
                {
                    "id": str(uuid.uuid4()),
                    "pmid": "[PubMed ID, 1-8 digits. Example: 12345678]",
                    "doi": "[DOI starting with 10. Example: 10.1038/s41598-020-12345-6]",
                    "title": "[Study title. Example: Effects of prebiotic supplementation on gut microbiome]",
                    "authors": "[Study authors. Example: Smith J, Johnson A, Brown K]",
                    "journal": "[Journal name. Example: Nature Scientific Reports]",
                    "publication_year": "[Year 1900-2025. Example: 2023]",
                    "study_type": "[rct/observational/meta_analysis/review/case_study/in_vitro/animal]",
                    "sample_size": "[Sample size >0. Example: 120]",
                    "study_quality": "[Quality score 0-1. Example: 0.85]",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            ],
            "interactions": [
                {
                    "id": str(uuid.uuid4()),
                    "ingredient_1_id": "[First ingredient ID]",
                    "ingredient_2_id": "[Second ingredient ID]",
                    "interaction_type": "[synergistic/antagonistic/neutral/unknown]",
                    "effect_description": "[Description of interaction. Example: Enhances absorption when taken together]",
                    "confidence": "[Confidence score 0-1. Example: 0.65]",
                    "created_at": current_time,
                    "updated_at": current_time
                }
            ]
        }
        
        return self._apply_category_specific_examples(template, category)
    
    def _apply_category_specific_examples(self, template: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Apply category-specific examples to the template."""
        category_examples = {
            "prebiotic": {
                "bacteria_example": "Bifidobacterium longum",
                "effect_example": "Selective bacterial growth promotion",
                "metabolic_example": "Butyrate production enhancement",
                "symptom_example": "Improved bowel regularity"
            },
            "probiotic": {
                "bacteria_example": "Lactobacillus rhamnosus GG",
                "effect_example": "Direct bacterial colonization",
                "metabolic_example": "Lactate production",
                "symptom_example": "Reduced antibiotic-associated diarrhea"
            },
            "fiber": {
                "bacteria_example": "Faecalibacterium prausnitzii",
                "effect_example": "Substrate provision for fermentation",
                "metabolic_example": "Short-chain fatty acid production",
                "symptom_example": "Improved stool consistency"
            },
            "polyphenol": {
                "bacteria_example": "Akkermansia muciniphila",
                "effect_example": "Antioxidant activity modulation",
                "metabolic_example": "Metabolite transformation",
                "symptom_example": "Reduced inflammation markers"
            }
        }
        
        if category in category_examples:
            examples = category_examples[category]
            
            if template["microbiome_effects"]:
                template["microbiome_effects"][0]["bacteria_name"] = f"[Example: {examples['bacteria_example']}]"
                template["microbiome_effects"][0]["effect_type"] = f"[Example: {examples['effect_example']}]"
            
            if template["metabolic_effects"]:
                template["metabolic_effects"][0]["effect_name"] = f"[Example: {examples['metabolic_example']}]"
            
            if template["symptom_effects"]:
                template["symptom_effects"][0]["symptom_name"] = f"[Example: {examples['symptom_example']}]"
        
        return template
    
    def save_template(self, template: Dict[str, Any], filename: str) -> str:
        """Save template to file."""
        filepath = self.templates_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        return str(filepath)
    
    def validate_template(self, json_file: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Validate a template JSON file.
        
        Args:
            json_file: Path to JSON file to validate
            dry_run: If True, only validate without processing
            
        Returns:
            Dictionary containing validation results
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Invalid JSON: {e}"]}
        except FileNotFoundError:
            return {"valid": False, "errors": [f"File not found: {json_file}"]}
        
        errors = []
        warnings = []
        
        # Validate main structure
        required_sections = ["ingredient", "microbiome_effects", "metabolic_effects", "symptom_effects", "citations", "interactions"]
        for section in required_sections:
            if section not in data:
                errors.append(f"Missing required section: {section}")
        
        # Validate ingredient section
        if "ingredient" in data:
            ingredient = data["ingredient"]
            
            # Required fields
            required_fields = ["name", "slug", "category"]
            for field in required_fields:
                if field not in ingredient or not ingredient[field]:
                    errors.append(f"Missing required ingredient field: {field}")
            
            # Validate category
            if "category" in ingredient:
                if ingredient["category"] not in [c.value for c in IngredientCategory]:
                    errors.append(f"Invalid category: {ingredient['category']}")
            
            # Validate slug format
            if "slug" in ingredient:
                slug = ingredient["slug"]
                if not re.match(r'^[a-z0-9-]+$', slug):
                    errors.append(f"Invalid slug format: {slug}. Must contain only lowercase letters, numbers, and hyphens")
            
            # Validate gut_score
            if "gut_score" in ingredient and ingredient["gut_score"] is not None:
                try:
                    score = float(ingredient["gut_score"])
                    if not (0 <= score <= 10):
                        errors.append("gut_score must be between 0 and 10")
                except (ValueError, TypeError):
                    errors.append("gut_score must be a number")
            
            # Validate confidence_score
            if "confidence_score" in ingredient and ingredient["confidence_score"] is not None:
                try:
                    score = float(ingredient["confidence_score"])
                    if not (0 <= score <= 1):
                        errors.append("confidence_score must be between 0 and 1")
                except (ValueError, TypeError):
                    errors.append("confidence_score must be a number")
            
            # Check for placeholder text
            for key, value in ingredient.items():
                if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                    warnings.append(f"Placeholder text found in ingredient.{key}: {value}")
        
        # Validate effects sections
        effect_sections = ["microbiome_effects", "metabolic_effects", "symptom_effects"]
        for section in effect_sections:
            if section in data:
                for i, effect in enumerate(data[section]):
                    if isinstance(effect, dict):
                        # Check for placeholder text
                        for key, value in effect.items():
                            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                                warnings.append(f"Placeholder text found in {section}[{i}].{key}: {value}")
        
        # Validate citations
        if "citations" in data:
            for i, citation in enumerate(data["citations"]):
                if isinstance(citation, dict):
                    # Validate PMID format
                    if "pmid" in citation and citation["pmid"]:
                        pmid = str(citation["pmid"])
                        if not re.match(r'^\d{1,8}$', pmid):
                            errors.append(f"Invalid PMID format in citation[{i}]: {pmid}")
                    
                    # Validate DOI format
                    if "doi" in citation and citation["doi"]:
                        doi = citation["doi"]
                        if not doi.startswith("10."):
                            errors.append(f"Invalid DOI format in citation[{i}]: {doi}")
                    
                    # Validate study_type
                    if "study_type" in citation:
                        if citation["study_type"] not in [s.value for s in StudyType]:
                            errors.append(f"Invalid study_type in citation[{i}]: {citation['study_type']}")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file": json_file
        }
        
        if dry_run:
            result["dry_run"] = True
            result["preview"] = "Template validation complete. Ready for database insertion."
        
        return result


def get_category_templates() -> Dict[str, Dict[str, Any]]:
    """Get pre-defined templates for each category with realistic examples."""
    generator = TemplateGenerator()
    
    templates = {
        "prebiotic": {
            "name": "Inulin",
            "description": "Inulin is a type of soluble fiber and prebiotic that occurs naturally in many plants. It acts as a prebiotic by selectively stimulating the growth and activity of beneficial bacteria in the colon, particularly Bifidobacterium species.",
            "bacteria_example": "Bifidobacterium longum",
            "bacteria_level": "increase",
            "effect_type": "selective growth promotion",
            "metabolic_effect": "Short-chain fatty acid production",
            "symptom_effect": "Improved bowel regularity",
            "dosage": {"min_dose": 2.5, "max_dose": 10, "unit": "g", "frequency": "daily"}
        },
        "probiotic": {
            "name": "Lactobacillus rhamnosus GG",
            "description": "Lactobacillus rhamnosus GG is one of the most extensively studied probiotic strains. It has demonstrated ability to survive gastric acid and colonize the intestinal tract, providing various health benefits including immune system support and digestive health.",
            "bacteria_example": "Lactobacillus rhamnosus GG",
            "bacteria_level": "increase",
            "effect_type": "direct bacterial colonization",
            "metabolic_effect": "Lactate and acetate production",
            "symptom_effect": "Reduced antibiotic-associated diarrhea",
            "dosage": {"min_dose": 1e9, "max_dose": 1e11, "unit": "CFU", "frequency": "daily"}
        },
        "fiber": {
            "name": "Psyllium Husk",
            "description": "Psyllium husk is a form of soluble fiber derived from the seeds of Plantago ovata. It forms a gel-like substance when mixed with water and serves as both a prebiotic and mechanical cleanser for the digestive system.",
            "bacteria_example": "Faecalibacterium prausnitzii",
            "bacteria_level": "increase",
            "effect_type": "substrate provision for fermentation",
            "metabolic_effect": "Butyrate production enhancement",
            "symptom_effect": "Improved stool consistency and reduced constipation",
            "dosage": {"min_dose": 3.4, "max_dose": 10.2, "unit": "g", "frequency": "daily"}
        },
        "additive": {
            "name": "Carrageenan",
            "description": "Carrageenan is a food additive extracted from red seaweed, commonly used as a thickener and stabilizer in processed foods. Research suggests it may have negative effects on gut health and inflammation.",
            "bacteria_example": "Akkermansia muciniphila",
            "bacteria_level": "decrease",
            "effect_type": "mucosal barrier disruption",
            "metabolic_effect": "Increased inflammatory markers",
            "symptom_effect": "Potential increase in digestive discomfort",
            "dosage": {"min_dose": 0, "max_dose": 0, "unit": "mg", "frequency": "avoid"}
        }
    }
    
    return templates


# Helper Functions

def convert_csv_to_json(csv_file: str, output_dir: str = "templates") -> List[str]:
    """
    Convert CSV file to JSON templates.
    
    Args:
        csv_file: Path to CSV file
        output_dir: Directory to save JSON files
        
    Returns:
        List of created file paths
    """
    generator = TemplateGenerator()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    created_files = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'name' in row and 'category' in row:
                    name = row['name'].strip()
                    category = row['category'].strip()
                    
                    if name and category:
                        template = generator.generate_template(name, category)
                        filename = f"{generator.generate_slug(name)}.json"
                        filepath = output_path / filename
                        
                        with open(filepath, 'w', encoding='utf-8') as out_f:
                            json.dump(template, out_f, indent=2, ensure_ascii=False)
                        
                        created_files.append(str(filepath))
    
    except Exception as e:
        raise RuntimeError(f"Error converting CSV to JSON: {e}")
    
    return created_files


def merge_templates(template_files: List[str], output_file: str) -> str:
    """
    Merge multiple template files into a single JSON file.
    
    Args:
        template_files: List of template file paths
        output_file: Output file path
        
    Returns:
        Path to merged file
    """
    merged_data = []
    
    for file_path in template_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.append(data)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    return output_file


def export_template_docs(output_file: str = "template_documentation.md") -> str:
    """
    Export template documentation for team reference.
    
    Args:
        output_file: Output markdown file path
        
    Returns:
        Path to documentation file
    """
    docs = """# GutIntel Ingredient Template Documentation

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
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(docs)
    
    return output_file


# CLI Interface

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GutIntel Ingredient Template Generator CLI"""
    pass


@cli.command()
@click.option('--name', required=True, help='Ingredient name')
@click.option('--category', required=True, 
              type=click.Choice([c.value for c in IngredientCategory]), 
              help='Ingredient category')
@click.option('--output', default=None, help='Output file path')
def generate(name: str, category: str, output: Optional[str]):
    """Generate a new ingredient template."""
    generator = TemplateGenerator()
    
    try:
        template = generator.generate_template(name, category)
        
        if output is None:
            output = f"{generator.generate_slug(name)}.json"
        
        filepath = generator.save_template(template, output)
        click.echo(f"Template generated: {filepath}")
        
    except Exception as e:
        click.echo(f"Error generating template: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--file', required=True, help='JSON file to validate')
@click.option('--dry-run', is_flag=True, help='Validate only, do not process')
def validate(file: str, dry_run: bool):
    """Validate an ingredient template."""
    generator = TemplateGenerator()
    
    try:
        result = generator.validate_template(file, dry_run)
        
        if result['valid']:
            click.echo(f"✓ Template is valid: {file}")
            if result['warnings']:
                click.echo("Warnings:")
                for warning in result['warnings']:
                    click.echo(f"  - {warning}")
        else:
            click.echo(f"✗ Template validation failed: {file}")
            for error in result['errors']:
                click.echo(f"  Error: {error}")
            raise click.Abort()
        
        if dry_run:
            click.echo("Dry run complete. Template ready for database insertion.")
            
    except Exception as e:
        click.echo(f"Error validating template: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--directory', required=True, help='Directory containing JSON files')
@click.option('--validate-only', is_flag=True, help='Only validate, do not process')
def batch(directory: str, validate_only: bool):
    """Process multiple templates in a directory."""
    generator = TemplateGenerator()
    
    try:
        json_files = list(Path(directory).glob("*.json"))
        
        if not json_files:
            click.echo(f"No JSON files found in {directory}")
            return
        
        results = []
        for json_file in json_files:
            result = generator.validate_template(str(json_file), validate_only)
            results.append(result)
        
        # Summary
        valid_count = sum(1 for r in results if r['valid'])
        total_count = len(results)
        
        click.echo(f"\nProcessed {total_count} files:")
        click.echo(f"✓ Valid: {valid_count}")
        click.echo(f"✗ Invalid: {total_count - valid_count}")
        
        # Show errors
        for result in results:
            if not result['valid']:
                click.echo(f"\nErrors in {result['file']}:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
        
    except Exception as e:
        click.echo(f"Error processing batch: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--csv-file', required=True, help='CSV file to convert')
@click.option('--output-dir', default='templates', help='Output directory')
def csv_convert(csv_file: str, output_dir: str):
    """Convert CSV file to JSON templates."""
    try:
        created_files = convert_csv_to_json(csv_file, output_dir)
        click.echo(f"Created {len(created_files)} template files in {output_dir}")
        
    except Exception as e:
        click.echo(f"Error converting CSV: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--output', default='template_documentation.md', help='Output file')
def docs(output: str):
    """Generate template documentation."""
    try:
        filepath = export_template_docs(output)
        click.echo(f"Documentation generated: {filepath}")
        
    except Exception as e:
        click.echo(f"Error generating docs: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()