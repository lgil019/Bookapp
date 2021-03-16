from flask.app import Flask
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms import validators
from wtforms.fields.core import IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from bookstore.models import User



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That Email is taken.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    street = StringField('Street Adress')
    city = StringField('City')
    zip = IntegerField('Zip', validators=[NumberRange(min=10000, max=99999)])
    state = StringField('State',validators=[Length(min=2, max=2), Regexp('[a-zA-Z][a-zA-Z]')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That Username is taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That Email is taken.')


class SearchForm(FlaskForm):
    choices = [ ('id', 'All Books'),
                ('title', 'Title'),
                ('author', 'Author'),
                ('price', 'Price'),
                ('book_rating', 'Rating'),
                ('date_published', 'Date Published')]
    select = SelectField('Sort By:', choices=choices)
    submit = SubmitField('Search')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account associated with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class AddShippingAddress(FlaskForm):
    street = StringField('Street Adress')
    city = StringField('City')
    zip = IntegerField('Zip', validators=[NumberRange(min=10000, max=99999)])
    state = StringField('State',validators=[Length(min=2, max=2), Regexp('[a-zA-Z][a-zA-Z]')])
    submit = SubmitField('Add Shipping Address')

class AddPaymentMethod(FlaskForm):
    name = StringField('Name (as appears on card)', validators=[DataRequired()])
    card = IntegerField('Card Number', validators=[NumberRange(min=1000000000000000, max=9999999999999999)])
    expiration_month = IntegerField('Expiration Month (2 digit month)', validators=[NumberRange(min=1, max=12)])
    expiration_year = IntegerField('Expiration Year (4 digit year)', validators=[NumberRange(min=2021, max=2099)])
    csv = IntegerField('Security Code', validators=[NumberRange(min=1, max=999)])
    submit = SubmitField('Add Payment Method')