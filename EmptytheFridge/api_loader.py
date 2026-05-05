# api_loader.py
# This file loads recipes from the TheMealDB API and saves them to our database.
#
# NOTE: This file uses Claude-assisted API logic.
#
# TheMealDB API is free and needs no API key.
# Documentation: https://www.themealdb.com/api.php
# -----------------------------------------------------------------------------

import requests
import sqlite3

DB_NAME = "emptythefridge.db"
API_URL = "https://www.themealdb.com/api/json/v1/1/"

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def get_connection():
    """Opens a connection to the database."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def recipe_exists(api_id):
    """Checks if a recipe with this API ID already exists in the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM recipes WHERE api_id = ?", (api_id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None


def add_api_columns():
    """Adds api_id and api_source columns to the database if they don't exist yet."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE recipes ADD COLUMN api_id TEXT")
        cursor.execute("ALTER TABLE recipes ADD COLUMN api_source TEXT")
        connection.commit()
    except Exception:
        pass  # Columns already exist
    connection.close()


def get_next_id():
    """Returns the next free ID for a new recipe."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(id) FROM recipes")
    result = cursor.fetchone()[0]
    connection.close()
    return 1000 if result is None else result + 1


# -----------------------------------------------------------------------------
# INGREDIENT TRANSLATION
# Maps TheMealDB ingredient names to our internal ingredient keys.
# -----------------------------------------------------------------------------

INGREDIENT_MAPPING = {
    "chicken": "chicken_breast",
    "chicken breast": "chicken_breast",
    "chicken breasts": "chicken_breast",
    "ground beef": "ground_beef",
    "beef mince": "ground_beef",
    "minced beef": "ground_beef",
    "bacon": "bacon",
    "salmon": "salmon",
    "tuna": "tuna",
    "shrimp": "shrimp",
    "prawns": "shrimp",
    "pork": "pork",
    "egg": "egg",
    "eggs": "egg",
    "milk": "milk",
    "butter": "butter",
    "cream": "cream",
    "double cream": "cream",
    "heavy cream": "cream",
    "cheese": "cheese",
    "cheddar": "cheese",
    "mozzarella": "mozzarella",
    "parmesan": "parmesan",
    "yogurt": "yogurt",
    "cream cheese": "cream_cheese",
    "potato": "potato",
    "potatoes": "potato",
    "carrot": "carrot",
    "carrots": "carrot",
    "onion": "onion",
    "onions": "onion",
    "garlic": "garlic",
    "tomato": "tomato",
    "tomatoes": "tomato",
    "zucchini": "zucchini",
    "courgette": "zucchini",
    "bell pepper": "bell_pepper",
    "red pepper": "bell_pepper",
    "green pepper": "bell_pepper",
    "spinach": "spinach",
    "broccoli": "broccoli",
    "mushroom": "mushroom",
    "mushrooms": "mushroom",
    "leek": "leek",
    "cauliflower": "cauliflower",
    "cucumber": "cucumber",
    "lettuce": "lettuce",
    "corn": "corn",
    "sweetcorn": "corn",
    "peas": "peas",
    "green beans": "green_beans",
    "eggplant": "eggplant",
    "aubergine": "eggplant",
    "sweet potato": "sweet_potato",
    "pasta": "pasta",
    "spaghetti": "pasta",
    "penne": "pasta",
    "rice": "rice",
    "bread": "bread",
    "flour": "flour",
    "oats": "oats",
    "lentils": "lentils",
    "chickpeas": "chickpeas",
    "tomato sauce": "tomato_sauce",
    "passata": "tomato_sauce",
    "olive oil": "olive_oil",
    "oil": "oil",
    "vegetable stock": "vegetable_broth",
    "chicken stock": "vegetable_broth",
    "salt": "salt",
    "pepper": "pepper",
    "sugar": "sugar",
    "vinegar": "vinegar",
    "soy sauce": "soy_sauce",
    "lemon": "lemon",
    "apple": "apple",
    "banana": "banana",
    "water": "water",
    "baking powder": "baking_powder",
}


def translate_ingredient(ingredient_name):
    """Translates a TheMealDB ingredient name into our internal key."""
    name_lower = ingredient_name.lower().strip()
    if name_lower in INGREDIENT_MAPPING:
        return INGREDIENT_MAPPING[name_lower]
    return name_lower.replace(" ", "_").replace("-", "_")


def detect_allergens(ingredient_keys):
    """Detects allergens based on the ingredients."""
    allergens = []
    gluten_ingredients = ["flour", "pasta", "bread", "oats"]
    dairy_ingredients = ["milk", "butter", "cream", "cheese", "mozzarella", "parmesan", "yogurt", "cream_cheese"]
    egg_ingredients = ["egg"]
    fish_ingredients = ["salmon", "tuna", "shrimp"]

    for key in ingredient_keys:
        if key in gluten_ingredients and "gluten" not in allergens:
            allergens.append("gluten")
        if key in dairy_ingredients and "dairy" not in allergens:
            allergens.append("dairy")
        if key in egg_ingredients and "egg" not in allergens:
            allergens.append("egg")
        if key in fish_ingredients and "fish" not in allergens:
            allergens.append("fish")

    return ",".join(allergens)


# -----------------------------------------------------------------------------
# ESTIMATE NUTRITION
# TheMealDB does not return nutritional values, so we estimate them.
# -----------------------------------------------------------------------------

CALORIES_PER_INGREDIENT = {
    "chicken_breast": 165, "ground_beef": 250, "bacon": 300, "salmon": 180,
    "tuna": 130, "shrimp": 80, "pork": 220, "egg": 70, "milk": 50,
    "butter": 120, "cream": 100, "cheese": 150, "pasta": 180, "rice": 160,
    "potato": 90, "sweet_potato": 100, "bread": 120, "flour": 80,
    "lentils": 120, "chickpeas": 130, "tomato": 20, "carrot": 25,
    "spinach": 10, "broccoli": 25, "mushroom": 15, "onion": 20,
    "tomato_sauce": 40, "olive_oil": 80, "oats": 150,
}


def estimate_nutrition(ingredient_keys):
    """Estimates nutritional values based on recipe ingredients."""
    calories = sum(CALORIES_PER_INGREDIENT.get(key, 0) for key in ingredient_keys)

    if calories == 0:
        calories = 350

    protein = int(calories * 0.15 / 4)
    carbohydrates = int(calories * 0.50 / 4)
    fat = int(calories * 0.35 / 9)
    fiber = max(2, int(len(ingredient_keys) * 0.8))
    vitamins = min(80, len(ingredient_keys) * 8)
    minerals = min(60, len(ingredient_keys) * 6)

    return {
        "calories": min(calories, 900),
        "protein": protein,
        "carbohydrates": carbohydrates,
        "fat": fat,
        "fiber": fiber,
        "vitamins": vitamins,
        "minerals": minerals
    }


# -----------------------------------------------------------------------------
# SAVE RECIPE
# -----------------------------------------------------------------------------

def save_recipe(recipe_data):
    """Saves a single recipe to the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO recipes (
            id, name, ingredients, amounts,
            time_minutes, difficulty,
            allergens, calories, protein, carbohydrates,
            fat, fiber, vitamins, minerals,
            instructions, api_id, api_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        recipe_data["id"],
        recipe_data["name"],
        recipe_data["ingredients"],
        recipe_data["amounts"],
        recipe_data["time_minutes"],
        recipe_data["difficulty"],
        recipe_data["allergens"],
        recipe_data["calories"],
        recipe_data["protein"],
        recipe_data["carbohydrates"],
        recipe_data["fat"],
        recipe_data["fiber"],
        recipe_data["vitamins"],
        recipe_data["minerals"],
        recipe_data["instructions"],
        recipe_data["api_id"],
        recipe_data["api_source"]
    ))
    connection.commit()
    connection.close()


# -----------------------------------------------------------------------------
# FETCH FROM THEMEALDB
# -----------------------------------------------------------------------------

def load_from_themealdb(max_recipes=200):
    """Loads recipes from TheMealDB API and saves them to the database."""
    saved = 0
    letters = "abcdefghijklmnopqrstuvwxyz"

    for letter in letters:
        if saved >= max_recipes:
            break

        try:
            response = requests.get(f"{API_URL}search.php?f={letter}", timeout=10)

            if response.status_code != 200:
                continue

            data = response.json()

            if data["meals"] is None:
                continue

            for meal in data["meals"]:
                if saved >= max_recipes:
                    break

                api_id = meal["idMeal"]
                if recipe_exists(api_id):
                    continue

                # Extract ingredients from TheMealDB structure
                # TheMealDB stores ingredients in fields strIngredient1...strIngredient20
                ingredient_keys = []
                amount_parts = []

                for i in range(1, 21):
                    ingredient_name = meal.get(f"strIngredient{i}", "")
                    amount = meal.get(f"strMeasure{i}", "")

                    if ingredient_name and ingredient_name.strip():
                        key = translate_ingredient(ingredient_name)
                        ingredient_keys.append(key)
                        if amount and amount.strip():
                            amount_parts.append(f"{key}:{amount.strip()}")

                if not ingredient_keys:
                    continue

                nutrition = estimate_nutrition(ingredient_keys)
                allergens = detect_allergens(ingredient_keys)

                # Estimate cooking time based on number of ingredients
                if len(ingredient_keys) <= 5:
                    time_minutes = 20
                elif len(ingredient_keys) <= 10:
                    time_minutes = 35
                else:
                    time_minutes = 50

                # Estimate difficulty
                if len(ingredient_keys) <= 5:
                    difficulty = "easy"
                elif len(ingredient_keys) <= 10:
                    difficulty = "medium"
                else:
                    difficulty = "hard"

                recipe_data = {
                    "id": get_next_id(),
                    "name": meal["strMeal"],
                    "ingredients": ",".join(ingredient_keys),
                    "amounts": ",".join(amount_parts) if amount_parts else "",
                    "time_minutes": time_minutes,
                    "difficulty": difficulty,
                    "allergens": allergens,
                    "calories": nutrition["calories"],
                    "protein": nutrition["protein"],
                    "carbohydrates": nutrition["carbohydrates"],
                    "fat": nutrition["fat"],
                    "fiber": nutrition["fiber"],
                    "vitamins": nutrition["vitamins"],
                    "minerals": nutrition["minerals"],
                    "instructions": meal.get("strInstructions", ""),
                    "api_id": api_id,
                    "api_source": "TheMealDB"
                }

                save_recipe(recipe_data)
                saved += 1

        except Exception as error:
            print(f"Error loading letter {letter}: {error}")
            continue

    return saved


# -----------------------------------------------------------------------------
# MAIN LOAD FUNCTION
# This function is called by app.py when the app starts.
# -----------------------------------------------------------------------------

def load_api_recipes():
    """Prepares the database and loads API recipes if needed."""

    add_api_columns()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE api_source = 'TheMealDB'")
    count_api_recipes = cursor.fetchone()[0]
    connection.close()

    if count_api_recipes == 0:
        print("Loading recipes from TheMealDB API...")
        count = load_from_themealdb(max_recipes=200)
        print(f"{count} recipes loaded from TheMealDB.")
        return count
    else:
        print(f"TheMealDB recipes already present: {count_api_recipes} recipes.")
        return 0
