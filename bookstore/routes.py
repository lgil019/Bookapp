import bcrypt
from flask import render_template, url_for, flash, redirect, request, session
from bookstore import app, db, bcrypt, mail
from bookstore.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, RequestResetForm, ResetPasswordForm
from bookstore.models import User, Book
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


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
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    return redirect(request.referrer)


@app.route("/movetosaved/<int:id>", methods=['GET','POST'])
@login_required
def movetosaved(id):
    try:
        quantity = 0
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                quantity = item['quantity']

        book = Book.query.filter_by(id=id).first()
        book_id = book.id
        print(quantity)
        if quantity:
            item = {book_id:{'title':book.title, 'author': book.author, 'price': float(book.price), 'quantity':quantity}}
            if 'Savebook' in session:
                session['Savebook'] = merge(session['Savebook'], item)
            else:
                session['Savebook'] = item
                #return redirect(request.referrer)
    except Exception as e:
        print(e)

    return redirect(url_for('removecart', id=key))


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


@app.route("/orders", methods=['GET'])
def orders():
    return render_template('orders.html', title='Orders')


@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book(id):
    image_file = url_for('static', filename='book_covers/' + Book.image_file)
    post = Book.query.get_or_404(id)
    return render_template('book.html', title = Book.title, post=post, image_file=image_file)


@app.route('/author/<string:author>', methods=['GET', 'POST'])
def book_author(author):
    page = request.args.get('page', 1, type=int)
    author = Book.query.filter_by(author=author).first_or_404()
    books = Book.query.filter_by(author=author).paginate(page=page,per_page=5)
    return render_template('author.html', title=Book.author, author=author, books=books)


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
        books = Book.query.order_by(selection).paginate(page=page,per_page=5)   #Javi's code
        return render_template('browse.html', title='Browse', form=form, books=books, path=path)

    return render_template('browse.html', title='Browse', books=books, form=form, path=path)    
    

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