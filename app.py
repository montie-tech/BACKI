from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import requests

app = Flask(__name__)
CORS(app)  # Allow frontend on different domain

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",       # Replace with your MySQL host
    user="root",            # Replace with your MySQL username
    password="1234",    # Replace with your MySQL password
    database="recipes_db"   # Replace with your MySQL database
)

cursor = db.cursor(dictionary=True)

# External Recipe API (Spoonacular)
SPOONACULAR_API_KEY = "YOUR_SPOONACULAR_API_KEY"
SPOONACULAR_URL = "https://api.spoonacular.com/recipes/complexSearch"

# Endpoint: Search recipes by ingredients
@app.route("/recipes", methods=["POST"])
def get_recipes():
    data = request.get_json()
    ingredients = data.get("ingredients", "")
    if not ingredients:
        return jsonify({"recipes": []})

    # Search in MySQL first
    ingredient_list = [i.strip() for i in ingredients.split(",")]
    query = "SELECT * FROM recipes WHERE " + " OR ".join([f"ingredients LIKE '%{i}%'" for i in ingredient_list])
    cursor.execute(query)
    results = cursor.fetchall()

    # If database has no results, search external API
    if not results:
        api_response = requests.get(SPOONACULAR_URL, params={
            "apiKey": SPOONACULAR_API_KEY,
            "includeIngredients": ingredients,
            "number": 5
        })
        if api_response.status_code == 200:
            api_data = api_response.json()
            recipes = []
            for item in api_data.get("results", []):
                recipes.append({
                    "title": item.get("title"),
                    "description": "Recipe found on Spoonacular",
                    "ingredients": ingredients
                })
            return jsonify({"recipes": recipes})
        else:
            return jsonify({"recipes": []})

    return jsonify({"recipes": results})

# Endpoint: Detect ingredients from image (dummy)
@app.route("/detect-ingredients", methods=["POST"])
def detect_ingredients():
    if "image" not in request.files:
        return jsonify({"ingredients": []})
    
    image = request.files["image"]
    filename = image.filename
    os.makedirs("uploads", exist_ok=True)
    image.save(os.path.join("uploads", filename))
    
    # Dummy ingredient detection
    detected = ["tomato", "onion", "garlic"]
    return jsonify({"ingredients": detected})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
