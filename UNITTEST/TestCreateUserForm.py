import unittest
from btbs.forms import createUserForm
from btbs.models import User
from btbs import app, db
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

class TestCreateUserForm(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        app.config['TESTING'] = True
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        self.app_context.pop()

    def test_create_user_form_invalid_username(self):
        with self.client:
            with app.test_request_context():
                with patch('btbs.models.User.query.filter_by') as mock_query:
                    # Mock user with existing email
                    mock_user = User(username='existinguser', email='existinguser@example.com', password='ExistingPass123!')
                    mock_query.return_value.first.return_value = mock_user
                    
                    # Test with invalid username
                    form = createUserForm(data={
                        'username': 'invalid user',
                        'email': 'existinguser@example.com',
                        'password': 'ValidPass123!',
                        'confirm_password': 'ValidPass123!'
                    })
                    self.assertFalse(form.validate())
                    self.assertIn('Username contains invalid characters.', form.username.errors)

                    # Test with existing email
                    form = createUserForm(data={
                        'username': 'newuser',
                        'email': 'herald@gmail.com',
                        'password': 'ValidPass123!',
                        'confirm_password': 'ValidPass123!'
                    })
                    self.assertFalse(form.validate())
                    self.assertIn('Email already taken.', form.email.errors)

    def test_create_user_form_password_mismatch(self):
        form = createUserForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'ValidPass123!',
            'confirm_password': 'DifferentPass123!'
        })
        self.assertFalse(form.validate())
        self.assertIn('Field must be equal to password.', form.confirm_password.errors)

    def test_create_user_form_weak_password(self):
        form = createUserForm(data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'weakpass',
            'confirm_password': 'weakpass'
        })
        self.assertFalse(form.validate())
        self.assertIn('Password is too weak. It should contain both letters and numbers.', form.password.errors)

if __name__ == '__main__':
    unittest.main()