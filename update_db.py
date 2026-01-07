import sqlite3

def update_db():
    """Add price history tracking to the database"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # create a new table for price history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_id INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            FOREIGN KEY (part_id) REFERENCES parts (id)
        )
    ''')
    
    # Add url column to part table if it does not exist 
    try:
        cursor.execute('ALTER TABLE parts ADD COLUMN url TEXT')
        print("✓ Added 'url' column to parts table")
    except:
        print("ℹ 'url' column already exists")
    
    # add last_updated column
    try:
        cursor.execute('ALTER TABLE parts ADD COLUMN last_updated DATETIME')
        print("✓ Added 'last_updated' column to parts table")
    except:
        print("ℹ 'last_updated' column already exists")
    
    conn.commit()
    
    # copy existing prices to price_history
    cursor.execute('SELECT id, price FROM parts WHERE price IS NOT NULL')
    existing_parts = cursor.fetchall()
    
    for part_id, price in existing_parts:
        # check if there is price_history entry
        cursor.execute('SELECT COUNT(*) FROM price_history WHERE part_id = ?', (part_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute('''
                INSERT INTO price_history (part_id, price, source)
                VALUES (?, ?, ?)
            ''', (part_id, price, 'Initial price'))
            print(f"✓ Added initial price history for part ID {part_id}")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Database updated successfully!")
    print("\nYou now have:")
    print("  - parts table (stores current info)")
    print("  - price_history table (stores all price changes)")

if __name__ == '__main__':
    print("=== Updating Database Structure ===\n")
    update_db()