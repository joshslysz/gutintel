import pandas as pd
import json
import os
import asyncio
from database.connection import Database
from database.repositories import IngredientRepository
from dotenv import load_dotenv
import sys
import uuid

class Top100Importer:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv('DATABASE_URL')
        self.templates_dir = "templates/top_100"
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def convert_csv_to_json_templates(self, csv_file):
        """Convert the AI-generated CSV to JSON templates"""
        print(f"🔍 Reading CSV file: {csv_file}")
        
        try:
            # Read CSV with proper handling
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f"📊 Found {len(df)} rows in CSV")
            
            # Clean the data - remove any empty rows
            df = df.dropna(subset=['name'])  
            df = df[df['name'].str.strip() != '']  
            
            print(f"✅ Processing {len(df)} valid ingredients")
            
            created_files = []
            
            for index, row in df.iterrows():
                try:
                    ingredient_data = self.create_ingredient_json(row)
                    filename = self.save_json_template(ingredient_data, row['name'])
                    created_files.append(filename)
                    print(f"✅ Created: {filename}")
                except Exception as e:
                    print(f"❌ Error processing {row.get('name', 'unknown')}: {e}")
            
            print(f"\n🎉 Successfully created {len(created_files)} JSON templates!")
            return created_files
            
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return []
    
    def create_ingredient_json(self, row):
        """Convert a CSV row to JSON ingredient format"""
        
        # Basic ingredient info
        ingredient_data = {
            "ingredient": {
                "name": str(row['name']).strip(),
                "slug": self.create_slug(str(row['name'])),
                "category": self.clean_category(row.get('category', 'other')),
                "description": str(row.get('description', f"{row['name']} - gut health ingredient")).strip(),
                "gut_score": self.safe_float(row.get('gut_score'), 5.0),
                "confidence_score": self.safe_float(row.get('confidence_score'), 0.5),
                "aliases": self.parse_aliases(row.get('aliases', '')),
                "dosage_info": {
                    "min_dose": str(row.get('dosage_min', 'TBD')).strip(),
                    "max_dose": str(row.get('dosage_max', 'TBD')).strip(),
                    "unit": str(row.get('dosage_unit', 'mg')).strip(),
                    "frequency": str(row.get('dosage_frequency', 'daily')).strip()
                }
            },
            "microbiome_effects": [],
            "metabolic_effects": [],
            "symptom_effects": [],
            "citations": []
        }
        
        # Add microbiome effects (bacteria_1, bacteria_2)
        for i in range(1, 3):
            bacteria_col = f'bacteria_{i}'
            effect_col = f'bacteria_effect_{i}'
            strength_col = f'bacteria_strength_{i}'
            mechanism_col = f'bacteria_mechanism_{i}'
            
            if pd.notna(row.get(bacteria_col)) and str(row.get(bacteria_col)).strip():
                ingredient_data["microbiome_effects"].append({
                    "bacteria_name": str(row[bacteria_col]).strip(),
                    "bacteria_level": "genus",
                    "effect_type": self.clean_effect_type(row.get(effect_col, "promotes_growth")),
                    "effect_strength": self.clean_strength(row.get(strength_col, "moderate")),
                    "confidence": 0.7,
                    "mechanism": str(row.get(mechanism_col, "")).strip()
                })
        
        # Add metabolic effects
        if pd.notna(row.get('metabolic_effect_1')) and str(row.get('metabolic_effect_1')).strip():
            ingredient_data["metabolic_effects"].append({
                "effect_name": str(row['metabolic_effect_1']).strip(),
                "effect_category": "metabolism",
                "impact_direction": "positive",
                "effect_strength": "moderate",
                "confidence": 0.7,
                "mechanism": str(row.get('metabolic_mechanism_1', "")).strip()
            })
        
        # Add symptom effects
        if pd.notna(row.get('symptom_effect_1')) and str(row.get('symptom_effect_1')).strip():
            ingredient_data["symptom_effects"].append({
                "symptom_name": str(row['symptom_effect_1']).strip(),
                "impact_direction": self.clean_direction(row.get('symptom_direction_1', "positive")),
                "effect_strength": "moderate",
                "confidence": 0.7,
                "population_notes": str(row.get('symptom_notes_1', "")).strip()
            })
        
        # Add citations
        if pd.notna(row.get('citation_1_pmid')) and str(row.get('citation_1_pmid')).strip():
            ingredient_data["citations"].append({
                "pmid": str(row['citation_1_pmid']).strip(),
                "title": str(row.get('citation_1_title', "")).strip(),
                "authors": "Research Team",
                "journal": str(row.get('citation_1_journal', "")).strip(),
                "publication_year": self.safe_int(row.get('citation_1_year'), 2023),
                "study_type": "clinical"
            })
        
        return ingredient_data
    
    def create_slug(self, name):
        """Create URL-friendly slug from name"""
        return name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '').replace(',', '')
    
    def clean_category(self, category):
        """Ensure category is valid"""
        valid_categories = ['prebiotic', 'probiotic', 'fiber', 'herb', 'mineral', 'vitamin', 'polyphenol', 'fatty_acid', 'other']
        category = str(category).lower().strip()
        return category if category in valid_categories else 'other'
    
    def clean_effect_type(self, effect):
        """Clean effect type"""
        effect = str(effect).lower().strip()
        if 'promotes' in effect or 'growth' in effect:
            return 'promotes_growth'
        elif 'inhibits' in effect:
            return 'inhibits_growth'
        else:
            return 'modulates_activity'
    
    def clean_strength(self, strength):
        """Clean strength values"""
        strength = str(strength).lower().strip()
        if strength in ['weak', 'moderate', 'strong']:
            return strength
        return 'moderate'
    
    def clean_direction(self, direction):
        """Clean direction values"""
        direction = str(direction).lower().strip()
        return 'positive' if 'positive' in direction else 'negative'
    
    def safe_float(self, value, default):
        """Safely convert to float"""
        try:
            return float(value) if pd.notna(value) else default
        except (ValueError, TypeError):
            return default
    
    def safe_int(self, value, default):
        """Safely convert to int"""
        try:
            return int(value) if pd.notna(value) else default
        except (ValueError, TypeError):
            return default
    
    def parse_aliases(self, aliases_str):
        """Parse aliases from string"""
        if pd.isna(aliases_str) or not str(aliases_str).strip():
            return []
        return [alias.strip() for alias in str(aliases_str).split(';') if alias.strip()]
    
    def save_json_template(self, ingredient_data, name):
        """Save ingredient data as JSON template"""
        filename = f"{self.templates_dir}/{self.create_slug(name)}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(ingredient_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    async def import_templates_to_database(self, template_files):
        """Import all JSON templates to database"""
        print(f"\n🚀 Starting database import of {len(template_files)} ingredients...")
        
        db = Database(database_url=self.db_url)
        await db.connect()
        
        repo = IngredientRepository(db)
        
        success_count = 0
        error_count = 0
        
        for template_file in template_files:
            try:
                print(f"📤 Importing {os.path.basename(template_file)}...")
                
                # Read JSON template
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Import using existing importer logic
                result = await self.import_single_ingredient(repo, data)
                if result:
                    success_count += 1
                    print(f"✅ Successfully imported {data['ingredient']['name']}")
                else:
                    error_count += 1
                    print(f"❌ Failed to import {data['ingredient']['name']}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error importing {template_file}: {e}")
        
        await db.disconnect()
        
        print(f"\n🎉 Import Complete!")
        print(f"✅ Success: {success_count} ingredients")
        print(f"❌ Errors: {error_count} ingredients")
        
        return success_count, error_count
    
    async def import_single_ingredient(self, repo, data):
        """Import a single ingredient to database"""
        try:
            # Check if ingredient already exists
            existing = await repo.get_ingredient_by_name(data['ingredient']['name'])
            if existing:
                print(f"⚠️  {data['ingredient']['name']} already exists, skipping...")
                return True
            
            # Create the complete ingredient data structure
            from models.ingredient import CompleteIngredientModel
            
            complete_ingredient = CompleteIngredientModel(**data)
            
            # Use repository to create ingredient
            ingredient_id = await repo.bulk_create_ingredients([complete_ingredient])
            
            return True
            
        except Exception as e:
            print(f"❌ Error importing ingredient: {e}")
            return False
    
    async def run_complete_import(self, csv_file):
        """Run the complete CSV to database import process"""
        print("🧬 GUTINTEL TOP 100 IMPORT PROCESS")
        print("=" * 50)
        
        # Step 1: Convert CSV to JSON templates
        print("\n📋 Step 1: Converting CSV to JSON templates...")
        template_files = self.convert_csv_to_json_templates(csv_file)
        
        if not template_files:
            print("❌ No templates created, stopping process")
            return
        
        # Step 2: Import to database
        print(f"\n📤 Step 2: Importing {len(template_files)} ingredients to database...")
        success_count, error_count = await self.import_templates_to_database(template_files)
        
        # Step 3: Verify import
        print(f"\n🔍 Step 3: Verifying database...")
        await self.verify_import()
        
        print(f"\n🎉 IMPORT COMPLETE!")
        print(f"📊 Total processed: {len(template_files)}")
        print(f"✅ Successfully imported: {success_count}")
        print(f"❌ Errors: {error_count}")
    
    async def verify_import(self):
        """Verify the import worked"""
        db = Database(database_url=self.db_url)
        await db.connect()
        
        # Count total ingredients
        total = await db.fetchval('SELECT COUNT(*) FROM ingredients')
        print(f"📊 Total ingredients in database: {total}")
        
        # Show top 5 by gut score
        top_5 = await db.fetch('SELECT name, gut_score FROM ingredients ORDER BY gut_score DESC LIMIT 5')
        print(f"🏆 Top 5 ingredients:")
        for row in top_5:
            print(f"   {row[0]}: {row[1]}/10")
        
        await db.disconnect()

# Main execution
async def main():
    if len(sys.argv) != 2:
        print("Usage: python import_top_100.py <csv_file>")
        print("Example: python import_top_100.py gut_health_ingredients.txt")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        sys.exit(1)
    
    importer = Top100Importer()
    await importer.run_complete_import(csv_file)

if __name__ == "__main__":
    asyncio.run(main())
