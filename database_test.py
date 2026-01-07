import sqlite3

conn = sqlite3.connect('parts.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL
    )
''')

cursor.execute('''
    INSERT INTO parts (name, category, price)
    VALUES (?, ?, ?)
''', ('NVIDIA RTX 4090', 'GPU', 1599.99))

conn.commit()

cursor.execute('SELECT * FROM parts')
parts = cursor.fetchall()

print("Parts in database:")
for part in parts:
    print(f"- {part[1]} ({part[2]}): ${part[3]}")

conn.close()

print("\nDatabase created successfully!")