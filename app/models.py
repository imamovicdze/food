import enum
from app import db
from flask_bcrypt import generate_password_hash, check_password_hash

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200))
    location = db.Column(db.String(200))
    
    recipes = db.relationship("Recipes", backref='users', cascade="all, delete", passive_deletes=True)
    ingredients = db.relationship("Ingredient", backref='users', cascade="all, delete", passive_deletes=True)
    recipe_rating = db.relationship("Recipe_rating", backref='users', cascade="all, delete", passive_deletes=True)
    
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"name: {self.first_name}, email: {self.email}"
    
    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    __table_args__ = {'mysql_engine':'InnoDB'}
    
class Recipes(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text(200), nullable=False)
    
    recipe_rating = db.relationship("Recipe_rating", backref='recipes', cascade="all, delete", passive_deletes=True)
    recipe_ingredient = db.relationship("Recipe_ingredient", backref='recipes', cascade="all, delete", passive_deletes=True)
    
    def __init__(self, name, text, user_id):
        self.name = name
        self.text = text
        self.user_id = user_id
    
    __table_args__ = {'mysql_engine':'InnoDB'}
    
class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    recipe_ingredient = db.relationship("Recipe_ingredient", backref='ingredient', cascade="all, delete", passive_deletes=True)
    
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    __table_args__ = {'mysql_engine':'InnoDB'}
        
class Recipe_rating(db.Model):
    __tablename__ = 'recipe_rating'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Enum('1', '2', '3', '4', '5'), nullable=False)
    
    def __init__(self, recipe_id, user_id, score):
        self.recipe_id = recipe_id
        self.user_id = user_id
        self.score = score

    __table_args__ = {'mysql_engine':'InnoDB'}
      
class Recipe_ingredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id', ondelete='CASCADE'), nullable=False)
    
    def __init__(self, recipe_id, ingredient_id):
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id

    __table_args__ = {'mysql_engine':'InnoDB'}
