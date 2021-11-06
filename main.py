from utils import (
    get_category_urls, get_books_of_category, get_product_info, create_books_csv
)

if __name__ == '__main__':

    # Retrieve all categories url of the website
    categories = get_category_urls('http://books.toscrape.com/')

    total_books_number = 0
    category_number = 1
    for category in categories:
        # get all books url from category
        category_number += 1
        products_info = []
        books = get_books_of_category(category)
        category_name = category.split('/')
        category_name = category_name[6].replace('_' + str(category_number), '')
        category_name.capitalize()
        print(category_name, ' : ', len(books))
        total_books_number += len(books)
        for book in books:
            book_to_display = book
            # get all books data from books url
            product_info = get_product_info(book)
            # save all books data from a category into a list
            products_info.append(product_info)

        # Write all products of a category into a CSV
        create_books_csv(category_name, products_info)

    print('Total numbers of books : ', total_books_number)
