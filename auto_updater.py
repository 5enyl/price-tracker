from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup

def scrape_newegg_price(url):
    """Scrape price from a Newegg product page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
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
                return price
        
        return None
        
    except Exception as e:
        print(f"Error scraping: {e}")
        return None

def update_all_prices():
    """Check all parts and update their prices"""
    print(f"\n{'='*50}")
    print(f"Starting price update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    
    # Get all parts that have URLs
    cursor.execute('SELECT id, name, url, price FROM parts WHERE url IS NOT NULL')
    parts = cursor.fetchall()
    
    if not parts:
        print("No parts with URLs to update!")
        conn.close()
        return
    
    print(f"Checking {len(parts)} part(s)...\n")
    
    updates_made = 0
    
    for part_id, name, url, old_price in parts:
        print(f"Checking: {name}")
        new_price = scrape_newegg_price(url)
        
        if new_price is None:
            print(f"Price could not be found\n")
            continue
        
        # Check if price changed
        if old_price is None or abs(new_price - old_price) > 0.01:
            if old_price:
                change = new_price - old_price
                if change > 0:
                    print(f"Price INCREASED by ${change:.2f}")
                else:
                    print(f"Price DECREASED by ${abs(change):.2f}")
            
            # Update parts table
            cursor.execute('''
                UPDATE parts 
                SET price = ?, last_updated = ?
                WHERE id = ?
            ''', (new_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), part_id))
            
            # Add to price history
            cursor.execute('''
                INSERT INTO price_history (part_id, price, source)
                VALUES (?, ?, ?)
            ''', (part_id, new_price, 'Newegg'))
            
            print(f"Updated to ${new_price:.2f}\n")
            updates_made += 1
        else:
            print(f"No change (${new_price:.2f})\n")
    
    conn.commit()
    conn.close()
    
    print(f"{'='*50}")
    print(f"Update complete! {updates_made} price(s) changed.")
    print(f"Next check scheduled for 1 hour from now")
    print(f"{'='*50}\n")

# Create scheduler
scheduler = BlockingScheduler()

scheduler.add_job(update_all_prices, 'interval', hours=1)

print("="*50)
print("AUTO PRICE UPDATER STARTED")
print("="*50)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Schedule: Checking prices every 1 hour")
print("Press Ctrl+C to stop")
print("="*50)
print()

#always update at least once at launch
print("Running initial price check...\n")
update_all_prices()

#Start the scheduler
try:
    scheduler.start()
except KeyboardInterrupt:
    print("\n\nShutting down auto-updater...")
    print("Exiting")