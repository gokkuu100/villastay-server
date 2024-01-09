import os
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import Admin, Guest, Property

ns = Namespace("villas", description="CRUD endpoints")

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    # Implement a logic to generate a unique filename
    # You can use a combination of timestamps, random strings, or other strategies
    return 'unique_filename.jpg'

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
                return make_response(jsonify({"token": token, "role": "admin", "id": admin_user.id}))
            
            # checks if user is guest
            guest_user = Guest.query.filter_by(email=email).first()
            if guest_user and bcrypt.check_password_hash(guest_user.password, password):
                token=create_access_token(identity={"id":guest_user.id, "role": "guest"})
                return make_response(jsonify({"token": token, "role": "guest", "id": guest_user.id}))
            
            return make_response(jsonify({"Email or password incorrect"}), 401)
        except Exception as e:
            return make_response(jsonify({"error":str(e)}), 500)
        
# create villa
@ns.route("/create")
class CreateProperty(Resource):
    def post(self):
        from app import db, app
        try:
            data = request.get_json()
            title = data.get("title")
            description = data.get("description")
            location = data.get("location")
            price = data.get("price")
            amenities = data.get("amenities")
            status = data.get("status")
            images = data.get("images")
            ownerID = data.get("admin_id")

            # Save images to the file system
            image_paths = []
            for img in images:
                if allowed_file(img.filename):
                    filename = generate_unique_filename(img.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    img.save(file_path)
                    image_paths.append(file_path)

            newProperty = Property(
                title=title,
                description=description,
                location=location,
                price=price,
                amenities=amenities,
                status=status,
                images=image_paths,  # Save the file paths to the images
                admin_id=ownerID
            )
            db.session.add(newProperty)
            db.session.commit()
            return make_response(jsonify({'message': 'New property created!'}), 201)
        except Exception as e:
            return make_response(jsonify({'error':'Error creating new property:'+ str(e)}), 500)

