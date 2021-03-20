import bcrypt
from flask import render_template, url_for, flash, redirect, request, session
from bookstore import app, db, bcrypt, mail
from bookstore.forms import AddPaymentMethod, AddShippingAddress, RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, RequestResetForm, ResetPasswordForm
from bookstore.models import PaymentMethod, ShippingAddress, User, Book, Reviews, Author
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import desc


def merge(cart, item):
    if isinstance(cart, dict) and isinstance(item, dict):
        return dict(list(cart.items()) + list(item.items()))
    return False

@app.route("/")
def home():
    path = url_for('static', filename='book_covers/')
    return render_template('home.html', title="Home", path=path)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login')) 
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash(f'{form.email.data} Successfully Logged In!', 'success')
            login_user(user, remember=form.remember.data) 
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('home'))


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.street = form.street.data
        current_user.city = form.city.data
        current_user.zip = form.zip.data
        current_user.state = form.state.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.street.data = current_user.street
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.zip.data = current_user.zip
    return render_template('account.html', title='Account', form=form)


@app.route("/addcart", methods=['POST', 'GET'])
@login_required
def addcart():
    try:
        book_id = request.form.get('book_id')
        quantity = request.form.get('quantity')
        book = Book.query.filter_by(id=book_id).first()
        if book_id and quantity and request.method == "POST":
            item = {book_id:{'title':book.title, 'author': book.author, 'price': float(book.price), 'quantity':quantity}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                session['Shoppingcart'] = merge(session['Shoppingcart'], item)
            else:
                session['Shoppingcart'] = item
            for key, item in session['Savebook'].items():
                if int(key) == book.id:
                    return redirect(url_for('removesaved', id=book.id))
    except Exception as e:
        print(e)

    return redirect(request.referrer)


@app.route("/movetosaved/<int:id>", methods=['GET','POST'])
@login_required
def movetosaved(id):
    try:
        book_id = id
        book = Book.query.filter_by(id=book_id).first()
        if book_id and request.method == "POST":
            item = {str(book_id):{'title':book.title, 'author': book.author, 'price': float(book.price), 'quantity':1}}
            if 'Savebook' in session:
                print(session['Savebook'])
                session['Savebook'] = merge(session['Savebook'], item)
            else:
                session['Savebook'] = item
            for key, item in session['Shoppingcart'].items():
                if int(key) == id:
                    return redirect(url_for('removecart', id=id))
    except Exception as e:
        print(e)
    return redirect(request.referrer)


@app.route("/removesaved/<int:id>")
@login_required
def removesaved(id):
    if 'Savebook' not in session and len(session['Savebook']) <= 0:
        return redirect(request.referrer)
    try:
        session.modified = True
        for key, item in session['Savebook'].items():
            if int(key) == id:
                session['Savebook'].pop(key, None)
                return redirect(url_for('shoppingcart'))
    except Exception as e:
        print(e)
        return redirect(url_for('shoppingcart'))
        
        
@app.route("/updatecart/<int:id>", methods=['POST'])
@login_required
def updatecart(id):
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(request.referrer)
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == id:
                    item['quantity'] = quantity
                    return redirect(url_for('shoppingcart'))
        except Exception as e:
            print(e)
            return redirect(url_for('shoppingcart'))


@app.route("/removecart/<int:id>")
@login_required
def removecart(id):
    if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
        return redirect(request.referrer)
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('shoppingcart'))
    except Exception as e:
        print(e)
        return redirect(url_for('shoppingcart'))


@app.route("/shoppingcart", methods=['GET', 'POST'])
@login_required
def shoppingcart():
    total = 0
    subtotal = 0
    if 'Shoppingcart' not in session:
        return render_template('shoppingcart.html', title='Shopping Cart', subtotal=0)
    else:
        for key, product in session['Shoppingcart'].items():
            total = float(product['price']) * int(product['quantity'])
            subtotal += total
        return render_template('shoppingcart.html', title='Shopping Cart', subtotal = subtotal)


@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book(id):
    book = Book.query.get_or_404(id)
    path = url_for('static', filename='book_covers/')
    reviews = Reviews.query.filter_by(book_id=book.id)

    if request.method == 'POST':
        #Must be logged in to Post Reviews
        if not current_user.is_authenticated:
            flash('Please login to comment!', 'danger')
            return redirect(url_for('login')) 

        message = request.form.get('message')
        rating = request.form.get('rate')
        checked = 'check' in request.form #is anonymous posting
        
        #There is a review
        if message is not None:
            if checked:
                review = Reviews(review=message,user_id=-1, book_id=book.id)
            else:
                review = Reviews(review=message,user_id=current_user.id, book_id=book.id)
            db.session.add(review)
            db.session.commit()
            flash('Your review has has been submited!', 'success')
            return redirect(request.url)

        #There is a rating
        if rating is not None:
            numRatings = book.numRatings
            sumRatings = book.sumRatings
            numRatings+=1
            sumRatings+=int(rating)
            book.numRatings = numRatings
            book.sumRatings = sumRatings
            book.book_rating = sumRatings / numRatings
            db.session.commit()

    return render_template('book.html', title = book.title, book=book, path=path, reviews=reviews, User=User)


@app.route('/author/<string:author>', methods=['GET', 'POST'])
def book_author(author):
    page = request.args.get('author')
    path = url_for('static', filename='book_covers/')
    books = Book.query.filter_by(author=author)
    authors = Author.query.filter_by(author_id=author).first()
    #books = Book.query.filter_by(author=author).paginate(page=page,per_page=5)
    #return render_template('author.html', title=Book.author, author=author, books=books)
    return render_template('author.html', title=author ,books=books, author=author, path=path, authors=authors)


@app.route('/browse', methods=['GET', 'POST'])
def browse():
    page = request.args.get('page', 1, type=int)  #Javi's Code
    form = SearchForm()
    #books = Book.query.all()   #Old code to display all
    books = Book.query.paginate(page=page,per_page=5)     #Javi's Code
    path = url_for('static', filename='book_covers/')

    if form.validate_on_submit():
        selection = form.select.data
        #books = Book.query.order_by(selection)
        books = Book.query.order_by(selection).paginate(page=page,per_page=5)   
        return render_template('browse.html', title='Browse', form=form, books=books, path=path)

    return render_template('browse.html', title='Browse', books=books, form=form, path=path)    

@app.route('/genres', methods=['GET', 'POST'])
def genres():
    genre = request.args.get('genre')
    if genre == None or genre == 'All':
        books = Book.query.all()
    else:
        books = Book.query.filter_by(genre=genre)
    path = url_for('static', filename='book_covers/')
    return render_template('genres.html', title='Genres', books=books, path=path)   

@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
    rating = request.args.get('rating', type=int)
    book_rating = Book.book_rating
    if rating == None:
        books = Book.query.order_by(desc(book_rating))
    else:
        books = Book.query.filter(book_rating >= rating)
        books = books.order_by(desc(book_rating))
    path = url_for('static', filename='book_covers/')
    return render_template('ratings.html', title='Ratings', books=books, path=path)  


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='cen4010group11@gmail.com', recipients=[user.email])
    msg.body = f'''To resset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

This Link will expire in 60 minutes.

If you did not make this request, ignore this email.
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset Password Instructions Sent. Please check spam folder if you did not see it arrive.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = RequestResetForm()
    form.email.data = current_user.email
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset Password Instructions Sent. Please check spam folder if you did not see it arrive.', 'info')
        return redirect(url_for('account'))
    return render_template('change_password.html', title='Change Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired request', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('login')) 
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/shipping", methods=['GET', 'POST'])
def shipping():
    form = AddShippingAddress()
    user = current_user
    shipping = ShippingAddress.query.filter_by(user=user)
    if form.validate_on_submit():
        address = ShippingAddress(street=form.street.data, city=form.city.data, state=form.state.data, zip=form.zip.data, user=user)
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('shipping'))
    return render_template('shipping.html', title='Shipping Addresses', form=form, shipping=shipping)

@app.route("/payments", methods=['GET', 'POST'])
def payments():
    form = AddPaymentMethod()
    user = current_user
    payments = PaymentMethod.query.filter_by(user=user)
    if form.validate_on_submit():
        payment = PaymentMethod(name=form.name.data, card=form.card.data, exp_month=form.expiration_month.data, exp_year=form.expiration_year.data, csv=form.csv.data, user=user)
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('payments'))
    return render_template('payments.html', title='Payment Details', form=form, payments=payments)


@app.route("/shipping/<int:shipping_id>/remove", methods=['GET','POST'])
@login_required
def removeshipping(shipping_id):
    address = ShippingAddress.query.get_or_404(shipping_id)
    #if address.user_id != current_user:
    #    abort(403)
    db.session.delete(address)
    db.session.commit()
    return redirect(url_for('shipping'))


@app.route("/payment/<int:payment_id>/remove", methods=['GET','POST'])
@login_required
def removepayment(payment_id):
    payment = PaymentMethod.query.get_or_404(payment_id)
    #if address.user_id != current_user:
    #    abort(403)
    db.session.delete(payment)
    db.session.commit()
    return redirect(url_for('payments'))
