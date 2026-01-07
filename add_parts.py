import sqlite3

def add_part():
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    print("=== Add a Computer Part ===")
    name = input("Part name (e.g., AMD Ryzen 9 7950X): ")
    category = input("Category (GPU/CPU/RAM/Storage/etc): ")
    price = float(input("Price: $"))
    
    cursor.execute('''
        INSERT INTO parts (name, category, price)
        VALUES (?, ?, ?)
    ''', (name, category, price))
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Added {name} to database!")

def view_all_parts():
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM parts')
    parts = cursor.fetchall()
    
    print("\n=== All Parts ===")
    for part in parts:
        print(f"ID: {part[0]} | {part[1]} ({part[2]}) - ${part[3]}")
    
    conn.close()

while True:
    print("\n--- Price Tracker Menu ---")
    print("1. Add a part")
    print("2. View all parts")
    print("3. Exit")
    
    choice = input("\nChoose an option: ")
    
    if choice == "1":
        add_part()
    elif choice == "2":
        view_all_parts()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")