from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()


class Guest(db.Model, SerializerMixin):
    __tablename__ = 'guests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(200))
    lname = db.Column(db.String(200))
    email = db.Column(db.String(65), unique=True)
    password = db.Column(db.String(255))

    bookings = db.relationship('Booking', backref='guest', lazy=True)
    reviews = db.relationship('Review', backref='guest', lazy=True)

    
class Property(db.Model, SerializerMixin):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(300))
    price = db.Column(db.Float)
    amenities = db.Column(db.String(300))
    status = db.Column(db.Boolean())
    images= db.Column(db.String(1000))

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    reviews = db.relationship('Review', backref='property', lazy=True)
    booking = db.relationship('Booking', uselist=False, backref='property', lazy=True)

class Booking(db.Model, SerializerMixin):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    checkOutDate = db.Column(db.String(45))
    checkInDate = db.Column(db.String(45))
    bookingDate = db.Column(db.String(45))
    price = db.Column(db.Float)
    paymentStatus = db.Column(db.Integer)

    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False, unique=True)



class Reviews(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    date = db.Column(db.String(45))

    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)

class Admin(db.Model, SerializerMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(65))
    password = db.Column(db.String(255))

    properties = db.relationship('Property', backref='admin', lazy=True)