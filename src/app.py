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
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    usuarios=User.query.all()
    if usuarios == []:
        return jsonify ({"msg":"No existen usuarios"}), 404
    response_body = [item.serialize() for item in usuarios]
    
    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user=User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify ({"msg":"No existen el usuario"}), 404
    return jsonify(user.serialize()), 200

@app.route('/character', methods=['GET'])
def get_character():
    personajes=Character.query.all()
    if personajes == []:
        return jsonify ({"msg":"No existen personajes"}), 404
    response_body = [item.serialize() for item in personajes]
    
    return jsonify(response_body), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character_id(character_id):
    personaje=Character.query.filter_by(id=character_id).first()
    if personaje is None:
        return jsonify ({"msg":"No existe el personaje"}), 404
    return jsonify(personaje.serialize()), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    planetas=Planet.query.all()
    if planetas == []:
        return jsonify ({"msg":"No existen planetas"}), 404
    response_body = [item.serialize() for item in planetas]
    
    return jsonify(response_body), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planetas=Planet.query.filter_by(id=planet_id).first()
    if planetas is None:
        return jsonify ({"msg":"No existe el planeta"}), 404
    return jsonify(planetas.serialize()), 200

@app.route('/favorite', methods=['GET'])
def get_favorite():
    favoritos=Favorite.query.all()
    if favoritos == []:
        return jsonify ({"msg":"No existen favoritos"}), 404
    response_body = [item.serialize() for item in favoritos]
    
    return jsonify(response_body), 200

@app.route('/favorite/<int:favorite_id>', methods=['GET'])
def get_favorite_id(favorite_id):
    favoritos=Favorite.query.filter_by(id=favorite_id).first()
    if favoritos is None:
        return jsonify ({"msg":"No existe favorito"}), 404
    return jsonify(favoritos.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    body = request.json
    email = body.get ("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify ({"msg":"No existe el usuario"}), 404
    
    planeta = Planet.query.get(planet_id)
    if planeta == None:
        return jsonify ({"msg":"No existe el planeta"}), 404
    
    new_favorite = Favorite ()
    new_favorite.user = user
    new_favorite.planet = planeta
    db.session.add (new_favorite)
    db.session.commit()

    return jsonify (new_favorite.serialize()), 200


@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def post_favorite_character(character_id):
    body = request.json
    email = body.get ("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify ({"msg":"No existe el usuario"}), 404
    
    personaje = Character.query.get(character_id)
    if personaje == None:
        return jsonify ({"msg":"No existe el personaje"}), 404
    
    new_favorite = Favorite ()
    new_favorite.user = user
    new_favorite.character = personaje
    db.session.add (new_favorite)
    db.session.commit ()

    return jsonify (new_favorite.serialize()), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.json
    email = body.get ("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify ({"msg":"No existe el usuario"}), 404
    
    planeta = Planet.query.get(planet_id)
    if planeta == None:
        return jsonify ({"msg":"No existe el planeta"}), 404
    
    favorite_delete = Favorite.query.filter_by(user_id=user.id,planet_id=planeta.id).first()
    if favorite_delete == None:
        return jsonify ({"msg":"No existe el favorito"}),404
    db.session.delete(favorite_delete)
    db.session.commit()

    return jsonify ({"msg":"Eliminado con éxito"}), 200


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    body = request.json
    email = body.get ("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify ({"msg":"No existe el usuario"}), 404
    
    personaje = Character.query.get(character_id)
    if personaje == None:
        return jsonify ({"msg":"No existe el planeta"}), 404
    
    favorite_delete = Favorite.query.filter_by(user_id=user.id,character_id=personaje.id).first()
    if favorite_delete == None:
        return jsonify ({"msg":"No existe el favorito"}),404
    db.session.delete(favorite_delete)
    db.session.commit()

    return jsonify ({"msg":"Eliminado con éxito"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
