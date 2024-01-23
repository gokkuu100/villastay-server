from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import CheckConstraint
import base64

db = SQLAlchemy()


class Guest(db.Model, SerializerMixin):
    __tablename__ = 'guests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(200))
    lname = db.Column(db.String(200))
    email = db.Column(db.String(65), unique=True)
    password = db.Column(db.String(255))

    bookings = db.relationship('Booking', backref='guest', lazy=True)
    reviews = db.relationship('Reviews', backref='guest', lazy=True)

    
class Property(db.Model, SerializerMixin):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(300))
    price = db.Column(db.Float)
    bedroom = db.Column(db.Integer)
    bathroom = db.Column(db.Integer)
    status = db.Column(db.Boolean)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

    amenities = db.relationship('Amenity', backref='property', lazy=True)
    images= db.relationship('Image', backref='property', lazy=True)
    reviews = db.relationship('Reviews', backref='property', lazy=True)
    booking = db.relationship('Booking', uselist=False, backref='property', lazy=True)


    def save_images(self, images):
        for image in images:
            image_data = image.read()
            new_image = Image(data=image_data)
            self.images.append(new_image)

    def save_amenities(self, amenities):
        for amenity_name in amenities:
            amenity = Amenity(name=amenity_name)
            self.amenities.append(amenity)

    def reviews_count(self):
        return Reviews.query.filter_by(property_id=self.id).count()

class Amenity(db.Model, SerializerMixin):
    __tablename__ = "amenities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"))


class Image(db.Model, SerializerMixin):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary(length=16277215))
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"))

class Booking(db.Model, SerializerMixin):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    checkOutDate = db.Column(db.String(45))
    checkInDate = db.Column(db.String(45))
    bookingDate = db.Column(db.String(45))
    price = db.Column(db.Float)
    paymentStatus = db.Column(db.Boolean)

    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False, unique=True)

class Reviews(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    rating = db.Column(db.Integer, CheckConstraint('rating >= 0 AND rating <= 5'))
    date = db.Column(db.String(45))

    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)

class Admin(db.Model, SerializerMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(65))
    password = db.Column(db.String(255))

    properties = db.relationship('Property', backref='admin', lazy=True)

