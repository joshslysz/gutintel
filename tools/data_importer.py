#!/usr/bin/env python3
"""
GutIntel Bulk Data Importer

A comprehensive tool for importing ingredient data from JSON files into the GutIntel database.
Supports validation, batch processing, error handling, and various import modes.

Usage:
    ./gutintel-import single --file "inulin.json" --dry-run
    ./gutintel-import batch --directory "./ingredients/" --update-existing
    ./gutintel-import validate --file "inulin.json" --verbose

Features:
    - JSON file validation against Pydantic models
    - Batch import with progress tracking
    - Error handling and detailed reporting
    - Multiple import modes (dry-run, update, skip duplicates)
    - Auto-slug generation and PMID validation
    - Transaction rollback on failures
    - Comprehensive logging

## Example Usage

### Single File Import
```bash
# Dry run validation
./gutintel-import single --file "ingredients/inulin.json" --dry-run

# Import with update existing
./gutintel-import single --file "ingredients/inulin.json" --update-existing

# Force import (overwrite existing)
./gutintel-import single --file "ingredients/inulin.json" --force-import
```

### Batch Directory Import
```bash
# Import all JSON files in directory
./gutintel-import batch --directory "./ingredients/"

# Skip existing ingredients
./gutintel-import batch --directory "./ingredients/" --skip-duplicates

# Update existing ingredients
./gutintel-import batch --directory "./ingredients/" --update-existing
```

### Validation Only
```bash
# Validate single file
./gutintel-import validate --file "ingredients/inulin.json" --verbose

# Validate entire directory
./gutintel-import validate --directory "./ingredients/" --verbose
```

## Import Modes

1. **dry_run=True** - Validates and reports without database changes
2. **update_existing=True** - Updates existing ingredients instead of failing
3. **skip_duplicates=True** - Skips existing ingredients silently
4. **force_import=True** - Overwrites existing data

## Data Processing Features

- Auto-generate slugs from ingredient names
- Validate PMID citations against format rules
- Cross-reference ingredient interactions for consistency
- Calculate derived fields (effect counts, confidence averages)
- UUID generation for missing IDs
- Comprehensive field validation

## Error Handling

- Detailed validation error messages with field-specific feedback
- Duplicate detection (by name/slug) with merge options
- Transaction rollback on batch import failures
- Comprehensive import logs with timestamps

## Troubleshooting

### Common Issues

1. **Invalid JSON Format**
   - Ensure JSON files are properly formatted
   - Check for missing commas or brackets
   - Use a JSON validator tool

2. **Missing Required Fields**
   - Ensure all required fields are present
   - Check field names match the schema
   - Review example JSON files

3. **PMID Validation Errors**
   - PMID must be 1-8 digits only
   - Remove any prefixes like "PMID:"
   - Ensure numeric format

4. **Database Connection Issues**
   - Check DATABASE_URL environment variable
   - Ensure database is running
   - Verify connection permissions

5. **Duplicate Ingredient Errors**
   - Use --skip-duplicates to skip existing
   - Use --update-existing to update existing
   - Use --force-import to overwrite

### Log Files

Import logs are saved to:
- `logs/import.log` - Main import log
- `logs/gutintel.log` - Application log

### Performance Tips

- Use batch import for multiple files
- Enable progress bars for large imports
- Use --no-progress for automated scripts
- Monitor memory usage for large datasets
"""

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import asyncpg
from pydantic import ValidationError as PydanticValidationError
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings
from database.connection import get_database, Database
from database.repositories import (
    IngredientRepository,
    create_ingredient_repository,
    DuplicateIngredientError,
    ValidationError as RepositoryValidationError,
    DatabaseOperationError,
)
from models.ingredient import (
    CompleteIngredientModel,
    IngredientModel,
    MicrobiomeEffectModel,
    MetabolicEffectModel,
    SymptomEffectModel,
    CitationModel,
    IngredientInteractionModel,
    IngredientCategory,
    EffectDirection,
    EffectStrength,
    BacteriaLevel,
    InteractionType,
    StudyType,
)


class ImportError(Exception):
    """Base exception for import operations."""
    pass


class ValidationError(ImportError):
    """Raised when validation fails."""
    pass


class DataProcessingError(ImportError):
    """Raised when data processing fails."""
    pass


class ImportResult:
    """Result of an import operation."""
    
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.imported_ids: List[UUID] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        
    def add_success(self, ingredient_id: UUID, filename: str):
        """Add successful import."""
        self.success_count += 1
        self.imported_ids.append(ingredient_id)
        
    def add_failure(self, filename: str, error: str, details: Optional[Dict] = None):
        """Add failed import."""
        self.failure_count += 1
        self.errors.append({
            'filename': filename,
            'error': error,
            'details': details or {},
            'timestamp': datetime.now()
        })
        
    def add_skip(self, filename: str, reason: str):
        """Add skipped import."""
        self.skipped_count += 1
        self.warnings.append({
            'filename': filename,
            'reason': reason,
            'timestamp': datetime.now()
        })
        
    def add_warning(self, filename: str, message: str):
        """Add warning."""
        self.warnings.append({
            'filename': filename,
            'message': message,
            'timestamp': datetime.now()
        })
        
    def finalize(self):
        """Finalize the import result."""
        self.end_time = datetime.now()
        
    @property
    def duration(self) -> float:
        """Get import duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
        
    @property
    def total_processed(self) -> int:
        """Get total number of files processed."""
        return self.success_count + self.failure_count + self.skipped_count
        
    def summary(self) -> Dict[str, Any]:
        """Get summary of import results."""
        return {
            'total_processed': self.total_processed,
            'successful': self.success_count,
            'failed': self.failure_count,
            'skipped': self.skipped_count,
            'duration_seconds': self.duration,
            'errors': len(self.errors),
            'warnings': len(self.warnings)
        }


class DataImporter:
    """Main data importer class."""
    
    def __init__(self, repository: IngredientRepository, logger: logging.Logger):
        self.repository = repository
        self.logger = logger
        self.settings = get_settings()
        
    def generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from ingredient name."""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug
        
    def validate_pmid(self, pmid: str) -> bool:
        """Validate PMID format (1-8 digits)."""
        if not pmid:
            return False
        return bool(re.match(r'^\d{1,8}$', pmid))
        
    def validate_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        if not doi:
            return False
        return bool(re.match(r'^10\.\d{4,}/.+', doi))
        
    def process_ingredient_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance ingredient data."""
        processed = data.copy()
        
        # Auto-generate slug if missing
        if 'slug' not in processed.get('ingredient', {}):
            name = processed.get('ingredient', {}).get('name', '')
            if name:
                processed['ingredient']['slug'] = self.generate_slug(name)
                
        # Validate and fix UUIDs
        processed = self._fix_uuids(processed)
        
        # Validate PMID citations
        citations = processed.get('citations', [])
        for citation in citations:
            if 'pmid' in citation and citation['pmid']:
                if not self.validate_pmid(citation['pmid']):
                    raise ValidationError(f"Invalid PMID format: {citation['pmid']}")
                    
            if 'doi' in citation and citation['doi']:
                if not self.validate_doi(citation['doi']):
                    raise ValidationError(f"Invalid DOI format: {citation['doi']}")
                    
        return processed
        
    def _fix_uuids(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing or invalid UUIDs in the data."""
        processed = data.copy()
        
        # Fix ingredient UUID
        if 'ingredient' in processed:
            if 'id' not in processed['ingredient']:
                processed['ingredient']['id'] = str(uuid4())
                
        # Fix effect UUIDs and link to ingredient
        ingredient_id = processed.get('ingredient', {}).get('id')
        
        for effect_type in ['microbiome_effects', 'metabolic_effects', 'symptom_effects']:
            if effect_type in processed:
                for effect in processed[effect_type]:
                    if 'id' not in effect:
                        effect['id'] = str(uuid4())
                    if 'ingredient_id' not in effect:
                        effect['ingredient_id'] = ingredient_id
                        
        # Fix citation UUIDs
        if 'citations' in processed:
            for citation in processed['citations']:
                if 'id' not in citation:
                    citation['id'] = str(uuid4())
                    
        # Fix interaction UUIDs
        if 'interactions' in processed:
            for interaction in processed['interactions']:
                if 'id' not in interaction:
                    interaction['id'] = str(uuid4())
                    
        return processed
        
    def calculate_derived_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived fields like effect counts and confidence averages."""
        processed = data.copy()
        
        # Count effects
        effect_counts = {}
        for effect_type in ['microbiome_effects', 'metabolic_effects', 'symptom_effects']:
            effect_counts[effect_type] = len(processed.get(effect_type, []))
            
        # Calculate average confidence
        confidences = []
        for effect_type in ['microbiome_effects', 'metabolic_effects', 'symptom_effects']:
            for effect in processed.get(effect_type, []):
                if 'confidence' in effect and effect['confidence'] is not None:
                    confidences.append(effect['confidence'])
                    
        if confidences:
            avg_confidence = round(sum(confidences) / len(confidences), 2)
            if 'ingredient' in processed:
                if 'confidence_score' not in processed['ingredient']:
                    processed['ingredient']['confidence_score'] = avg_confidence
                    
        return processed
        
    def validate_json_file(self, filepath: Path) -> Tuple[bool, List[str], Optional[CompleteIngredientModel]]:
        """
        Validate JSON file against Pydantic models.
        
        Returns:
            Tuple of (is_valid, errors, parsed_model)
        """
        errors = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {e}")
            return False, errors, None
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return False, errors, None
            
        try:
            # Process the data
            processed_data = self.process_ingredient_data(data)
            processed_data = self.calculate_derived_fields(processed_data)
            
            # Validate against Pydantic model
            ingredient_model = CompleteIngredientModel(**processed_data)
            
            return True, [], ingredient_model
            
        except PydanticValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(loc) for loc in error['loc'])
                errors.append(f"Field '{field_path}': {error['msg']}")
            return False, errors, None
        except ValidationError as e:
            errors.append(str(e))
            return False, errors, None
        except Exception as e:
            errors.append(f"Unexpected validation error: {e}")
            return False, errors, None
            
    async def import_ingredient_from_json(
        self, 
        filepath: Path, 
        dry_run: bool = False,
        update_existing: bool = False,
        skip_duplicates: bool = False,
        force_import: bool = False
    ) -> Tuple[bool, str, Optional[UUID]]:
        """
        Import ingredient from JSON file.
        
        Returns:
            Tuple of (success, message, ingredient_id)
        """
        # Validate the file first
        is_valid, errors, ingredient_model = self.validate_json_file(filepath)
        
        if not is_valid:
            return False, f"Validation failed: {'; '.join(errors)}", None
            
        if dry_run:
            return True, f"Dry run successful - would import {ingredient_model.ingredient.name}", None
            
        try:
            # Check for existing ingredient
            existing = await self.repository.get_ingredient_by_name(ingredient_model.ingredient.name)
            
            if existing:
                if skip_duplicates:
                    return True, f"Skipped duplicate: {ingredient_model.ingredient.name}", existing.ingredient.id
                elif update_existing:
                    # Update existing ingredient
                    await self.repository.update_ingredient(
                        existing.ingredient.id,
                        ingredient_model.ingredient.dict(exclude={'id', 'created_at', 'updated_at'})
                    )
                    return True, f"Updated existing ingredient: {ingredient_model.ingredient.name}", existing.ingredient.id
                elif not force_import:
                    return False, f"Ingredient already exists: {ingredient_model.ingredient.name}", None
                    
            # Create new ingredient
            ingredient_id = await self.repository.create_ingredient(ingredient_model)
            return True, f"Successfully imported: {ingredient_model.ingredient.name}", ingredient_id
            
        except DuplicateIngredientError as e:
            return False, f"Duplicate ingredient: {e}", None
        except RepositoryValidationError as e:
            return False, f"Validation error: {e}", None
        except DatabaseOperationError as e:
            return False, f"Database error: {e}", None
        except Exception as e:
            return False, f"Unexpected error: {e}", None
            
    async def batch_import_directory(
        self,
        directory_path: Path,
        dry_run: bool = False,
        update_existing: bool = False,
        skip_duplicates: bool = False,
        force_import: bool = False,
        progress_bar: bool = True
    ) -> ImportResult:
        """
        Import all JSON files from a directory.
        
        Returns:
            ImportResult with detailed results
        """
        result = ImportResult()
        
        if not directory_path.exists():
            result.add_failure('directory', f"Directory not found: {directory_path}")
            result.finalize()
            return result
            
        # Find all JSON files
        json_files = list(directory_path.glob('*.json'))
        
        if not json_files:
            result.add_warning('directory', f"No JSON files found in: {directory_path}")
            result.finalize()
            return result
            
        self.logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process files with progress bar
        if progress_bar:
            pbar = tqdm(json_files, desc="Importing ingredients", unit="file")
        else:
            pbar = json_files
            
        for filepath in pbar:
            try:
                success, message, ingredient_id = await self.import_ingredient_from_json(
                    filepath,
                    dry_run=dry_run,
                    update_existing=update_existing,
                    skip_duplicates=skip_duplicates,
                    force_import=force_import
                )
                
                if success:
                    if "Skipped" in message:
                        result.add_skip(filepath.name, message)
                    else:
                        result.add_success(ingredient_id, filepath.name)
                        
                    if progress_bar and hasattr(pbar, 'set_postfix'):
                        pbar.set_postfix({
                            'Success': result.success_count,
                            'Failed': result.failure_count,
                            'Skipped': result.skipped_count
                        })
                        
                else:
                    result.add_failure(filepath.name, message)
                    
            except Exception as e:
                result.add_failure(filepath.name, f"Unexpected error: {e}")
                
        result.finalize()
        return result
        
    async def validate_directory(self, directory_path: Path, verbose: bool = False) -> ImportResult:
        """
        Validate all JSON files in a directory without importing.
        
        Returns:
            ImportResult with validation results
        """
        result = ImportResult()
        
        if not directory_path.exists():
            result.add_failure('directory', f"Directory not found: {directory_path}")
            result.finalize()
            return result
            
        json_files = list(directory_path.glob('*.json'))
        
        if not json_files:
            result.add_warning('directory', f"No JSON files found in: {directory_path}")
            result.finalize()
            return result
            
        self.logger.info(f"Validating {len(json_files)} JSON files")
        
        for filepath in tqdm(json_files, desc="Validating files", unit="file"):
            try:
                is_valid, errors, ingredient_model = self.validate_json_file(filepath)
                
                if is_valid:
                    result.add_success(ingredient_model.ingredient.id, filepath.name)
                    if verbose:
                        self.logger.info(f"✓ Valid: {filepath.name}")
                else:
                    result.add_failure(filepath.name, '; '.join(errors))
                    if verbose:
                        self.logger.error(f"✗ Invalid: {filepath.name}")
                        for error in errors:
                            self.logger.error(f"  - {error}")
                            
            except Exception as e:
                result.add_failure(filepath.name, f"Validation error: {e}")
                if verbose:
                    self.logger.error(f"✗ Error: {filepath.name} - {e}")
                    
        result.finalize()
        return result


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/import.log')
        ]
    )
    return logging.getLogger(__name__)


def print_results(result: ImportResult, verbose: bool = False):
    """Print import results summary."""
    print(f"\n{'='*60}")
    print(f"IMPORT RESULTS SUMMARY")
    print(f"{'='*60}")
    
    summary = result.summary()
    print(f"Total files processed: {summary['total_processed']}")
    print(f"Successful imports: {summary['successful']}")
    print(f"Failed imports: {summary['failed']}")
    print(f"Skipped imports: {summary['skipped']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ✗ {error['filename']}: {error['error']}")
            
    if result.warnings:
        print(f"\nWARNINGS ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  ⚠ {warning['filename']}: {warning.get('reason', warning.get('message', 'Unknown'))}")
            
    if verbose and result.imported_ids:
        print(f"\nIMPORTED IDs:")
        for ingredient_id in result.imported_ids:
            print(f"  - {ingredient_id}")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GutIntel Ingredient Data Importer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import single file with dry run
  python tools/data_importer.py single --file "inulin.json" --dry-run
  
  # Import directory with update mode
  python tools/data_importer.py batch --directory "./ingredients/" --update-existing
  
  # Validate single file with verbose output
  python tools/data_importer.py validate --file "inulin.json" --verbose
  
  # Batch import with force override
  python tools/data_importer.py batch --directory "./ingredients/" --force-import
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single file import
    single_parser = subparsers.add_parser('single', help='Import single JSON file')
    single_parser.add_argument('--file', required=True, help='JSON file path')
    single_parser.add_argument('--dry-run', action='store_true', help='Validate only, do not import')
    single_parser.add_argument('--update-existing', action='store_true', help='Update existing ingredients')
    single_parser.add_argument('--skip-duplicates', action='store_true', help='Skip existing ingredients')
    single_parser.add_argument('--force-import', action='store_true', help='Force import (overwrite existing)')
    
    # Batch directory import
    batch_parser = subparsers.add_parser('batch', help='Import directory of JSON files')
    batch_parser.add_argument('--directory', required=True, help='Directory containing JSON files')
    batch_parser.add_argument('--dry-run', action='store_true', help='Validate only, do not import')
    batch_parser.add_argument('--update-existing', action='store_true', help='Update existing ingredients')
    batch_parser.add_argument('--skip-duplicates', action='store_true', help='Skip existing ingredients')
    batch_parser.add_argument('--force-import', action='store_true', help='Force import (overwrite existing)')
    batch_parser.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    
    # Validation only
    validate_parser = subparsers.add_parser('validate', help='Validate JSON files without importing')
    validate_parser.add_argument('--file', help='Single JSON file to validate')
    validate_parser.add_argument('--directory', help='Directory to validate')
    validate_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Global options
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log file path (default: logs/import.log)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Setup logging
    logger = setup_logging(args.verbose)
    
    try:
        # Initialize database and repository
        db = await get_database()
        repository = await create_ingredient_repository(db)
        importer = DataImporter(repository, logger)
        
        # Execute command
        if args.command == 'single':
            filepath = Path(args.file)
            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return 1
                
            success, message, ingredient_id = await importer.import_ingredient_from_json(
                filepath,
                dry_run=args.dry_run,
                update_existing=args.update_existing,
                skip_duplicates=args.skip_duplicates,
                force_import=args.force_import
            )
            
            if success:
                logger.info(f"SUCCESS: {message}")
                if ingredient_id:
                    logger.info(f"Ingredient ID: {ingredient_id}")
                return 0
            else:
                logger.error(f"FAILED: {message}")
                return 1
                
        elif args.command == 'batch':
            directory = Path(args.directory)
            result = await importer.batch_import_directory(
                directory,
                dry_run=args.dry_run,
                update_existing=args.update_existing,
                skip_duplicates=args.skip_duplicates,
                force_import=args.force_import,
                progress_bar=not args.no_progress
            )
            
            print_results(result, args.verbose)
            return 0 if result.failure_count == 0 else 1
            
        elif args.command == 'validate':
            if args.file:
                filepath = Path(args.file)
                if not filepath.exists():
                    logger.error(f"File not found: {filepath}")
                    return 1
                    
                is_valid, errors, ingredient_model = importer.validate_json_file(filepath)
                
                if is_valid:
                    logger.info(f"✓ VALID: {filepath.name}")
                    if args.verbose and ingredient_model:
                        logger.info(f"  Name: {ingredient_model.ingredient.name}")
                        logger.info(f"  Category: {ingredient_model.ingredient.category}")
                        logger.info(f"  Effects: {ingredient_model.total_effects_count}")
                    return 0
                else:
                    logger.error(f"✗ INVALID: {filepath.name}")
                    for error in errors:
                        logger.error(f"  - {error}")
                    return 1
                    
            elif args.directory:
                directory = Path(args.directory)
                result = await importer.validate_directory(directory, args.verbose)
                print_results(result, args.verbose)
                return 0 if result.failure_count == 0 else 1
                
            else:
                logger.error("Either --file or --directory must be specified for validation")
                return 1
                
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        # Clean up database connections
        if 'db' in locals():
            await db.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))