from app import ma
from app.models import Recipes

class RecipesSchema(ma.SQLAlchemySchema):
    class Meta:
        fields = ("id", "user_id", "name", "tekst")
        
recipe_schema = RecipesSchema(many=True)