from sqlalchemy.orm import backref, relation, relationship
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from bookstore import db, login_manager, app
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    street = db.Column(db.String(60))
    city = db.Column(db.String(30))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(5))
    addresses = db.relationship('ShippingAddress', backref='user')
    payments = db.relationship('PaymentMethod', backref='user')
    purchased = db.relationship('Purchases', backref='user')
    review = db.relationship('Review', backref='user')
    
    def get_reset_token(self, expires_sec=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(30), nullable=False)
    genre = db.Column(db.String(30), nullable=False)
    book_rating = db.Column(db.Integer, nullable=False, default = 'N/A')
    publisher = db.Column(db.String(30), nullable=False, default = 'N/A')
    summary = db.Column(db.String(), nullable=False, default = 'N/A')
    date_published = db.Column(db.String)
    price = db.Column(db.Numeric(8,2), nullable=False)
    image = db.Column(db.String(40), default='imagenotfound.jpg')
    numRatings = db.Column(db.Integer, default=0)
    sumRatings = db.Column(db.Integer, default=0)
    purchased = db.relationship('Purchased', backref='book')
    review = db.relationship('Purchased', backref='book')
    


    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', '{self.genre}', '{self.book_rating}', '{self.publisher}', '{self.date_published}')"


class ShippingAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    street = db.Column(db.String(60))
    city = db.Column(db.String(30))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(5))

    def __repr__(self):
        return f"Address('{self.user_id}', '{self.street}', '{self.city}', '{self.state}', '{self.zip}')"

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    card = db.Column(db.String(16))
    exp_month = db.Column(db.String(2))
    exp_year = db.Column(db.String(4))
    csv = db.Column(db.String(3))

    def __repr__(self):
        return f"Card('{self.user_id}', '{self.card}', '{self.exp_month}', '{self.exp_year}', '{self.csv}')"

class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))



