from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()


class Guest(db.Model, SerializerMixin):
    __tablename__ = 'guests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(200))
    lname = db.Column(db.String(200))
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String())

class Property(db.Model, SerializerMixin):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(300))
    price = db.Column(db.Float)
    amenities = db.Column(db.String())
    status = db.Column(db.Boolean())
    images= db.Column(db)

class Booking(db.Model, SerializerMixin):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    checkOutDate = db.Column(db.String())
    checkInDate = db.Column(db.String())
    bookingDate = db.Column(db.String())
    price = db.Column(db.Float)
    paymentStatus = db.Column(db.Integer)

class Reviews(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    date = db.Column(db.String)

class Admin(db.Model, SerializerMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())