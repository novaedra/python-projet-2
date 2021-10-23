# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import csv


def get_category_urls(website_url):
    response = requests.get(website_url)
    if response.ok:
        links = []
        soup = BeautifulSoup(response.text, features="html.parser")
        side_menu = soup.find("ul", {"class": "nav nav-list"}).find("ul")
        category_links = side_menu.findAll("li")
        for category_link in category_links:
            a = category_link.find('a')
            link = a['href']
            links.append(website_url + link)
        return links


def get_books_of_category(category_url):
    more_book_to_add = True
    links = []
    while more_book_to_add is True:
        response = requests.get(category_url)
        if response.ok:
            soup = BeautifulSoup(response.text, features="html.parser")
        else:
            return False

        products = soup.findAll("article", {"class": "product_pod"})
        for product in products:
            h3 = product.find('h3')
            a = h3.find('a')
            link = a['href']
            link = link.replace('../../../', '')
            link = 'http://books.toscrape.com/catalogue/' + link
            links.append(link)

        next_page = soup.find("li", {"class": "next"})
        if next_page is not None:
            next_a = next_page.find('a')
            next_link = next_a['href']
            category_url = category_url[:category_url.rfind('/')] + '/' + next_link
        else:
            more_book_to_add = False

    return links


def get_product_info(book_url):
    response = requests.get(book_url)
    if response.ok:
        soup = BeautifulSoup(response.text, features="html.parser")
        title = soup.find("div", {"class": "col-sm-6 product_main"}).find("h1")
        product_information = soup.find("table").findAll("td")
        universal_product_code = product_information[0]
        price_including_tax = product_information[3]
        price_excluding_tax = product_information[2]
        number_available = product_information[5]
        product_description = soup.find("div", {"id": "product_description"})
        if product_description:
            product_description = product_description.findNext('p').text
        else:
            product_description = 'Pas de description'
        category = soup.find("ul", {"class": "breadcrumb"}).findAll('li')[2].find('a').text
        review_rating = soup.findAll('p', {"class": "star-rating"})[0]['class'][1]
        div_image = soup.find('div', {"class": "item active"})
        image_url = div_image.find('img')['src']
        image_url = image_url.replace('../../', 'http://books.toscrape.com/')

        product_info = [
            book_url,
            universal_product_code.text,
            title.text,
            price_including_tax.text.replace('Â', ''),
            price_excluding_tax.text.replace('Â', ''),
            number_available.text,
            product_description,
            category,
            review_rating,
            image_url
        ]

        filename = image_url.split("/")[-1]
        with open('img/' + filename, "wb") as f:
            f.write(requests.get(image_url).content)

        return product_info


category_list = get_category_urls('http://books.toscrape.com/')

total_books_number = 0
header = ['product_page_url',
          'universal_ product_code (upc)',
          'title',
          'price_including_tax',
          'price_excluding_tax',
          'number_available',
          'product_description',
          'category',
          'review_rating',
          'image_url']
products_info = []
for category in category_list:
    books = get_books_of_category(category)
    print('category : ', category, 'books : ', len(books))
    total_books_number += len(books)
    for book in books:
        book_to_display = book
        product_info = get_product_info(book)
        products_info.append(product_info)


with open('books_to_scrap.csv', 'w', encoding="utf-8") as csvfile:
    write = csv.writer(csvfile)
    write.writerow(header)
    for row in products_info:
        write.writerow(row)

print('Total numbers of books : ', total_books_number)
