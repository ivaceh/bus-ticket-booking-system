import unittest
from flask import Flask
from btbs.forms import LoginForm
from wtforms import ValidationError

class TestLoginForm(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_valid_username_and_password(self):
        form = LoginForm(username="validuser", password="validpassword")
        self.assertTrue(form.validate())

    def test_invalid_username_characters(self):
        form = LoginForm(username="invalid user!", password="validpassword")
        with self.assertRaises(ValidationError):
            form.validate_username(form.username)

    def test_short_username(self):
        form = LoginForm(username="usr", password="validpassword")
        self.assertFalse(form.validate())

    def test_long_username(self):
        form = LoginForm(username="u" * 26, password="validpassword")
        self.assertFalse(form.validate())

    def test_empty_username(self):
        form = LoginForm(username="", password="validpassword")
        self.assertFalse(form.validate())

    def test_empty_password(self):
        form = LoginForm(username="validuser", password="")
        self.assertFalse(form.validate())

    def test_short_password(self):
        form = LoginForm(username="validuser", password="short")
        self.assertFalse(form.validate())

    def test_long_password(self):
        form = LoginForm(username="validuser", password="p" * 26)
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()