from flask import jsonify, request, make_response, Response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import text
from app import app, db
from app.models import Users, Recipes, Recipe_rating, Ingredient
from app.schemas import SignUpSchema, LoginSchema, IngredientSchema,RecipeSchema, RecipeRatingSchema
from marshmallow import ValidationError
import requests
import datetime
import clearbit

clearbit.key = 'sk_6e5fc2e2eaca14297d931ee1b957fbd7'

@app.route("/")
def hello_world():
    return jsonify({"message":"welcome to the food app"})


@app.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()
    
    try:
        result = SignUpSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages)
    
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
            additional_data = clearbit.Enrichment.find(email=email, stream=True)
            
            user =  Users(first_name, last_name, email, password)
            
            if additional_data != None:
                user.avatar = additional_data['person']['avatar']
                user.location = additional_data['person']['location']
            
            user.hash_password()
            db.session.add(user)
            db.session.commit()
            id = user.id
            
            return jsonify({'id': str(id), 'status': 200})
        
        
@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    
    try:
        result = LoginSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages)
    
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
    
    try:
        result = RecipeSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages)
    
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
    # select all recipes with their average score
    sql = text('SELECT recipes.name, AVG(recipe_rating.score) as average_score FROM recipes ' 
            'LEFT JOIN recipe_rating ON recipes.id = recipe_rating.recipe_id '
            'GROUP BY recipes.id ')
            
    result = db.session.execute(sql)
    
    return jsonify({'result': [dict(row) for row in result]})


@app.route("/my-recipes", methods=["GET"])
@jwt_required()  
def my_recipes():
    current_user = get_jwt_identity()
    
    recipes = Recipes.query.filter_by(user_id=current_user).all()
    recipe_schema = RecipeSchema(many=True)
    
    return jsonify(recipe_schema.dump(recipes))


@app.route("/rate-recipe", methods=["POST"])
@jwt_required()  
def rate_recipe():
    body = request.get_json()
    
    try:
        result = RecipeRatingSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages)
    
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
    
    try:
        result = IngredientSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages)
    
    name = body['name']
    current_user = get_jwt_identity()
    
    ingredient =  Ingredient(name, current_user)
    db.session.add(ingredient)
    db.session.commit()
    id = ingredient.id
    
    return jsonify({'id': str(id)})

@app.route("/ingredient/most-used", methods=["GET"])
@jwt_required()  
def most_used():
    
    # get top 5 used ingredients
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
