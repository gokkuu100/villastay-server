from flask_restx import Resource, Namespace
ns = Namespace("villas", description="CRUD endpoints")

@ns.route("/home")
class Hello(Resource):
    def get(self):
        return "Welcome to the first route"
    
