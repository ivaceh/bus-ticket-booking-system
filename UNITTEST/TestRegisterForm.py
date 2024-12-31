import unittest
from btbs.forms import RegisterForm
from btbs.models import User
from btbs import app, db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

class TestRegisterForm(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_invalid_username_characters(self):
        with self.client:
            with app.test_request_context():
                form = RegisterForm(data={
                    'username': 'invalid user',
                    'email': 'validuser@example.com',
                    'password': 'ValidPass123!',
                    'confirm_password': 'ValidPass123!'
                })
                self.assertFalse(form.validate())
                self.assertIn('Username contains invalid characters.', form.username.errors)

    def test_username_already_taken(self):
        with self.client:
            with app.test_request_context():
                with patch('btbs.models.User.query.filter_by') as mock_query:
                    mock_user = User(username='existinguser', email='existinguser@example.com', password='ExistingPass123!')
                    mock_query.return_value.first.return_value = mock_user
                    form = RegisterForm(data={
                        'username': 'newuser',
                        'email': 'newuser@example.com',
                        'password': 'ValidPass123!',
                        'confirm_password': 'ValidPass123!'
                    })
                    self.assertFalse(form.validate())
                    self.assertIn('Username already taken.', form.username.errors)

    def test_email_already_taken(self):
        with self.client:
            with app.test_request_context():
                user = User(username='newuser', email='existinguser@example.com', password='ExistingPass123!')
                try:
                    user.save()
                except IntegrityError:
                    db.session.rollback()
                    form = RegisterForm(data={
                        'username': 'newuser',
                        'email': 'existinguser@example.com',
                        'password': 'ValidPass123!',
                        'confirm_password': 'ValidPass123!'
                    })
                    self.assertFalse(form.validate())
                    self.assertIn('Email already taken.', form.email.errors)
                form = RegisterForm(data={
                    'username': 'newuser',
                    'email': 'existinguser@example.com',
                    'password': 'ValidPass123!',
                    'confirm_password': 'ValidPass123!'
                })
                self.assertFalse(form.validate())
                self.assertIn('Email already taken.', form.email.errors)

    def test_password_strength(self):
        with self.client:
            with app.test_request_context():
                form = RegisterForm(data={
                    'username': 'validuser',
                    'email': 'validuser@example.com',
                    'password': 'weakpass',
                    'confirm_password': 'weakpass'
                })
                self.assertFalse(form.validate())
                self.assertIn('Password is too weak. It should contain both letters and numbers.', form.password.errors)

    def test_password_mismatch(self):
        with self.client:
            with app.test_request_context():
                form = RegisterForm(data={
                    'username': 'validuser',
                    'email': 'validuser@example.com',
                    'password': 'ValidPass123!',
                    'confirm_password': 'DifferentPass123!'
                })
                self.assertFalse(form.validate())
                self.assertIn('Field must be equal to password.', form.confirm_password.errors)

if __name__ == '__main__':
    unittest.main()