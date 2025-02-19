import unittest
from btbs.forms import createBusForm
from btbs.models import Bus
from btbs import app, db
from flask import Flask

from flask_wtf.csrf import CSRFProtect

class TestCreateBusForm(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_validate_name_valid(self):
        form = createBusForm(name="ValidBusName", capacity="50")
        self.assertTrue(form.validate())

    def test_validate_name_invalid_characters(self):
        with app.test_request_context():
            form = createBusForm(name="Invalid@Bus#Name", capacity="50")
            self.assertFalse(form.validate())
            self.assertIn('Bus name contains invalid characters.', form.name.errors)

    def test_validate_name_already_exists(self):
        with app.app_context():
            # Assuming a bus with name 'ExistingBus' already exists in the database
            existing_bus = Bus(name="ExistingBus", capacity=50)
            db.session.add(existing_bus)
            db.session.commit()

        with app.test_request_context():
            form = createBusForm(name="ExistingBus", capacity="50")
            self.assertFalse(form.validate())
            self.assertIn('Bus name already exists.', form.name.errors)

if __name__ == '__main__':
    unittest.main()