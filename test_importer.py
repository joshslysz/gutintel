#!/usr/bin/env python3
"""
Simple test script for the data importer
"""

import asyncio
import logging
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from tools.data_importer import DataImporter
from database.repositories import create_ingredient_repository


async def test_validation():
    """Test validation functionality."""
    print("Testing validation...")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create repository and importer
    repository = await create_ingredient_repository()
    importer = DataImporter(repository, logger)
    
    # Test validation
    test_file = Path("ingredients/inulin.json")
    
    if test_file.exists():
        print(f"Validating {test_file}...")
        is_valid, errors, ingredient_model = importer.validate_json_file(test_file)
        
        if is_valid:
            print("✓ Validation successful!")
            print(f"  Name: {ingredient_model.ingredient.name}")
            print(f"  Category: {ingredient_model.ingredient.category}")
            print(f"  Effects: {ingredient_model.total_effects_count}")
            print(f"  Confidence: {ingredient_model.average_confidence}")
        else:
            print("✗ Validation failed!")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"Test file {test_file} not found")
        
    print("Test completed.")


if __name__ == '__main__':
    asyncio.run(test_validation())