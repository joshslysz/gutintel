import asyncio
from database.connection import Database
from dotenv import load_dotenv
import os

async def run_query(query, description):
    print(f"\n{description}")
    print("-" * 50)
    load_dotenv()
    db = Database(database_url=os.getenv('DATABASE_URL'))
    await db.connect()
    
    try:
        rows = await db.fetch(query)
        
        if not rows:
            print("  No results found")
        else:
            for row in rows:
                if len(row) == 3:  # name, score, category
                    print(f"  {row[0]:25} {row[1]}/10 ({row[2]})")
                elif len(row) == 2:  # name, score
                    print(f"  {row[0]:25} {row[1]}")
                elif len(row) == 1:  # single value (like count)
                    print(f"  {row[0]}")
                else:
                    print(f"  {row}")
    except Exception as e:
        print(f"  Error: {e}")
    
    await db.disconnect()

def menu():
    print("\n" + "="*50)
    print("🧬 GUTINTEL DATABASE MENU")
    print("="*50)
    
    # BASIC QUERIES
    print("\n📊 BASIC QUERIES:")
    print("1.  Show all ingredients")
    print("2.  Count total ingredients")
    print("3.  Show top 5 ingredients")
    print("4.  Show bottom 5 ingredients")
    
    # CATEGORY QUERIES  
    print("\n📂 BY CATEGORY:")
    print("5.  Show all prebiotics")
    print("6.  Show all probiotics") 
    print("7.  Show all fibers")
    print("8.  Show category summary")
    
    # SCORE-BASED QUERIES
    print("\n⭐ BY SCORE:")
    print("9.  High score ingredients (≥8.0)")
    print("10. Medium score ingredients (5.0-7.9)")
    print("11. Low score ingredients (<5.0)")
    print("12. Ingredients to avoid (<4.0)")
    
    # BACTERIAL INTELLIGENCE
    print("\n🦠 BACTERIAL INTELLIGENCE:")
    print("13. Show tracked bacteria")
    print("14. Bifidobacterium supporters")
    print("15. Lactobacillus supporters")
    
    # SCIENTIFIC DATA
    print("\n📚 SCIENTIFIC DATA:")
    print("16. Show sample citations")
    print("17. Database overview")
    
    # ADD YOUR OWN QUERIES HERE
    print("\n🔧 CUSTOM QUERIES:")
    print("18. [Add your own query]")
    print("19. [Add your own query]")
    print("20. [Add your own query]")
    
    print("\n0.  Exit")
    
    choice = input(f"\nEnter choice (0-20): ")
    
    # QUERY DEFINITIONS - ADD YOUR OWN HERE!
    queries = {
        # Basic queries
        '1': ('SELECT name, gut_score, category FROM ingredients ORDER BY gut_score DESC', 
              '🧬 All Ingredients (sorted by gut score)'),
        '2': ('SELECT COUNT(*) as total FROM ingredients', 
              '📊 Total Ingredient Count'),
        '3': ('SELECT name, gut_score FROM ingredients ORDER BY gut_score DESC LIMIT 5', 
              '🏆 Top 5 Ingredients'),
        '4': ('SELECT name, gut_score FROM ingredients ORDER BY gut_score ASC LIMIT 5', 
              '📉 Bottom 5 Ingredients'),
        
        # Category queries
        '5': ('SELECT name, gut_score FROM ingredients WHERE category = \'prebiotic\' ORDER BY gut_score DESC', 
              '🌱 Prebiotic Ingredients'),
        '6': ('SELECT name, gut_score FROM ingredients WHERE category = \'probiotic\' ORDER BY gut_score DESC', 
              '🦠 Probiotic Ingredients'),
        '7': ('SELECT name, gut_score FROM ingredients WHERE category = \'fiber\' ORDER BY gut_score DESC', 
              '🌾 Fiber Ingredients'),
        '8': ('SELECT category, COUNT(*) as count, ROUND(AVG(gut_score), 1) as avg_score FROM ingredients GROUP BY category ORDER BY avg_score DESC', 
              '📂 Category Summary'),
        
        # Score-based queries
        '9': ('SELECT name, gut_score FROM ingredients WHERE gut_score >= 8.0 ORDER BY gut_score DESC', 
              '⭐ High Score Ingredients (≥8.0)'),
        '10': ('SELECT name, gut_score FROM ingredients WHERE gut_score >= 5.0 AND gut_score < 8.0 ORDER BY gut_score DESC', 
               '🔶 Medium Score Ingredients (5.0-7.9)'),
        '11': ('SELECT name, gut_score FROM ingredients WHERE gut_score < 5.0 ORDER BY gut_score DESC', 
               '🔻 Low Score Ingredients (<5.0)'),
        '12': ('SELECT name, gut_score FROM ingredients WHERE gut_score < 4.0 ORDER BY gut_score ASC', 
               '⚠️ Ingredients to Avoid (<4.0)'),
        
        # Bacterial intelligence
        '13': ('SELECT DISTINCT bacteria_name, COUNT(*) as ingredient_count FROM microbiome_effects GROUP BY bacteria_name ORDER BY ingredient_count DESC', 
               '🦠 Tracked Bacteria'),
        '14': ('SELECT DISTINCT i.name, i.gut_score FROM ingredients i JOIN microbiome_effects me ON i.id = me.ingredient_id WHERE me.bacteria_name ILIKE \'%bifidobacterium%\' ORDER BY i.gut_score DESC', 
               '🧫 Bifidobacterium Supporters'),
        '15': ('SELECT DISTINCT i.name, i.gut_score FROM ingredients i JOIN microbiome_effects me ON i.id = me.ingredient_id WHERE me.bacteria_name ILIKE \'%lactobacillus%\' ORDER BY i.gut_score DESC', 
               '🧫 Lactobacillus Supporters'),
        
        # Scientific data
        '16': ('SELECT title, journal, publication_year FROM citations LIMIT 5', 
               '📚 Sample Scientific Citations'),
        '17': ('SELECT \'Ingredients\' as type, COUNT(*) as count FROM ingredients UNION SELECT \'Effects\' as type, COUNT(*) as count FROM microbiome_effects UNION SELECT \'Citations\' as type, COUNT(*) as count FROM citations', 
               '📊 Database Overview'),
        
        # YOUR CUSTOM QUERIES - ADD HERE!
        '18': ('SELECT name, gut_score FROM ingredients WHERE name ILIKE \'%fiber%\' ORDER BY gut_score DESC', 
               '🔍 Search for ingredients with "fiber" in name'),
        '19': ('SELECT category, MAX(gut_score) as highest_score FROM ingredients GROUP BY category ORDER BY highest_score DESC', 
               '🏆 Highest score in each category'),
        '20': ('SELECT name, confidence_score FROM ingredients ORDER BY confidence_score DESC LIMIT 10', 
               '🎯 Most confident scores'),
    }
    
    if choice in queries:
        query, description = queries[choice]
        asyncio.run(run_query(query, description))
        input("\n👆 Press Enter to continue...")
        menu()
    elif choice == '0':
        print("\n👋 Thanks for using GutIntel! Goodbye!")
    else:
        print("❌ Invalid choice, try again")
        input("Press Enter to continue...")
        menu()

if __name__ == "__main__":
    menu()
