import unittest
from wtforms import Form, PasswordField
from btbs.forms import PasswordStrength

class TestPasswordStrength(unittest.TestCase):

    class TestForm(Form):
        password = PasswordField(validators=[PasswordStrength()])

    def test_empty_password(self):
        form = self.TestForm(password='')
        self.assertFalse(form.validate())
        self.assertIn('Password must be stronger.', form.password.errors)

    def test_weak_password_only_letters(self):
        form = self.TestForm(password='abcdef')
        self.assertFalse(form.validate())
        self.assertIn('Password is too weak. It should contain both letters and numbers.', form.password.errors)

    def test_weak_password_only_numbers(self):
        form = self.TestForm(password='123456')
        self.assertFalse(form.validate())
        self.assertIn('Password is too weak. It should contain both letters and numbers.', form.password.errors)

    def test_medium_password(self):
        form = self.TestForm(password='abc123')
        self.assertFalse(form.validate())
        self.assertIn('Password is medium. It should contain special characters for more strength.', form.password.errors)

    def test_strong_password_invalid_characters(self):
        form = self.TestForm(password='abc123!')
        self.assertFalse(form.validate())
        self.assertIn('Password should contain only letters, numbers, and special characters @#$%^&+=', form.password.errors)

    def test_strong_password_valid(self):
        form = self.TestForm(password='abc123@')
        self.assertTrue(form.validate())

if __name__ == '__main__':
    unittest.main()