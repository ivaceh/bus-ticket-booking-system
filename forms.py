from flask_wtf import FlaskForm
import re
from wtforms import Form as BaseForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
  
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

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=25), PasswordStrength()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='create account')