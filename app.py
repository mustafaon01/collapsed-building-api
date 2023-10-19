from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)

# PostgreSQL için config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:password@db:5432/buildings_db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    street = db.Column(db.String(70))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "street": self.street,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

class BuildingSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=lambda n: len(n) <= 50)
    street = fields.Str(required=True, validate=lambda s: len(s) <= 70)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

building_schema = BuildingSchema()


@app.route('/buildings/getAllBuildings', methods=['GET'])
def get_all_buildings():
    buildings = Building.query.all()
    return jsonify([bldg.as_dict() for bldg in buildings]), 200

@app.route('/buildings/postBuilding', methods=['POST'])
def post_building():
    try:
        building_data = building_schema.load(request.json)
        new_building = Building(**building_data)
        db.session.add(new_building)
        db.session.commit()
        return jsonify({"message": "success"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/buildings/deleteBuilding/<int:id>', methods=['DELETE'])
def delete_building(id):
    building = Building.query.get(id)
    if building:
        db.session.delete(building)
        db.session.commit()
        return jsonify({"message": "Silindi"}), 200
    return jsonify({"message": "Silinmedi"}), 404

@app.route('/buildings/updateBuilding/<int:id>', methods=['PUT'])
def update_building(id):
    try:
        building_data = building_schema.load(request.json)
        building = Building.query.get(id)
        if building:
            for key, value in building_data.items():
                setattr(building, key, value)
            db.session.commit()
            return jsonify({"message": "Güncellendi"}), 200
        return jsonify({"message": "Bina bulunamadı"}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
