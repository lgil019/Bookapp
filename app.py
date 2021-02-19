from flask import Flask
from flask_sqlalchemy import sqlalchemy
from datetime import datetime

class ShoppingCart(object):

    def __init__(self):
        self.total = 0 
        self.books = {}

    def add_item(self, book_name, quantity, price):
        self.total += (quantity * price)
        self.books = (book_name : quantity)

    def remove_item(self, book_name, quantity, price):
        self.total -= (quantity * price)
        if quantity > self.books[book_name]
           del self.books[book_name]
        self.books[book_name] -= quantity

    def checkout()
        balance = 0
        if cash_paid < self.total:
          return "Not enough funds for purchase."
        balance = cash_paid - self.total
          return balance

class Shop(ShoppingCart):

    def __init__(self):
      ShoppingCart.__init__(self)
      self.quantity = 100

    def remove_item(self):
        self.quantity -= 1

db = SQLAlchemy(app)

@app.route('/orders', methods=['GET'])

class Orders(db.Model)

    order_number = db.Column(db.integer, primary_key = True)
    customer_id = db.Column(db.integer, nullable = False)
    payment_id = db.Column(db.integer, nullable = False)
    time_stamp = db.Column(db.datetime, nullable = False, default=datetime.utcnow)
    title = db.Column(db.integer, nullable = False)
    quantity = db.Column(db.integer, nullable = False, default = 0)
    total = db.Column(db.integer, nullable = False, default = 0)

@app.route('/shoppingcart', methods=['GET'])

class ShoppingCart(db.Model)

    title = db.Column(db.String(30), nullable=False)
    price = db.Column(db.integer, nullable = False, default = 0)
    quantity = db.Column(db.integer, nullable = False, default = 0)
    total = db.Column(db.integer, nullable = False, default = 0)


    
    
    
      
    