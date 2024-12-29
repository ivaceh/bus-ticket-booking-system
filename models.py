from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Bus {self.name}>'
    
class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    travel_date = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    bus = db.relationship('Bus', backref=db.backref('bookings', lazy=True))
    destination = db.relationship('Destination', backref=db.backref('bookings', lazy=True))
    
    def __repr__(self):
        return f'<Booking {self.booking_id}>'
    
class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Destination {self.name}>'
