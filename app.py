from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db, Flight, Passenger
from flask_migrate import Migrate
from flask_restful import Api, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'  # set the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
api = Api(app)
migrate = Migrate(app, db)

# Resources
class FlightResource(Resource):
    def post(self):
        data = request.get_json()
        flight = Flight(
            flight_name=data.get('flight_name'),
            destination=data.get('destination')
        )
        db.session.add(flight)
        db.session.commit()
        return {'message': 'Flight created', 'flight_id': flight.id}, 201
    
    def get(self, flight_id=None):
        if flight_id:
            flight = Flight.query.get(flight_id)
            if not flight:
                return {'message': 'Flight not found'}, 404
            return flight.to_dict(), 200
        else:
            flights = Flight.query.all()
            return [flight.to_dict() for flight in flights], 200
        
    def put(self, flight_id):
        flight = Flight.query.get(flight_id)
        if not flight:
            return {'message': 'Flight not found'}, 404
        data = request.get_json()
        flight.flight_name = data.get('flight_name', flight.flight_name)
        flight.destination = data.get('destination', flight.destination)
        db.session.commit()
        return {'message': 'Flight updated'}, 200
    

class PassengerResource(Resource):
    def post(self):
        data = request.get_json()

        flight_id = data.get('flight_id')
        flight = Flight.query.filter_by(id=flight_id).first()

        if not flight:
            return {'message': 'Flight not found'}, 404

        passenger = Passenger(
            name=data.get('name'), 
            email=data.get('email'), 
            flight=flight,
        )

        db.session.add(passenger)
        db.session.commit()

        return passenger.to_dict(), 201

    def get(self, passenger_id=None):
        if passenger_id:
            passenger = Passenger.query.get(passenger_id)
            if not passenger:
                return {'message': 'Passenger not found'}, 404
            return passenger.to_dict()
        else:
            passengers = Passenger.query.filter_by(deleted=False).all()
            return [passenger.to_dict() for passenger in passengers]

    def put(self, passenger_id):
        passenger = Passenger.query.get(passenger_id)
        if not passenger:
            return {'message': 'Passenger not found'}, 404

        data = request.get_json()
        passenger.name = data.get('name', passenger.name)
        passenger.email = data.get('email', passenger.email)
        passenger.checked_in = data.get('checked_in', passenger.checked_in)

        db.session.commit()
        return passenger.to_dict()

class PassengerSoftDeleteResource(Resource):
    def delete(self, passenger_id):
        passenger = Passenger.query.get(passenger_id)
        if passenger is None:
            return {'message': 'Passenger not found'}, 404
        passenger.soft_delete()
        db.session.commit()
        return {'message': 'Passenger soft deleted'}

class PassengerRestoreResource(Resource):
    def patch(self, passenger_id):
        passenger = Passenger.query.get(passenger_id)
        if passenger is None:
            return {'message': 'Passenger not found'}, 404
        passenger.restore()
        db.session.commit()
        return {'message': 'Passenger restored'}
    



# Add resources to the API
api.add_resource(FlightResource, '/flights' , '/flights/<int:flight_id>')
api.add_resource(PassengerResource, '/passengers', '/passengers/<int:passenger_id>')
api.add_resource(PassengerSoftDeleteResource, '/passengers/<int:passenger_id>/soft_delete')
api.add_resource(PassengerRestoreResource, '/passengers/<int:passenger_id>/restore')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
