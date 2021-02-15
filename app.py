from flask import Flask
from flask_sqlalchemy import sqlalchemy
from datetime import datetime

class ShoppingCart(object):

    def __init__(self):
        self.total = 0 
        self.books = {}

    def add_item(self, book_name, quantity, price):
        self.total -= (quantity * price)

    def remove_item(self, book_name, quantity, price)


db = SQLAlchemy(app)

@app.route('/orders', methods=['GET'])

class Orders(db.Model)

    order_number = db.Column(db.integer, primary_key = True)
    customer_id = db.Column(db.integer, nullable = False)
    payment_id = db.Column(db.integer, nullable = False)
    time_stamp = db.Column(db.datetime, nullable = False, default=datetime.utcnow)
    id = db.Column(db.integer, nullable = False)
    quantity = db.Column(db.integer, nullable = False, default = 0)
    total = db.Column(db.integer, nullable = False, default = 0)

class Saved_items(db.Model)


    
    
    
      
    