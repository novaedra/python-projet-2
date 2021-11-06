import csv
import requests
from bs4 import BeautifulSoup


def get_category_urls(website_url):
    """Return all urls of category for a website url given.
        website_url: url of the website we want to get categories.

        Returns:
            links: list of all categories urls.
    """
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
    """Return all books urls of category for a category url given.
            category_url: url of the category we want to get books urls.

            Returns:
                links: list of all books urls.
                false: if the request failed.
        """
    more_book_to_add = True
    links = []
    while more_book_to_add:
        # loop until no further next page button show up
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
            # replace the relative path part of the url
            link = link.replace('../../../', '')
            link = 'http://books.toscrape.com/catalogue/' + link
            links.append(link)

        next_page = soup.find("li", {"class": "next"})
        if next_page:
            # check if the next page button is present
            next_a = next_page.find('a')
            next_link = next_a['href']
            category_url = category_url[:category_url.rfind('/')] + '/' + next_link
        else:
            more_book_to_add = False

    return links


def get_product_info(book_url):
    """Return all books data for a book url given.
                book_url: url of the book we want to get data about.

                Returns:
                    product_info: dictionary of the book's data.
            """
    response = requests.get(book_url)
    if response.ok:
        # fetch the data from the book url page
        soup = BeautifulSoup(response.text, features="html.parser")
        title = soup.find("div", {"class": "col-sm-6 product_main"}).find("h1")
        product_information = soup.find("table").findAll("td")
        universal_product_code = product_information[0]
        price_including_tax = product_information[3]
        price_excluding_tax = product_information[2]
        number_available = product_information[5]
        product_description = soup.find("div", {"id": "product_description"})
        # prevent the no description error from Alice in Wonderland
        # https://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html
        product_description = product_description.findNext('p').text if product_description else 'No description'
        category = soup.find("ul", {"class": "breadcrumb"}).findAll('li')[2].find('a').text
        review_rating = soup.findAll('p', {"class": "star-rating"})[0]['class'][1]
        div_image = soup.find('div', {"class": "item active"})
        image_url = div_image.find('img')['src']
        image_url = image_url.replace('../../', 'http://books.toscrape.com/')

        # save the image of the book into the 'img' folder
        save_image(image_url)

        # save the data into a dictionary and return them
        product_info = {
            'product_page_url': book_url,
            'universal_product_code (upc)': universal_product_code.text,
            'title': title.text,
            'price_including_tax': price_including_tax.text.replace('Â', ''),
            'price_excluding_tax': price_excluding_tax.text.replace('Â', ''),
            'number_available': number_available.text,
            'product_description': product_description,
            'category': category,
            'review_rating': review_rating,
            'image_url': image_url
        }
        return product_info


def save_image(image_url):
    # split the image url to get filename and save the image to local directory 'img/'
    filename = image_url.split("/")[-1]
    with open('img/' + filename, "wb") as f:
        f.write(requests.get(image_url).content)


def create_books_csv(dict_data):
    """Save all books data to an svg file.
        dict_data: the list of dictionary we want to save to a svg file.

        Returns:
            None.
    """
    csv_columns = ['product_page_url',
                   'universal_product_code (upc)',
                   'title',
                   'price_including_tax',
                   'price_excluding_tax',
                   'number_available',
                   'product_description',
                   'category',
                   'review_rating',
                   'image_url']
    csv_file = "books_to_scrap.csv"
    try:
        # save all the books data into a svg file
        with open(csv_file, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")
