import requests
from bs4 import BeautifulSoup

def search_newegg(query):
    url = f"https://www.newegg.com/p/pl?d={query.replace(' ', '+')}"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
}


    response = requests.get(url, headers=headers, timeout=30)

    soup = BeautifulSoup(response.content, 'html.parser')

    results = []
    items = soup.find_all('div', class_='item-cell')

    for item in items:
        name_tag = item.find('a', class_='item-title')
        price_tag = item.find('li', class_='price-current')

        if not name_tag:
            continue

        name = name_tag.text.strip()

        excluded_keywords = ['gaming pc', 'desktop', 'gaming desktop', 'prebuilt', 'tower', 'insights', 'skytech', 'avgpc', 'mxz', 'clx', 'andromeda']
        if any(keyword in name.lower() for keyword in excluded_keywords):
            continue


        url = name_tag['href']


        price = None
        if price_tag:
            strong = price_tag.find('strong')
            sup = price_tag.find('sup')
            if strong:
                try:
                    price = float(strong.text.replace(',', '') + (sup.text if sup else '.00'))
                except ValueError:
                    price = None


        results.append({'name': name, 'url': url, 'price': price})

    return results

if __name__ == '__main__':
    query = 'RTX 4090'
    results = search_newegg(query)
    print(f"Found {len(results)} results")
    for r in results:
        print(r['name'], '-', r['price'])
