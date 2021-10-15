import requests
from bs4 import BeautifulSoup

url='http://books.toscrape.com/'

response = requests.get(url)

if response.ok:
    soup = BeautifulSoup(response.text)
    print(soup)