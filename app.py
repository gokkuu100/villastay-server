from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from api.routes import ns as routes_ns
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import db
import os

# loads env variables
load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://goku:Goku100!@localhost/villaDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 10240* 1024
app.config['ALLOWED_ExTENSIONS'] = ALLOWED_EXTENSIONS
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


CORS(app, support_credentials=True)
api = Api(app, title="Villa API", description="List of available APIs for villa-stay application", prefix='/api')

api.add_namespace(routes_ns)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
