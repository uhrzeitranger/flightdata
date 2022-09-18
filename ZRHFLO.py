from bs4 import BeautifulSoup
import requests

url = f'https://www.google.com/flights'
page_data = requests.get(url)
page_soup = BeautifulSoup(page_data.content, 'html.parser')
print(page_soup)