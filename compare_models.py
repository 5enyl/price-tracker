import sqlite3

def list_all_base_models():
    """Show all unique base models"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT base_model, COUNT(*) as count
        FROM parts 
        WHERE base_model IS NOT NULL AND base_model != ""
        GROUP BY base_model
    ''')
    
    models = cursor.fetchall()
    conn.close()
    
    return models

def compare_model_variants(base_model):
    """Show all variants of a specific model with prices"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, price, url, last_updated
        FROM parts
        WHERE base_model = ?
        ORDER BY price ASC
    ''', (base_model,))
    
    variants = cursor.fetchall()
    conn.close()
    
    return variants

def find_cheapest_per_model():
    """Find the cheapest variant for each base model"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT base_model, name, MIN(price) as lowest_price
        FROM parts
        WHERE base_model IS NOT NULL 
          AND base_model != ""
          AND price IS NOT NULL
        GROUP BY base_model
        ORDER BY base_model
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def set_base_model(part_id, base_model):
    """Set the base model for a part"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE parts SET base_model = ? WHERE id = ?', (base_model, part_id))
    
    conn.commit()
    conn.close()

def list_parts_without_base_model():
    """Show parts that don't have a base model set"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, category
        FROM parts
        WHERE base_model IS NULL OR base_model = ""
    ''')
    
    parts = cursor.fetchall()
    conn.close()
    
    return parts

# Main menu
def main():
    while True:
        print("\n=== Model Comparison Tool ===")
        print("1. Set base model for parts")
        print("2. View all base models")
        print("3. Compare variants of a model")
        print("4. Find cheapest option per model")
        print("5. Exit")
        
        choice = input("\nChoose option: ")
        
        if choice == "1":
            # Set base model
            parts = list_parts_without_base_model()
            
            if not parts:
                print("\n✓ All parts have base models assigned!")
            else:
                print("\n=== Parts Without Base Model ===\n")
                for part_id, name, category in parts:
                    print(f"ID: {part_id} | {name} ({category})")
                
                print("\n")
                part_id = input("Enter part ID to set base model: ")
                base_model = input("Enter base model (e.g., 'RTX 4090', 'RTX 4080'): ")
                
                set_base_model(part_id, base_model)
                print(f"\n✓ Set base model to '{base_model}'")
        
        elif choice == "2":
            # View all base models
            models = list_all_base_models()
            
            if not models:
                print("\nNo base models set yet!")
            else:
                print("\n=== All Base Models ===\n")
                for model, count in models:
                    print(f"{model}: {count} variant(s)")
        
        elif choice == "3":
            # Compare variants
            models = list_all_base_models()
            
            if not models:
                print("\nNo base models set yet!")
                continue
            
            print("\n=== Available Models ===\n")
            for model, count in models:
                print(f"- {model} ({count} variant(s))")
            
            print("\n")
            base_model = input("Enter base model to compare: ")
            
            variants = compare_model_variants(base_model)
            
            if not variants:
                print(f"\nNo variants found for '{base_model}'")
            else:
                print(f"\n=== All {base_model} Variants ===\n")
                for part_id, name, price, url, last_updated in variants:
                    price_str = f"${price:.2f}" if price else "No price"
                    print(f"{name}")
                    print(f"  Price: {price_str}")
                    print(f"  Last updated: {last_updated if last_updated else 'Never'}")
                    print(f"  URL: {url if url else 'No URL'}")
                    print()
        
        elif choice == "4":
            # Find cheapest per model
            results = find_cheapest_per_model()
            
            if not results:
                print("\nNo models with prices found!")
            else:
                print("\n=== Cheapest Option Per Model ===\n")
                for base_model, name, price in results:
                    print(f"{base_model}: ${price:.2f}")
                    print(f"  → {name}\n")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()