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
    return render_template('home.html', title="Home")


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

@app.route("/addcart", methods=['POST'])
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

@app.route("/shoppingcart", methods=['GET', 'POST'])
@login_required
def shoppingcart():
    return render_template('shoppingcart.html', title='Shopping Cart')


@app.route("/orders", methods=['GET'])
def orders():
    return render_template('orders.html', title='Orders')

#@app.route('/book/<int:id>')
#def book(id):
#    post = Book.query.get_or_404(id)
#    db.session.delete(post)
#    db.session.commit()
#    return redirect('/home')

@app.route('/browse', methods=['GET', 'POST'])
def browse():
    form = SearchForm()
    books = Book.query.all()
    path = url_for('static', filename='book_covers/')

    if form.validate_on_submit():
        selection = form.select.data
        books = Book.query.order_by(selection)
        return render_template('browse.html', title='Browse', form=form, books=books, path=path)

    return render_template('browse.html', title='Browse', books=books, form=form, path=path)    
    

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='cen4010group11@gmail.com', recipients=[user.email])
    msg.body = f'''To resset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

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