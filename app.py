from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from api.routes import ns as routes_ns
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://goku:Goku100!@localhost/villaDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CORS(app, support_credentials=True)
migrate = Migrate(app, db)
api = Api(app, title="Villa API", description="List of available APIs for villa-stay application", prefix='/api')

api.add_namespace(routes_ns)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
