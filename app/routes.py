from flask import jsonify, request, make_response, Response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import text
from app import app, db
from app.models import Users, Recipes, Recipe_rating, Ingredient
import requests
import datetime
import json

@app.route("/")
def hello_world():
    return jsonify({"message":"welcome to the food app"})


@app.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()
    
    first_name = body['first_name']
    last_name = body['last_name']
    email = body['email']
    password = body['password']
    
    user_exist = db.session.query(Users.id).filter_by(email=email).first() is not None
    
    if user_exist:
        return jsonify({"message":'This already email exist!'})
    else:
        url = 'https://api.hunter.io/v2/email-verifier?email=' + email + '&api_key=6024e2db93619204bb42e31bad0626e66162328a'
    
        data = requests.get(url)
        data = data.json()
        if data['data']['status'] == 'invalid':
            return jsonify({"message":'Email address is invalid!'})
        else:
            user =  Users(first_name, last_name, email, password)
            user.hash_password()
            db.session.add(user)
            db.session.commit()
            id = user.id
            
            return jsonify({'id': str(id), 'status': 200})
        
        
@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    user = Users.query.filter_by(email=body['email']).first_or_404()
    authorized = user.check_password(body['password'])
    
    if not authorized:
            return jsonify({'error': 'Email or password invalid'})
    
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=user.id, expires_delta=expires)
    
    return jsonify({'token': access_token}, 200)
    
@app.route("/recipe", methods=["POST"])
@jwt_required()  
def create_recipe():
    body = request.get_json()
    
    name = body['name']
    text = body['text']
    
    current_user = get_jwt_identity()
    
    recipe =  Recipes(name, text, current_user)
    db.session.add(recipe)
    db.session.commit()
    id = recipe.id
    
    return jsonify({'id': str(id), 'status': 200})
    
    

@app.route("/recipes", methods=["GET"])
@jwt_required()  
def recipes():
    # select recipes with average score
    sql = text('SELECT recipes.name, AVG(recipe_rating.score) as average_score FROM recipe_rating ' 
            'INNER JOIN recipes ON recipe_rating.recipe_id = recipes.id '
            'GROUP BY recipe_id ')
            
    result = db.session.execute(sql)
    
    return jsonify({'result': [dict(row) for row in result]})


@app.route("/my-recipes", methods=["GET"])
@jwt_required()  
def my_recipes():
    current_user = get_jwt_identity()
    recipes = Recipes.query.filter_by(user_id=get_jwt_identity())
    
    #return json.dumps(recipe_schema.dump(recipes))
    return []

@app.route("/rate-recipe", methods=["POST"])
@jwt_required()  
def rate_recipe():
    body = request.get_json()
    
    recipe_id = body['recipe_id']
    score = body['score']
    current_user = get_jwt_identity()
    
    recipe = Recipes.query.filter_by(id=recipe_id).first()
    
    if recipe.user_id == current_user:
        return jsonify({'error': 'You cannot rate your own recipe!'})
    else:
        recipe_rating =  Recipe_rating(recipe_id, current_user, score)
        db.session.add(recipe_rating)
        db.session.commit()
        id = recipe_rating.id

        return jsonify({'id': str(id)})
    

@app.route("/ingredient", methods=["POST"])
@jwt_required()  
def create_ingredient():
    body = request.get_json()
    
    name = body['name']
    
    ingredient =  Ingredient(name)
    db.session.add(ingredient)
    db.session.commit()
    id = ingredient.id
    
    return jsonify({'id': str(id)})

@app.route("/ingredient/most-used", methods=["GET"])
@jwt_required()  
def most_used():
    
    # select top 5 used ingredients
    sql = text('SELECT ingredient.name, COUNT(ingredient_id) as total from recipe_ingredient ' 
            'INNER JOIN ingredient ON recipe_ingredient.ingredient_id = ingredient.id '
            'GROUP BY ingredient_id '
            'ORDER BY total DESC ' 
            'LIMIT 5')
    result = db.session.execute(sql)
    
    return jsonify({'result': [dict(row) for row in result]})


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    
    return jsonify(logged_in_as=current_user), 200
