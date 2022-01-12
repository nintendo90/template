from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pcStore.db"
api = Api(app)
db = SQLAlchemy(app)


class Deals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pc_id = db.Column(db.Integer, db.ForeignKey('pc.id'), nullable='False')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable='False')

    customer = db.relationship("Customer", backref="deals", lazy=True)
    computer = db.relationship("Pc", backref="deals", lazy=True)

    def __repr__(self):
        return f"Deals('{self.customer_id}', '{self.pc_id}')"

class Pc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String(100), nullable=False)
    ram = db.Column(db.String(100), nullable=False)
    ssd = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float(10, 2), nullable=False)

    def __repr__(self):
        return f"Pc('{self.cpu}')"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Customer('{self.name}')"

db.create_all() #run only once

pc_post_args = reqparse.RequestParser()
pc_post_args.add_argument("cpu", type=str, help="Cpu of the pc", required=True)
pc_post_args.add_argument("ram", type=str, help="Ram of the pc", required=True)
pc_post_args.add_argument("ssd", type=str, help="Ssd of the pc", required=True)
pc_post_args.add_argument("price", type=float, help="Price of the pc", required=True)

customer_post_args = reqparse.RequestParser()
customer_post_args.add_argument('name',type=str,help='enter name',required=True)
customer_post_args.add_argument('surname',type=str,help='enter surname',required=True)
customer_post_args.add_argument('email',type=str,help='Enter email',required=True)

deals_post_args = reqparse.RequestParser()
deals_post_args.add_argument('pc_id', type=int, help="Id of pc", required=True)

pc_fields = {
    'id': fields.Integer,
    'cpu': fields.String,
    'ram': fields.String,
    'ssd': fields.String,
    'price': fields.Float
}

customer_fields = {  
    'id' : fields.Integer,
    'name' : fields.String,
    'surname' : fields.String,
    'email' : fields.String
}

deals_field = {
    "customer_id": fields.Integer,
    "pc_id": fields.Integer
}

class PcResource(Resource):
    @marshal_with(pc_fields)
    def get(self, pc_id):
        result = Pc.query.filter_by(id=pc_id).first_or_404(description="PC with provided id is not found")
        return result
    
    @marshal_with(pc_fields)
    def post(self, pc_id):
        if Pc.query.get(pc_id):
            abort(409, message="The pc with provided id is already exists")
        args = pc_post_args.parse_args()
        pc = Pc(id=pc_id, cpu=args['cpu'], ram=args['ram'], ssd=args['ssd'], price=args['price'])
        db.session.add(pc)
        db.session.commit()
        return pc, 201

    def delete(self, pc_id):
        result = Pc.query.filter_by(id=pc_id).first_or_404(description="PC with provided id is not found")
        db.session.delete(result)
        db.session.commit()
        return "", 204

class CustomerResource(Resource):
    @marshal_with(customer_fields)
    def get(self, customer_id):
        result = Customer.query.filter_by(id=customer_id).first_or_404(description="Customer does not exist")
        return result

    @marshal_with(customer_fields)
    def post(self, customer_id):
        if Customer.query.get(customer_id):
            abort(409, message="The customer with provided id is already exists")
        args = customer_post_args.parse_args()
        customer = Customer(id=customer_id, name=args['name'], surname=args['surname'], email=args['email'])
        db.session.add(customer)
        db.session.commit()
        return customer, 201

    def delete(self, customer_id):
        result = Customer.query.filter_by(id=customer_id).first_or_404(description="Customer does not exist")
        db.session.delete(result)
        db.session.commit()
        return "", 204

class DealsResource(Resource):
    @marshal_with(deals_field)
    def get(self, customer_id):
        customer = Customer.query.filter_by(id=customer_id).first_or_404(description="There is not such customer")
        deal = Deals.query.filter_by(customer_id=customer_id).all()
        if deal == []:
            abort(404, message="Deal does not exist")
        return deal

    @marshal_with(deals_field)
    def post(self, customer_id):
        args = deals_post_args.parse_args()
        customer1 = Customer.query.filter_by(id=customer_id).first_or_404(description="There is not such customer")
        pc1 = Pc.query.filter_by(id=args['pc_id']).first_or_404(description="There is not such pc")
        deal = Deals(customer=customer1, computer=pc1)
        db.session.add(deal)
        db.session.commit()
        return deal, 201

class ShowClientByPcResource(Resource):
    @marshal_with(customer_fields)
    def get(self, pc_id):
        deals = Deals.query.filter_by(pc_id=pc_id).all()
        if deals == []:
            abort(404, message= "Deal does not exist")
        customers = []
        for deal in deals:
            customers.append(deal.customer)
        return customers

class BestBuyerResource(Resource):
    @marshal_with(deals_field)
    def get(self):
        deals = Deals.query.all()
        result = {}
        for deal in deals:
            customer_id = deal.customer_id
            money = deal.computer.price
            result[customer_id] = str(money)
            for res in result:
                if res == customer_id:
                    result[res] =  str(float(money) + float(result[res]))
        
        return deals



api.add_resource(PcResource, "/pc/<int:pc_id>")
api.add_resource(CustomerResource, "/customer/<int:customer_id>")
api.add_resource(DealsResource, "/deals/<int:customer_id>")
api.add_resource(ShowClientByPcResource, "/showclient/<int:pc_id>")
api.add_resource(BestBuyerResource, "/bestbuyer/")

if __name__ == "__main__":
    app.run(debug=True)