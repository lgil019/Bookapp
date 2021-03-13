from bookstore.models import Book

books = Book.query.all()


for book in books:
    print(book.title)
    print("--- "  + book.author)

