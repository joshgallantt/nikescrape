import re
import requests
from bs4 import BeautifulSoup
import csv

API_URL = 'https://api.nike.com/cic/browse/v1'
endpoint = '/product_feed/rollup_threads/v2?filter=marketplace(GB)&filter=language(en-GB)&filter=employeePrice(true)&filter=attributeIds({concept_id})&anchor={anchor}&consumerChannelId={channel_id}&count={count}'
data = {'queryid': 'products', 'endpoint': endpoint}
product_list = []

class Product:
    def __init__(self, url, title = None, subtitle = None, color = None, currentPrice = None, fullPrice = None, onSale = None, stock = None, membersOnly = None, image = None, description = None, materials = None):
        self.url = 'https://www.nike.com/gb' + url[13:]
        self.title = title
        self.subtitle = subtitle
        self.color = color
        self.description = description
        self.image = image
        self.materials = materials
        self.currentPrice = currentPrice
        self.fullPrice = fullPrice
        self.onSale = onSale
        self.stock = stock
        self.membersOnly = membersOnly

def scrape_url(url):
    with requests.session() as s:
        soup = BeautifulSoup( s.get(url).text, 'html.parser' )

        concept_id = soup.select_one('meta[name="branch:deeplink:$deeplink_path"]')['content'].split('=')[-1]
        channel_id = re.search(r'"channelId":"(.*?)"', str(soup)).group(1)
        product_count = soup.select_one('.wall-header__item_count').text[1:-1]

        position = 0
        while position < int(product_count):

            data['endpoint'] = endpoint.format(concept_id=concept_id, channel_id=channel_id, anchor=position, count=50)
            json_data = s.get(API_URL, params=data).json()
            print(json_data['data']['products']['products'])

            for i, product in enumerate(json_data['data']['products']['products'], position + 1):
                if len(product['colorways']) > 1:
                    for each_prod in product['colorways']:
                        product_list.append(Product(url = each_prod['pdpUrl'],
                                                    title = product['title'],
                                                    subtitle= product['subtitle'],
                                                    color = each_prod['colorDescription'],
                                                    currentPrice= each_prod['price']['currentPrice'],
                                                    fullPrice= each_prod['price']['fullPrice'],
                                                    onSale= each_prod['price']['discounted'],
                                                    stock= each_prod['inStock'],
                                                    membersOnly= each_prod['isMemberExclusive'],
                                                    image= each_prod['images']['squarishURL']))
                else:
                    product_list.append(Product(product['url'],
                                                title = product['title'],
                                                subtitle= product['subtitle'],
                                                color = product['colorDescription'],
                                                currentPrice= product['price']['currentPrice'],
                                                fullPrice= product['price']['fullPrice'],
                                                onSale= product['price']['discounted'],
                                                stock = product['inStock'],
                                                membersOnly = product['isMemberExclusive'],
                                                image= product['images']['squarishURL']))

            position += 50

def write_to_csv():
    with open('nike.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Product', 'Type', 'Url', 'Color','Current Price','Reg Price', 'On Sale', 'In Stock', 'Members Only', 'Image'])

        for product in product_list:
            data = [product.title,
                    product.subtitle,
                    # f'=HYPERLINK("{product.url}")',
                    product.url,
                    product.color,
                    product.currentPrice,
                    product.fullPrice,
                    product.onSale,
                    product.stock,
                    product.membersOnly,
                    # f'=HYPERLINK("{product.image}")']
                    product.image]
            writer.writerow(data)

if __name__ == "__main__":
    print("\nExample url: https://www.nike.com/gb/w/mens-football-shoes-1gdj0znik1zy7ok\n")
    url = input("Enter a url: ")
    scrape_url(url)
    write_to_csv()
