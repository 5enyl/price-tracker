import requests
from bs4 import BeautifulSoup
import sqlite3

def newegg_scrape(url):
    """
    Scrape price from a Newegg product page
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # find price-current
        price_element = soup.find('li', class_='price-current')
        
        if price_element:
            # get main price in <strong>
            strong_tag = price_element.find('strong')
            sup_tag = price_element.find('sup')
            
            if strong_tag:
                main_price = strong_tag.text.strip().replace(',', '')
                cents = sup_tag.text.strip() if sup_tag else '.00'
                
                # combine cents w dollars
                full_price = main_price + cents
                price = float(full_price)
                
                print(f"✓ Found price: ${price}")
                return price
        
        print("✗ Could not find price element")
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def add_part_with_price(name, category, url):
    """
    Add a part to the database with its current price from Newegg
    """
    # scraping price
    price = scrape_newegg_price(url)
    
    if price is None:
        print("Could not get price. Add manually? (y/n)")
        if input().lower() == 'y':
            price = float(input("Enter price manually: $"))
        else:
            return
    
    # add db
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO parts (name, category, price)
        VALUES (?, ?, ?)
    ''', (name, category, price))
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Added {name} to database at ${price}")

# test
print("=== Newegg Price Scraper ===\n")

product_url = input("Paste a Newegg product URL: ")

if product_url:
    name = input("Product name: ")
    category = input("Category (GPU/CPU/RAM/etc): ")
    
    add_part_with_price(name, category, product_url)
    
    print("\nCheck your database in SQLite Browser to see the new part!")
else:
    print("No URL provided")