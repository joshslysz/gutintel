import asyncio
import json
import os
from database.connection import Database
from dotenv import load_dotenv

class DataEntryMenu:
    def __init__(self):
        load_dotenv()
        self.db_url = os.getenv('DATABASE_URL')
    
    def main_menu(self):
        print("\n" + "="*50)
        print("🧬 GUTINTEL DATA ENTRY MENU")
        print("="*50)
        
        print("\n📝 ADD NEW INGREDIENTS:")
        print("1.  Quick add (name, score, category only)")
        print("2.  Generate template for detailed ingredient")
        print("3.  Edit existing template")
        print("4.  Import from JSON file")
        
        print("\n📊 BATCH OPERATIONS:")
        print("5.  Generate multiple templates")
        print("6.  Import multiple files")
        print("7.  Validate files before import")
        
        print("\n🔍 UTILITIES:")
        print("8.  List available templates")
        print("9.  Show recent additions")
        print("10. Check if ingredient exists")
        
        print("\n0.  Exit")
        
        choice = input(f"\nEnter choice (0-10): ")
        self.handle_choice(choice)
    
    def handle_choice(self, choice):
        if choice == '1':
            self.quick_add()
        elif choice == '2':
            self.generate_template()
        elif choice == '3':
            self.edit_template()
        elif choice == '4':
            self.import_json()
        elif choice == '5':
            self.generate_multiple()
        elif choice == '6':
            self.import_multiple()
        elif choice == '7':
            self.validate_files()
        elif choice == '8':
            self.list_templates()
        elif choice == '9':
            self.show_recent()
        elif choice == '10':
            self.check_exists()
        elif choice == '0':
            print("\n👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice")
        
        input("\n👆 Press Enter to continue...")
        self.main_menu()
    
    def quick_add(self):
        print("\n🚀 QUICK ADD INGREDIENT")
        print("(Creates basic ingredient - you can add details later)")
        print("-" * 40)
        
        name = input("Ingredient name: ").strip()
        if not name:
            print("❌ Name required")
            return
        
        # Check if exists
        if asyncio.run(self.ingredient_exists(name)):
            print(f"⚠️ Ingredient '{name}' already exists!")
            return
        
        print("\nCategories: prebiotic, probiotic, fiber, herb, mineral, vitamin, other")
        category = input("Category: ").strip().lower()
        if category not in ['prebiotic', 'probiotic', 'fiber', 'herb', 'mineral', 'vitamin', 'other']:
            print("❌ Invalid category")
            return
        
        try:
            gut_score = float(input("Gut score (0-10): "))
            if not 0 <= gut_score <= 10:
                print("❌ Gut score must be 0-10")
                return
        except ValueError:
            print("❌ Invalid gut score")
            return
        
        try:
            confidence = float(input("Confidence (0-1): "))
            if not 0 <= confidence <= 1:
                print("❌ Confidence must be 0-1")
                return
        except ValueError:
            print("❌ Invalid confidence")
            return
        
        description = input("Brief description (optional): ").strip()
        
        # Create basic JSON
        data = {
            "ingredient": {
                "name": name,
                "slug": name.lower().replace(' ', '-'),
                "category": category,
                "description": description or f"{name} - gut health ingredient",
                "gut_score": gut_score,
                "confidence_score": confidence,
                "dosage_info": {
                    "min_dose": "TBD",
                    "max_dose": "TBD", 
                    "unit": "mg",
                    "frequency": "daily"
                }
            },
            "microbiome_effects": [],
            "metabolic_effects": [],
            "symptom_effects": [],
            "citations": []
        }
        
        # Save template
        filename = f"templates/{name.lower().replace(' ', '_')}.json"
        os.makedirs("templates", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Created template: {filename}")
        
        # Ask if want to import now
        import_now = input("Import to database now? (y/n): ").strip().lower()
        if import_now == 'y':
            self.import_file(filename)
    
    def generate_template(self):
        print("\n📝 GENERATE DETAILED TEMPLATE")
        print("-" * 40)
        
        name = input("Ingredient name: ").strip()
        if not name:
            print("❌ Name required")
            return
        
        print("\nCategories: prebiotic, probiotic, fiber, herb, mineral, vitamin, other")
        category = input("Category: ").strip().lower()
        if category not in ['prebiotic', 'probiotic', 'fiber', 'herb', 'mineral', 'vitamin', 'other']:
            category = 'other'
        
        # Use your existing template generator
        try:
            os.system(f'python tools/template_generator.py generate --name "{name}" --category "{category}"')
            print(f"✅ Template generated for {name}")
            print(f"📝 Edit: templates/{name.lower().replace(' ', '-')}.json")
            print("💡 Tip: Fill in gut_score, effects, and citations before importing")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def edit_template(self):
        print("\n✏️ EDIT TEMPLATE")
        print("-" * 40)
        
        # List available templates
        templates = self.get_templates()
        if not templates:
            print("❌ No templates found in templates/ directory")
            return
        
        print("Available templates:")
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
        
        try:
            choice = int(input(f"\nSelect template (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                filename = f"templates/{templates[choice-1]}"
                print(f"📝 Opening {filename} in VS Code...")
                os.system(f"code {filename}")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
    
    def import_json(self):
        print("\n📤 IMPORT JSON FILE")
        print("-" * 40)
        
        # List available files
        templates = self.get_templates()
        if not templates:
            print("❌ No JSON files found in templates/ directory")
            return
        
        print("Available files:")
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
        
        try:
            choice = int(input(f"\nSelect file to import (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                filename = f"templates/{templates[choice-1]}"
                
                # Validate first
                print("🔍 Validating file...")
                result = os.system(f"./gutintel-import validate --file {filename}")
                if result == 0:
                    print("✅ File is valid")
                    
                    # Ask for dry run
                    dry_run = input("Do dry run first? (y/n): ").strip().lower()
                    if dry_run == 'y':
                        os.system(f"./gutintel-import single --file {filename} --dry-run")
                        proceed = input("Proceed with actual import? (y/n): ").strip().lower()
                        if proceed != 'y':
                            return
                    
                    # Actual import
                    print("📤 Importing...")
                    result = os.system(f"./gutintel-import single --file {filename}")
                    if result == 0:
                        print("✅ Import successful!")
                    else:
                        print("❌ Import failed")
                else:
                    print("❌ File validation failed")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
    
    def generate_multiple(self):
        print("\n📝 GENERATE MULTIPLE TEMPLATES")
        print("-" * 40)
        
        ingredients = input("Enter ingredient names (comma-separated): ").strip()
        if not ingredients:
            print("❌ No ingredients provided")
            return
        
        print("\nCategories: prebiotic, probiotic, fiber, herb, mineral, vitamin, other")
        category = input("Default category (or leave blank for 'other'): ").strip().lower()
        if category not in ['prebiotic', 'probiotic', 'fiber', 'herb', 'mineral', 'vitamin', 'other']:
            category = 'other'
        
        ingredient_list = [ing.strip() for ing in ingredients.split(',')]
        
        for ingredient in ingredient_list:
            if ingredient:
                try:
                    os.system(f'python tools/template_generator.py generate --name "{ingredient}" --category "{category}"')
                    print(f"✅ Generated template for {ingredient}")
                except Exception as e:
                    print(f"❌ Failed for {ingredient}: {e}")
        
        print(f"\n🎉 Generated {len(ingredient_list)} templates!")
        print("💡 Edit each template before importing")
    
    def import_multiple(self):
        print("\n📤 BATCH IMPORT")
        print("-" * 40)
        
        # Validate all files first
        print("🔍 Validating all templates...")
        result = os.system("./gutintel-import batch --directory templates/ --dry-run")
        
        if result == 0:
            proceed = input("All files valid. Proceed with import? (y/n): ").strip().lower()
            if proceed == 'y':
                print("📤 Importing all files...")
                os.system("./gutintel-import batch --directory templates/")
            else:
                print("❌ Import cancelled")
        else:
            print("❌ Some files have validation errors. Fix them first.")
    
    def validate_files(self):
        print("\n🔍 VALIDATE FILES")
        print("-" * 40)
        
        templates = self.get_templates()
        if not templates:
            print("❌ No templates found")
            return
        
        for template in templates:
            filename = f"templates/{template}"
            print(f"Checking {template}...")
            os.system(f"./gutintel-import validate --file {filename}")
    
    def list_templates(self):
        print("\n📋 AVAILABLE TEMPLATES")
        print("-" * 40)
        
        templates = self.get_templates()
        if not templates:
            print("❌ No templates found in templates/ directory")
            return
        
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
        
        print(f"\n📊 Total: {len(templates)} templates")
    
    async def show_recent(self):
        print("\n📅 RECENT ADDITIONS")
        print("-" * 40)
        
        db = Database(database_url=self.db_url)
        await db.connect()
        
        rows = await db.fetch('SELECT name, gut_score, created_at FROM ingredients ORDER BY created_at DESC LIMIT 10')
        
        if rows:
            for row in rows:
                print(f"  {row[0]:20} {row[1]}/10 (added: {row[2].strftime('%Y-%m-%d')})")
        else:
            print("  No ingredients found")
        
        await db.disconnect()
    
    async def ingredient_exists(self, name):
        db = Database(database_url=self.db_url)
        await db.connect()
        
        result = await db.fetchval('SELECT COUNT(*) FROM ingredients WHERE name ILIKE %s', f'%{name}%')
        
        await db.disconnect()
        return result > 0
    
    def check_exists(self):
        print("\n🔍 CHECK IF INGREDIENT EXISTS")
        print("-" * 40)
        
        name = input("Ingredient name to check: ").strip()
        if not name:
            print("❌ Name required")
            return
        
        exists = asyncio.run(self.ingredient_exists(name))
        if exists:
            print(f"✅ '{name}' already exists in database")
        else:
            print(f"❌ '{name}' not found in database")
    
    def get_templates(self):
        if not os.path.exists("templates"):
            return []
        return [f for f in os.listdir("templates") if f.endswith('.json')]
    
    def import_file(self, filename):
        try:
            result = os.system(f"./gutintel-import single --file {filename}")
            if result == 0:
                print("✅ Import successful!")
            else:
                print("❌ Import failed")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    menu = DataEntryMenu()
    menu.main_menu()
