from flask import Flask, redirect, render_template, url_for, session, flash
from flask_bcrypt import Bcrypt
from forms import LoginForm, RegisterForm
import pymysql
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///busTicketBooking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set the secret key for CSRF protection
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# --------------------- Database Initialization | Header ---------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, default=1000)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Bus(db.Model):
    # busID, busName, capacity
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Bus {self.name}>'
    
class Booking(db.Model):
    # bookingID, userID, buID, destinationID, bookingDate, travelDate
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    travel_date = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Booking {self.id}>'
    
class Destination(db.Model):
    # destinationID, destinationName, distance
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Destination {self.name}>'
    
# --------------------- Database Initialization | Footer ---------------------
#
#
@app.route('/')
@app.route('/index')
def login_page():
    form = LoginForm()
    return render_template('login.html', form=form)

# login post
@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session['logged_in'] = True
                session['username'] = username
                if user.is_admin:
                    return redirect('/admin-dashboard')
                else:
                    return redirect('/user-dashboard')
            else:
                flash('Invalid username or password')
                return redirect(url_for('login_page'))
        except pymysql.MySQLError as e:
            app.logger.error(f"MySQL error during login: {e}")
            flash('A database error occurred during login. Please try again.', 'error')
        except Exception as e:
            app.logger.error(f"Error during login: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    else:
        flash('Form validation failed. Please check your inputs.')
    return render_template('login.html', form=form)

# logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out successfully')
    return redirect(url_for('login_page'))

# register page
@app.route('/register-page')
def register_page():
    form = RegisterForm()
    return render_template('register.html', form=form)

# register post
@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Please login.')
        return redirect(url_for('login_page'))
    else:
        flash('Form validation failed. Please check your inputs.')
    return render_template('register.html', form=form)

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/user-dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)