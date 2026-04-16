import sqlite3

def add_base_model_field():
    """Add base_model column to parts table"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # Add base_model column
    try:
        cursor.execute('ALTER TABLE parts ADD COLUMN base_model TEXT')
        print("✓ Added 'base_model' column to parts table")
    except:
        print("ℹ 'base_model' column already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Database updated!")
    print("\nNow you can add a base_model (like 'RTX 4090') to group similar parts.")

if __name__ == '__main__':
    print("=== Adding Base Model Field ===\n")
    add_base_model_field()