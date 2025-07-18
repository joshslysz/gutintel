import pandas as pd
import json
import os
import asyncio
from database.connection import Database
from dotenv import load_dotenv
import sys

class Top100ImporterCorrect:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv('DATABASE_URL')
    
    async def import_csv_directly(self, csv_file):
        """Import CSV directly to database using SQL"""
        print(f"🔍 Reading CSV file: {csv_file}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            df = df.dropna(subset=['name'])
            df = df[df['name'].str.strip() != '']
            
            print(f"✅ Processing {len(df)} valid ingredients")
            
            # Connect to database
            db = Database(database_url=self.db_url)
            await db.connect()
            
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Check if ingredient exists
                    existing = await db.fetchval(
                        'SELECT id FROM ingredients WHERE name = $1', 
                        str(row['name']).strip()
                    )
                    
                    if existing:
                        print(f"⚠️  {row['name']} already exists, skipping...")
                        continue
                    
                    # Insert ingredient
                    ingredient_id = await self.insert_ingredient(db, row)
                    
                    if ingredient_id:
                        # Insert related data
                        await self.insert_microbiome_effects(db, ingredient_id, row)
                        await self.insert_metabolic_effects(db, ingredient_id, row)
                        await self.insert_symptom_effects(db, ingredient_id, row)
                        await self.insert_citations(db, ingredient_id, row)
                        
                        success_count += 1
                        print(f"✅ Successfully imported {row['name']}")
                    else:
                        error_count += 1
                        print(f"❌ Failed to import {row['name']}")
                        
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error importing {row['name']}: {e}")
            
            await db.disconnect()
            
            print(f"\n🎉 Import Complete!")
            print(f"✅ Success: {success_count} ingredients")
            print(f"❌ Errors: {error_count} ingredients")
            
            # Verify import
            await self.verify_import()
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def insert_ingredient(self, db, row):
        """Insert main ingredient record"""
        try:
            # Parse aliases as array
            aliases = []
            if pd.notna(row.get('aliases')):
                aliases = [alias.strip() for alias in str(row['aliases']).split(';') if alias.strip()]
            
            # Create dosage_info JSON
            dosage_info = {
                "min_dose": str(row.get('dosage_min', 'TBD')).strip(),
                "max_dose": str(row.get('dosage_max', 'TBD')).strip(),
                "unit": str(row.get('dosage_unit', 'mg')).strip(),
                "frequency": str(row.get('dosage_frequency', 'daily')).strip()
            }
            
            # Insert ingredient
            ingredient_id = await db.fetchval('''
                INSERT INTO ingredients (
                    name, slug, category, description, gut_score, confidence_score,
                    aliases, dosage_info, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                RETURNING id
            ''',
                str(row['name']).strip(),
                self.create_slug(str(row['name'])),
                self.clean_category(row.get('category', 'other')),
                str(row.get('description', f"{row['name']} - gut health ingredient")).strip(),
                self.safe_float(row.get('gut_score'), 5.0),
                self.safe_float(row.get('confidence_score'), 0.5),
                aliases,
                json.dumps(dosage_info)
            )
            
            return ingredient_id
            
        except Exception as e:
            print(f"❌ Error inserting ingredient: {e}")
            return None
    
    async def insert_microbiome_effects(self, db, ingredient_id, row):
        """Insert microbiome effects"""
        try:
            # Insert bacteria_1 effect
            if pd.notna(row.get('bacteria_1')) and str(row.get('bacteria_1')).strip():
                await db.execute('''
                    INSERT INTO microbiome_effects (
                        ingredient_id, bacteria_name, bacteria_level, effect_type, 
                        effect_strength, confidence, mechanism, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ''',
                    ingredient_id,
                    str(row['bacteria_1']).strip(),
                    self.clean_bacteria_level(row.get('bacteria_effect_1', 'modulate')),
                    self.clean_effect_type(row.get('bacteria_effect_1', 'promotes_growth')),
                    self.clean_strength(row.get('bacteria_strength_1', 'moderate')),
                    0.7,
                    str(row.get('bacteria_mechanism_1', '')).strip()
                )
            
            # Insert bacteria_2 effect
            if pd.notna(row.get('bacteria_2')) and str(row.get('bacteria_2')).strip():
                await db.execute('''
                    INSERT INTO microbiome_effects (
                        ingredient_id, bacteria_name, bacteria_level, effect_type, 
                        effect_strength, confidence, mechanism, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ''',
                    ingredient_id,
                    str(row['bacteria_2']).strip(),
                    self.clean_bacteria_level(row.get('bacteria_effect_2', 'modulate')),
                    self.clean_effect_type(row.get('bacteria_effect_2', 'promotes_growth')),
                    self.clean_strength(row.get('bacteria_strength_2', 'moderate')),
                    0.7,
                    str(row.get('bacteria_mechanism_2', '')).strip()
                )
                
        except Exception as e:
            print(f"❌ Error inserting microbiome effects: {e}")
    
    async def insert_metabolic_effects(self, db, ingredient_id, row):
        """Insert metabolic effects"""
        try:
            if pd.notna(row.get('metabolic_effect_1')) and str(row.get('metabolic_effect_1')).strip():
                await db.execute('''
                    INSERT INTO metabolic_effects (
                        ingredient_id, effect_name, effect_category, impact_direction,
                        effect_strength, confidence, mechanism, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ''',
                    ingredient_id,
                    str(row['metabolic_effect_1']).strip(),
                    'metabolism',
                    'positive',
                    'moderate',
                    0.7,
                    str(row.get('metabolic_mechanism_1', '')).strip()
                )
                
        except Exception as e:
            print(f"❌ Error inserting metabolic effects: {e}")
    
    async def insert_symptom_effects(self, db, ingredient_id, row):
        """Insert symptom effects - FIXED COLUMN NAMES"""
        try:
            if pd.notna(row.get('symptom_effect_1')) and str(row.get('symptom_effect_1')).strip():
                await db.execute('''
                    INSERT INTO symptom_effects (
                        ingredient_id, symptom_name, symptom_category, effect_direction,
                        effect_strength, confidence, population_notes, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ''',
                    ingredient_id,
                    str(row['symptom_effect_1']).strip(),
                    'digestive',  # Default symptom category
                    self.clean_direction(row.get('symptom_direction_1', 'positive')),
                    'moderate',
                    0.7,
                    str(row.get('symptom_notes_1', '')).strip()
                )
                
        except Exception as e:
            print(f"❌ Error inserting symptom effects: {e}")
    
    async def insert_citations(self, db, ingredient_id, row):
        """Insert citations"""
        try:
            if pd.notna(row.get('citation_1_pmid')) and str(row.get('citation_1_pmid')).strip():
                await db.execute('''
                    INSERT INTO citations (
                        pmid, title, authors, journal, publication_year, study_type,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                    ON CONFLICT (pmid) DO NOTHING
                ''',
                    str(row['citation_1_pmid']).strip(),
                    str(row.get('citation_1_title', '')).strip(),
                    'Research Team',
                    str(row.get('citation_1_journal', '')).strip(),
                    self.safe_int(row.get('citation_1_year'), 2023),
                    'observational'
                )
                
        except Exception as e:
            print(f"❌ Error inserting citations: {e}")
    
    def create_slug(self, name):
        """Create URL-friendly slug"""
        return name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '').replace(',', '')
    
    def clean_category(self, category):
        """Clean category"""
        valid_categories = ['prebiotic', 'probiotic', 'fiber', 'herb', 'mineral', 'vitamin', 'polyphenol', 'fatty_acid', 'other']
        category = str(category).lower().strip()
        return category if category in valid_categories else 'other'
    
    def clean_bacteria_level(self, effect):
        """Clean bacteria level for enum"""
        effect = str(effect).lower().strip()
        if 'promotes' in effect or 'growth' in effect:
            return 'increase'
        elif 'inhibits' in effect:
            return 'decrease'
        else:
            return 'modulate'
    
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
        """Clean strength"""
        strength = str(strength).lower().strip()
        if strength in ['weak', 'moderate', 'strong']:
            return strength
        return 'moderate'
    
    def clean_direction(self, direction):
        """Clean direction"""
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
    
    async def verify_import(self):
        """Verify the import worked"""
        db = Database(database_url=self.db_url)
        await db.connect()
        
        # Count total ingredients
        total = await db.fetchval('SELECT COUNT(*) FROM ingredients')
        print(f"\n📊 Total ingredients in database: {total}")
        
        # Show top 5 by gut score
        top_5 = await db.fetch('SELECT name, gut_score FROM ingredients ORDER BY gut_score DESC LIMIT 5')
        print(f"🏆 Top 5 ingredients:")
        for row in top_5:
            print(f"   {row[0]}: {row[1]}/10")
        
        # Count effects
        microbiome_count = await db.fetchval('SELECT COUNT(*) FROM microbiome_effects')
        metabolic_count = await db.fetchval('SELECT COUNT(*) FROM metabolic_effects')
        symptom_count = await db.fetchval('SELECT COUNT(*) FROM symptom_effects')
        citation_count = await db.fetchval('SELECT COUNT(*) FROM citations')
        
        print(f"🦠 Microbiome effects: {microbiome_count}")
        print(f"⚡ Metabolic effects: {metabolic_count}")
        print(f"🩺 Symptom effects: {symptom_count}")
        print(f"📚 Citations: {citation_count}")
        
        await db.disconnect()

# Main execution
async def main():
    if len(sys.argv) != 2:
        print("Usage: python import_top_100_correct.py <csv_file>")
        print("Example: python import_top_100_correct.py gut_health_ingredients.txt")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        sys.exit(1)
    
    print("🧬 GUTINTEL TOP 85 IMPORT (CORRECTED)")
    print("=" * 50)
    
    importer = Top100ImporterCorrect()
    await importer.import_csv_directly(csv_file)

if __name__ == "__main__":
    asyncio.run(main())
