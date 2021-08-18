from marshmallow import Schema, fields, validate

class SignUpSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
class IngredientSchema(Schema):
    name = fields.String(required=True)
    
class RecipeSchema(Schema):
    name = fields.String(required=True)
    text = fields.String(required=True)
    
class RecipeRatingSchema(Schema):
    recipe_id = fields.Integer(required=True)
    score = fields.String(validate=validate.OneOf(["1", "2", "3", "4", "5"]),required=True)
    
