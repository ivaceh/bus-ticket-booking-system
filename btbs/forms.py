from flask_wtf import FlaskForm
import re
from wtforms import Form as BaseForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, HiddenField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from btbs.models import User, Bus, Destination  # Assuming you have a User model defined in models.py
from btbs import app

# Password strength validation
class PasswordStrength:
    def __init__(self, message: str | None = None) -> None:
        if not message:
            message = 'Password must be stronger.'
        self.message = message

    def __call__(self, form: BaseForm, field: StringField) -> None:
        password = field.data
        if not password:
            raise ValidationError(self.message)
        
        # Check for weak password
        if re.fullmatch(r'[A-Za-z]+|\d+', password):
            raise ValidationError('Password is too weak. It should contain both letters and numbers.')

        # Check for medium password
        if re.fullmatch(r'[A-Za-z0-9]+', password):
            raise ValidationError('Password is medium. It should contain special characters for more strength.')

        # Check for strong password
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]+', password):
            raise ValidationError('Password should contain only letters, numbers, and special characters @#$%^&+=')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25)])
    submit = SubmitField(label='login')

    def validate_username(self, username):
        if not re.match("^[a-zA-Z0-9_.-]+$", username.data):
            raise ValidationError('Username contains invalid characters.')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25), PasswordStrength()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='create account')

    def validate_username(self, username):
        if not re.match("^[a-zA-Z0-9_.-]+$", username.data):
            raise ValidationError('Username contains invalid characters.')
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken.')

class createUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25), PasswordStrength()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='create user')

    def validate_username(self, username):
        if not re.match("^[a-zA-Z0-9_.-]+$", username.data):
            raise ValidationError('Username contains invalid characters.')
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken.')

class createBusForm(FlaskForm):
    name = StringField('Bus Name', validators=[DataRequired(), Length(min=4, max=25)])
    capacity = StringField('Bus Capacity', validators=[DataRequired()])
    submit = SubmitField(label='create bus')

    def validate_name(self, name):
        if not re.match("^[a-zA-Z0-9_.\s-]+$", name.data):
            raise ValidationError('Bus name contains invalid characters.')
        with app.app_context():
            bus = Bus.query.filter_by(name=name.data).first()
            if bus:
                raise ValidationError('Bus name already exists.')

class createDestinationForm(FlaskForm):
    name = StringField('Destination Name', validators=[DataRequired(), Length(min=4, max=25)])
    price = StringField('Price', validators=[DataRequired()])
    distance = StringField('Distance', validators=[DataRequired()])
    submit = SubmitField(label='create destination')

    def validate_name(self, name):
        if not re.match("^[a-zA-Z0-9_.-]+$", name.data):
            raise ValidationError('Destination name contains invalid characters.')
        with app.app_context():
            destination = Destination.query.filter_by(name=name.data).first()
            if destination:
                raise ValidationError('Destination name already exists.')

# User books a ticket or cancel it
class bookBusTicketForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(bookBusTicketForm, self).__init__(*args, **kwargs)
        with app.app_context():
            self.bus_id.choices = [(bus.id, bus.name) for bus in Bus.query.all()]
            self.destination_id.choices = [(destination.id, destination.name) for destination in Destination.query.all()]

    bus_id = SelectField('Bus ID', validators=[DataRequired()])
    destination_id = SelectField('Destination Name', validators=[DataRequired()])
    travel_date = DateField('Travel Date', format='%Y-%m-%d', validators=[DataRequired()])
    user_id = HiddenField('User ID')
    booking_date = HiddenField('Booking Date')
    submit = SubmitField('Book Ticket')