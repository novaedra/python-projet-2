from utils import (
    get_category_urls, get_books_of_category, get_product_info, create_books_csv
)


if __name__ == '__main__':

    # Retrieve all categories url of the website
    categories = get_category_urls('http://books.toscrape.com/')

    total_books_number = 0
    products_info = []
    for category in categories:
        # get all books url from category
        books = get_books_of_category(category)
        print('category : ', category, 'books : ', len(books))
        total_books_number += len(books)
        for book in books:
            book_to_display = book
            # get all books data from books url
            product_info = get_product_info(book)
            # save all books data into a collection
            products_info.append(product_info)

    # Write all products into a CSV
    create_books_csv(products_info)

    print('Total numbers of books : ', total_books_number)
