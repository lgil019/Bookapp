#from bookstore import db
from bookstore.models import User

myList = User.query.all()


for row in myList:
    print(row.username)
    print(row.email)
    print(row.password)