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

from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

CURRENT_USER_ID = 1

@app.route("/people", methods=["GET"])
def get_people():
    people = Character.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "eye_color": p.eye_color}
        for p in people
    ]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_single_person(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    return jsonify({
        "id": person.id,
        "name": person.name,
        "height": person.height,
        "mass": person.mass,
        "hair_color": person.hair_color,
        "eye_color": person.eye_color
    }), 200


@app.route("/people", methods=["POST"])
def create_person():
    body = request.get_json()
    if not body or "name" not in body:
        return jsonify({"msg": "Missing name"}), 400

    person = Character(
        name=body["name"],
        height=body.get("height"),
        mass=body.get("mass"),
        hair_color=body.get("hair_color"),
        eye_color=body.get("eye_color")
    )

    db.session.add(person)
    db.session.commit()
    return jsonify({"msg": "Person created", "id": person.id}), 201


@app.route("/people/<int:people_id>", methods=["PUT"])
def update_person(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    body = request.get_json()
    person.name = body.get("name", person.name)
    person.height = body.get("height", person.height)
    person.mass = body.get("mass", person.mass)
    person.hair_color = body.get("hair_color", person.hair_color)
    person.eye_color = body.get("eye_color", person.eye_color)

    db.session.commit()
    return jsonify({"msg": "Person updated"}), 200


@app.route("/people/<int:people_id>", methods=["DELETE"])
def delete_person(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({"msg": "Person deleted"}), 200


@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "climate": p.climate}
        for p in planets
    ]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify({
        "id": planet.id,
        "name": planet.name,
        "diameter": planet.diameter,
        "climate": planet.climate,
        "population": planet.population
    }), 200


@app.route("/planets", methods=["POST"])
def create_planet():
    body = request.get_json()
    if not body or "name" not in body:
        return jsonify({"msg": "Missing name"}), 400

    planet = Planet(
        name=body["name"],
        diameter=body.get("diameter"),
        population=body.get("population"),
        climate=body.get("climate")
    )

    db.session.add(planet)
    db.session.commit()
    return jsonify({"msg": "Planet created", "id": planet.id}), 201


@app.route("/planets/<int:planet_id>", methods=["PUT"])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    body = request.get_json()
    planet.name = body.get("name", planet.name)
    planet.diameter = body.get("diameter", planet.diameter)
    planet.population = body.get("population", planet.population)
    planet.climate = body.get("climate", planet.climate)

    db.session.commit()
    return jsonify({"msg": "Planet updated"}), 200


@app.route("/planets/<int:planet_id>", methods=["DELETE"])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = User.query.get(CURRENT_USER_ID)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify([f.serialize() for f in user.favorites]), 200


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    favorite = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"}), 201


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    favorite = Favorite(user_id=CURRENT_USER_ID, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites"}), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    ).first()

    if not favorite:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet removed from favorites"}), 200


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        character_id=people_id
    ).first()

    if not favorite:
        return jsonify({"msg": "Favorite person not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Person removed from favorites"}), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)