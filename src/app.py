"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Database configuration
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
MIGRATE = Migrate(app, db)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoint for getting all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# List all favorites of the current user (assuming user ID = 1 for demonstration)
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_favorites = Favorite.query.filter_by(user_id=1).all()  # Static user ID for demo
    return jsonify([favorite.serialize() for favorite in user_favorites]), 200

# Add a new favorite planet for the current user
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    new_favorite = Favorite(user_id=1, planet_id=planet_id)  # Static user ID for demo
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

# Add a new favorite character for the current user
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    new_favorite = Favorite(user_id=1, character_id=people_id)  # Static user ID for demo
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

# Delete a favorite planet
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(user_id=1, planet_id=planet_id).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet deleted'}), 200

# Delete a favorite character
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    favorite = Favorite.query.filter_by(user_id=1, character_id=people_id).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite character deleted'}), 200

# Endpoint for getting all planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# Endpoint for getting a single planet by ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200

# Endpoint for getting all characters
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

# Endpoint for getting a single character by ID
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get_or_404(character_id)
    return jsonify(character.serialize()), 200

# Create a new planet
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    planet = Planet(
        name=data.get('name'),
        diameter=data.get('diameter'),
        climate=data.get('climate')
    )
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201

# Update an existing planet
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    data = request.get_json()
    planet.name = data.get('name', planet.name)
    planet.diameter = data.get('diameter', planet.diameter)
    planet.climate = data.get('climate', planet.climate)
    db.session.commit()
    return jsonify(planet.serialize()), 200

# Delete an existing planet
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted"}), 200

# Create a new character
@app.route('/characters', methods=['POST'])
def create_character():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    character = Character(
        name=data.get('name'),
        species=data.get('species'),
        gender=data.get('gender')
    )
    db.session.add(character)
    db.session.commit()
    return jsonify(character.serialize()), 201

# Update an existing character
@app.route('/characters/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    character = Character.query.get_or_404(character_id)
    data = request.get_json()
    character.name = data.get('name', character.name)
    character.species = data.get('species', character.species)
    character.gender = data.get('gender', character.gender)
    db.session.commit()
    return jsonify(character.serialize()), 200

# Delete an existing character
@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get_or_404(character_id)
    db.session.delete(character)
    db.session.commit()
    return jsonify({"message": "Character deleted"}), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
