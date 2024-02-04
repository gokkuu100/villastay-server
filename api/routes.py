import os
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import Admin, Guest, Property, Image, Booking, Reviews
from datetime import datetime
import base64
import requests
import json

ns = Namespace("villas", description="CRUD endpoints")


@ns.route("/home")
class Hello(Resource):
    def get(self):
        return "Welcome to the first route"

# admin signup route
@ns.route("/admin/signup")
class Signup(Resource):
    def post(self):
        from app import bcrypt, db
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return make_response(jsonify(error="Invalid data request"), 400)
            
            # quesy if admin exists
            existing_user = Admin.query.filter_by(email=email).first()
            if existing_user:
                return make_response(jsonify({"error": "User with this email already exists"}), 409)

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = Admin(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return make_response(jsonify({"message": "User created successfully", "id": new_user.id, "name": new_user.email }))

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

# guest signup route
@ns.route("/guest/signup")
class GuestSignup(Resource):
    def post(self):
        from app import bcrypt, db
        try:
            data = request.get_json()
            fname = data.get('fname')
            lname = data.get('lname')
            email = data.get('email')
            password = data.get('password')

            if not fname or not lname or not email or not password:
                return make_response(jsonify(error="Invalid data request"), 400)
            
            # query if guest exists
            existing_user = Guest.query.filter_by(email=email).first()
            if existing_user:
                return make_response(jsonify({"error": "User with this email already exists"}), 409)

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = Guest(fname=fname, lname=lname, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return make_response(jsonify({"message": "Guest created successfully", "id": new_user.id, "name": new_user.fname}))

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

# signin route
@ns.route("/signin")
class SignIn(Resource):
    def post(self):
        from app import db, bcrypt
        try:
            data=request.get_json()
            email=data.get('email')
            password=data.get('password')

            if not email or not password:
                return make_response(jsonify(error="Invalid data request"), 400)
            
            # checks if user is admin
            admin_user = Admin.query.filter_by(email=email).first()
            if admin_user and bcrypt.check_password_hash(admin_user.password, password):
                token=create_access_token(identity={"id":admin_user.id, "role":"admin"})
                return make_response(jsonify({"token": token, "role": "admin", "id": admin_user.id}), 201)
            
            # checks if user is guest
            guest_user = Guest.query.filter_by(email=email).first()
            if guest_user and bcrypt.check_password_hash(guest_user.password, password):
                token=create_access_token(identity={"id":guest_user.id, "role": "guest"})
                return make_response(jsonify({"token": token, "role": "guest", "id": guest_user.id}), 201)
            
            return make_response(jsonify({"error": "Email or password incorrect"}), 401)
        except Exception as e:
            return make_response(jsonify({"error":str(e)}), 500)
        
# create villa
@ns.route("/create")
class CreateProperty(Resource):
    def post(self):
        from app import db, app
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = {key: request.form[key] for key in request.form}

            app.logger.info("Received data:", data)

            title = data.get('title')
            description = data.get('description')
            location = data.get('location')
            price = data.get('price')
            amenities = data.get('amenities')
            if isinstance(amenities, str):
                amenities = amenities.split(',')
            bedroom = data.get('bedroom')
            bathroom = data.get('bathroom')
            status = bool(data.get('status'))
            admin_id = data.get('admin_id')

            newVilla = Property(
                title=title,
                description=description,
                location=location,
                price=price,
                bedroom=bedroom,
                bathroom=bathroom,
                status=status,
                admin_id=admin_id
            )

            # Save amenities correctly
            newVilla.save_amenities(amenities)

            # Save the property instance
            db.session.add(newVilla)
            db.session.commit()

            # Save images
            images = request.files.getlist("images")
            for image in images:
                if image.filename != '':
                    image_data = image.read()
                    new_image = Image(data=image_data, property_id=newVilla.id)
                    db.session.add(new_image)

            db.session.commit()

            return make_response(jsonify({'message': 'New Villa created successfully!'}), 201)
        except Exception as error:
            print(error)
            app.logger.error(f"Error creating new property: {str(error)}")
            
            db.session.rollback()
            return make_response(jsonify({'message': 'Error creating new Villa.'}), 500)

        
# read all villa
@ns.route("/listings")
class AllVillas(Resource):
    def get(self):
        try:
            location =request.args.get('location')
            price = request.args.get('price')
            rating = request.args.get('rating')

            properties_query = Property.query

            if location is not None and location != '':
                properties_query = properties_query.filter(Property.location.ilike(f"{location}"))
            if price is not None and price != '':
                properties_query = properties_query.filter(Property.price < price)
            if rating is not None and rating != '':
                properties_query = properties_query.filter(Property.reviews.any(Reviews.rating <= rating))

            properties = properties_query.all()

            property_list = []
            for property in properties:
                amenities = [amenity.name for amenity in property.amenities]

                property_data = {
                    "id": property.id,
                    "title": property.title,
                    "location": property.location,
                    "price": property.price,
                    "description": property.description,
                    "amenities": amenities,
                    "status": property.status,
                    "images": []
                }
                images = Image.query.filter_by(property_id=property.id).all()
                for image in images:
                    image_data = {
                        "id": image.id,
                        "data": base64.b64encode(image.data).decode("utf-8")
                    }
                    property_data["images"].append(image_data)

                property_list.append(property_data)
            if not property_list:
                return make_response(jsonify({"message": "No properties were found"}))
            
            return make_response(jsonify(property_list), 200)
        except Exception as e:
            print(f"Error fetching property listings: {str(e)}")
            return make_response(jsonify({"error": str(e)}), 500)
        
# get specific villa
@ns.route("/listings/<int:id>")
class SingleVilla(Resource):
    def get(self, id):
        try:
            property = Property.query.get(id)
            

            if not property:
                return make_response(jsonify({"error":"Property does not exist"}), 404)
            
            amenities = [amenity.name for amenity in property.amenities]

            data = {
                "id": property.id,
                "title": property.title,
                "location": property.location,
                "price": property.price,
                "description": property.description,
                "bathroom": property.bathroom,
                "bedroom": property.bedroom,
                "amenities": amenities,
                "status": property.status,
                "images": [],
                "reviews": []
            }
            # fetch images
            images = Image.query.filter_by(property_id=property.id).all()
            for image in images:
                image_data = {
                    "id": image.id,
                    "data": base64.b64encode(image.data).decode("utf-8")
                }
                data['images'].append(image_data)

            # fetch reviews
            reviews = Reviews.query.filter_by(property_id=property.id).all()
            for review in reviews:
                review_data = {
                    "id": review.id,
                    "comment": review.comment,
                    "rating": review.rating,
                    "date": review.date,
                    "guest": {
                        "id": review.guest.id,
                        "fname": review.guest.fname,
                    }
                }
                data['reviews'].append(review_data)

            return make_response(jsonify(data), 200)
        except Exception as e:
            print(f"Error getting single listing: {str(e)}")
            return make_response(jsonify({"error": str(e)}), 500)
            
            
@ns.route("/booking")
class BookingResource(Resource):
    def post(self):
        try:
            from app import db, app
            data = request.get_json()
            checkOutDate = data.get("checkOutDate")
            checkInDate = data.get("checkInDate")
            bookingDate = data.get("bookingDate")
            price = data.get("price")
            paymentStatus = data.get("paymentStatus")
            guest_id=data.get("guest_id")
            property_id = data.get("property_id")

            newBooking = Booking (
                checkOutDate=checkOutDate,
                checkInDate=checkInDate,
                bookingDate=bookingDate,
                price=price,
                paymentStatus=paymentStatus,
                guest_id=guest_id,
                property_id=property_id
            )

            db.session.add(newBooking)
            db.session.commit()

            return make_response(jsonify({"Message": "Booking success"}), 200)
        except Exception as e:
            app.logger.error(f"Error creating new booking: {str(e)}")
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        
@ns.route("/review")
class ReviewResource(Resource):
    def post(self):
        try:
            from app import db, app
            data = request.get_json()
            comment = data.get("comment")
            rating = data.get("rating")
            date = datetime.now().strftime("%d-%m-%Y")
            guest_id = data.get("guest_id")
            property_id = data.get("property_id")

            newReview = Reviews (
                comment=comment,
                rating=rating,
                date=date,
                guest_id=guest_id,
                property_id=property_id
            )

            db.session.add(newReview)
            db.session.commit()

            return make_response(jsonify({"message": "review created successfully"}), 201)
        except Exception as e:
            app.logger.error(f"Error creating a new review: {str(e)}")
            db.session.rollback()
            return make_response(jsonify({"error": f"Failed to create the review: {str(e)}"}), 500)
        
@ns.route("/reviews")
class GetReviews(Resource):
    def get(self):
        try: 
            from app import db, app
            reviews = Reviews.query.all()
            reviews_data = []
            for review in reviews:
                review_data = {
                    "id": review.id,
                    "comment": review.comment,
                    "rating": review.rating,
                    "date": review.date,
                    "guest_id": review.guest_id,
                    "property_id": review.property_id,
                    "guest": {
                        "id": review.guest.id,
                        "fname": review.guest.fname,
                    }
                }
                reviews_data.append(review_data)
            return make_response(jsonify({"reviews": reviews_data}), 200)
        
        except Exception as e:
            app.logger.error(f"Error fetching reviews: {str(e)}")
            return make_response(jsonify({"error": f"Failed to fetch reviews: {str(e)}"}), 500)
        
@ns.route('/darajatoken')
class GetAccessToken(Resource):
    def get(self):
        consumer_key = "vlxIG7z3Y5pNrLF8LhFTFZ6GMQBAS16zLRvGkfo3LoqXY23y"
        consumer_secretKey = "Bwq5SPyaSQcKiAWZnIN7S3GJvzPxdOb1AWA9b7ux2OxIdZARA7wBW3G1NgSgBMrK"
        access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        headers = {'Content-Type': 'application/json'}
        auth = (consumer_key, consumer_secretKey)
        try:
            response = requests.get(access_token_url, headers=headers, auth=auth)
            result = response.json()
            access_token = result['access_token']
            return make_response(jsonify({"access_token": access_token}), 200) 
        except Exception as e:
            return make_response(jsonify({'message':'Error getting the Access Token.'+ str(e)}), 401)  

@ns.route('/stkpush')
class InitiateSTKPush(Resource):
    def post(self):
        access_token_resource = GetAccessToken()
        access_token_response = access_token_resource.get()

        if access_token_response.status_code == 200:
            access_token = access_token_response.get_json()['access_token']
            
            if access_token:
                amount = 1
                phone = "254746551520"
                passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
                business_short_code = "174379"
                process_request_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
                callback_url = "https://mydomain.com/pat"
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
                party_a = phone
                party_b = "174379"
                account_reference = "GokuLTD"
                transaction_desc = "stkpush_test"
                stk_push_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + access_token
                }
                stk_push_payload = {
                    'BusinessShortCode': business_short_code,
                    'Password':  password,
                    'Timestamp': timestamp,
                    'TransactionType': 'CustomerPayBillOnline',
                    'Amount': amount,
                    'PartyA':  party_a,
                    'PartyB': business_short_code,
                    'PhoneNumber': party_a,
                    'CallBackURL': callback_url,
                    'AccountReference': account_reference,
                    'TransactionDesc': transaction_desc
                }

                try:
                    response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                    response_data = response.json()
                    checkout_request_id = response_data['CheckoutRequestID']
                    response_code = response_data['ResponseCode']

                    if response_code == '0':
                        return jsonify({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                    else:
                        return make_response(jsonify({'error': 'STK push failed'}))
                except Exception as e:
                    return make_response(jsonify({'error': str(e)}))
            else:
                return make_response(jsonify({'error': 'Access token not available'}))
        else:
            return make_response(jsonify({'error': 'Failed to get access_token.'}))
