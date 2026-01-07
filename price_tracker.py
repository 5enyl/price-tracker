import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_newegg_price(url):
    """Scrape price from a Newegg product page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        price_element = soup.find('li', class_='price-current')
        
        if price_element:
            strong_tag = price_element.find('strong')
            sup_tag = price_element.find('sup')
            
            if strong_tag:
                main_price = strong_tag.text.strip().replace(',', '')
                cents = sup_tag.text.strip() if sup_tag else '.00'
                full_price = main_price + cents
                price = float(full_price)
                
                print(f"✓ Found price: ${price}")
                return price
        
        print("✗ Could not find price element")
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def add_new_part(name, category, url):
    """Add a brand new part to track"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # Scrape initial price
    price = scrape_newegg_price(url)
    
    if price is None:
        print("Could not get price. Add manually? (y/n)")
        if input().lower() == 'y':
            price = float(input("Enter price manually: $"))
        else:
            conn.close()
            return
    
    # add to parts table
    cursor.execute('''
        INSERT INTO parts (name, category, price, url, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, category, price, url, datetime.now()))
    
    part_id = cursor.lastrowid
    
    # add to price history
    cursor.execute('''
        INSERT INTO price_history (part_id, price, source)
        VALUES (?, ?, ?)
    ''', (part_id, price, 'Newegg'))
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Added {name} to database at ${price}")

def update_prices():
    """Check all parts and update their prices"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # get any part with a url
    cursor.execute('SELECT id, name, url, price FROM parts WHERE url IS NOT NULL')
    parts = cursor.fetchall()
    
    if not parts:
        print("No parts with URLs to update!")
        conn.close()
        return
    
    print(f"\n=== Updating {len(parts)} parts ===\n")
    
    for part_id, name, url, old_price in parts:
        print(f"Checking: {name}")
        new_price = scrape_newegg_price(url)
        
        if new_price is None:
            print(f"  ⚠ Could not get price, skipping\n")
            continue
        
        # check if price was changed
        if old_price is None or abs(new_price - old_price) > 0.01:
            if old_price:
                change = new_price - old_price
                if change > 0:
                    print(f"  📈 Price increased by ${change:.2f}")
                else:
                    print(f"  📉 Price decreased by ${abs(change):.2f}")
            
            # update parts table
            cursor.execute('''
                UPDATE parts 
                SET price = ?, last_updated = ?
                WHERE id = ?
            ''', (new_price, datetime.now(), part_id))
            
            # Add to price history
            cursor.execute('''
                INSERT INTO price_history (part_id, price, source)
                VALUES (?, ?, ?)
            ''', (part_id, new_price, 'Newegg'))
            
            print(f"  ✓ Updated to ${new_price:.2f}\n")
        else:
            print(f"  → No change (${new_price:.2f})\n")
    
    conn.commit()
    conn.close()
    print("✓ All prices updated!")

def view_price_history(part_id):
    """Show price history for a specific part"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # get part name
    cursor.execute('SELECT name FROM parts WHERE id = ?', (part_id,))
    result = cursor.fetchone()
    
    if not result:
        print("Part not found!")
        conn.close()
        return
    
    name = result[0]
    
    # get price history
    cursor.execute('''
        SELECT price, timestamp, source
        FROM price_history
        WHERE part_id = ?
        ORDER BY timestamp
    ''', (part_id,))
    
    history = cursor.fetchall()
    
    print(f"\n=== Price History for {name} ===\n")
    
    for price, timestamp, source in history:
        print(f"{timestamp} | ${price:.2f} | {source}")
    
    conn.close()

def list_all_parts():
    """Show all tracked parts"""
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, category, price, last_updated FROM parts')
    parts = cursor.fetchall()
    
    print("\n=== All Tracked Parts ===\n")
    
    for part_id, name, category, price, last_updated in parts:
        price_str = f"${price:.2f}" if price else "No price"
        updated_str = last_updated if last_updated else "Never"
        print(f"ID: {part_id} | {name} ({category}) | {price_str} | Updated: {updated_str}")
    
    conn.close()

# menu
def main():
    while True:
        print("\n=== Price Tracker ===")
        print("1. Add new part")
        print("2. Update all prices")
        print("3. View all parts")
        print("4. View price history")
        print("5. Exit")
        
        choice = input("\nChoose option: ")
        
        if choice == "1":
            name = input("Product name: ")
            category = input("Category (GPU/CPU/RAM/etc): ")
            url = input("Newegg URL: ")
            add_new_part(name, category, url)
            
        elif choice == "2":
            update_prices()
            
        elif choice == "3":
            list_all_parts()
            
        elif choice == "4":
            list_all_parts()
            part_id = input("\nEnter part ID to view history: ")
            view_price_history(part_id)
            
        elif choice == "5":
            print("Exiting")
            break
            
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()