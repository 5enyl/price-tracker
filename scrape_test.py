import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

print("Fetching webpage...")
response = requests.get(url)


soup = BeautifulSoup(response.content, 'html.parser')


title = soup.find('h1').text
print(f"Book title: {title}")

price_element = soup.find('p', class_='price_color')
price = price_element.text
print(f"Price: {price}")

print("\nWeb scraping works!")