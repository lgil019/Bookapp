#from bookstore import db
from bookstore.models import User, Book

book = Book.query.all()
print(book)

for item in book:
    print(item)
