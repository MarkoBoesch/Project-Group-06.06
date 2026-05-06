# api_loader.py
# This file loads recipes from the TheMealDB API and saves them to our database.
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
# These are small utility functions used by the bigger functions below.
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
    """
    Adds api_id and api_source columns to the recipes table if they don't exist yet.
    We need these two extra columns to track which recipes came from the API.
    The try/except simply skips the ALTER TABLE if the columns are already there.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE recipes ADD COLUMN api_id TEXT")
        cursor.execute("ALTER TABLE recipes ADD COLUMN api_source TEXT")
        connection.commit()
    except Exception:
        pass  # Columns already exist — that is fine, just continue
    connection.close()


def get_next_id():
    """
    Returns the next free ID for a new recipe.
    We start at 1000 so that API recipe IDs never clash with the
    hardcoded recipe IDs in recipes.py (which are much smaller numbers).
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(id) FROM recipes")
    result = cursor.fetchone()[0]
    connection.close()
    return 1000 if result is None else result + 1


# -----------------------------------------------------------------------------
# INGREDIENT TRANSLATION
# TheMealDB uses plain English names like "chicken breast".
# Our app uses internal keys like "chicken_breast".
# This dictionary maps the most common TheMealDB names to our keys.
# If a name is not in this dictionary, translate_ingredient() uses a
# simple fallback: replace spaces with underscores.
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
    """
    Translates a TheMealDB ingredient name into our internal key.
    Example: "chicken breast"  ->  "chicken_breast"
    If the name is not in INGREDIENT_MAPPING, we fall back to replacing
    spaces and hyphens with underscores.
    Example: "thai basil"  ->  "thai_basil"
    """
    name_lower = ingredient_name.lower().strip()
    if name_lower in INGREDIENT_MAPPING:
        return INGREDIENT_MAPPING[name_lower]
    return name_lower.replace(" ", "_").replace("-", "_")


def make_display_name(ingredient_key):
    """
    Turns an internal key into a readable display name for the ingredient selector.
    Example: "chicken_breast"  ->  "Chicken Breast"
    """
    return ingredient_key.replace("_", " ").title()


# -----------------------------------------------------------------------------
# REGISTER INGREDIENTS  ← THIS IS THE KEY FIX
#
# The ingredients table is what populates the ingredient selector in the app.
# Hardcoded recipes (from recipes.py) have their ingredients pre-loaded into
# that table by database.py on first run.
# API recipes do NOT — so after saving an API recipe we call this function
# to make sure every ingredient key that appears in API recipes is also
# listed in the ingredients table.
# Without this step, users can never select those ingredients, so API
# recipes never match and are invisible in search results.
# -----------------------------------------------------------------------------

def register_ingredients(ingredient_keys):
    """
    Adds any new ingredient keys to the ingredients table.
    If an ingredient key already exists there, it is skipped
    (INSERT OR IGNORE handles that automatically).
    """
    connection = get_connection()
    cursor = connection.cursor()

    for key in ingredient_keys:
        # Build a human-readable display name from the key.
        # e.g. "sweet_potato" becomes "Sweet Potato"
        display_name = make_display_name(key)

        # INSERT OR IGNORE: if the key already exists, do nothing.
        cursor.execute(
            "INSERT OR IGNORE INTO ingredients (key, name) VALUES (?, ?)",
            (key, display_name)
        )

    connection.commit()
    connection.close()


# -----------------------------------------------------------------------------
# ALLERGEN DETECTION
# TheMealDB does not tag allergens, so we check the ingredient list ourselves.
# -----------------------------------------------------------------------------

def detect_allergens(ingredient_keys):
    """Detects allergens based on the ingredients and returns them as a comma-separated string."""
    allergens = []

    gluten_ingredients  = ["flour", "pasta", "bread", "oats"]
    dairy_ingredients   = ["milk", "butter", "cream", "cheese", "mozzarella", "parmesan", "yogurt", "cream_cheese"]
    egg_ingredients     = ["egg"]
    fish_ingredients    = ["salmon", "tuna", "shrimp"]

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
# NUTRITION ESTIMATION
# TheMealDB does not return nutritional values, so we estimate them
# based on which ingredients are in the recipe.
# -----------------------------------------------------------------------------

# Estimated calories contributed by each ingredient (rough values per portion).
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
    """
    Estimates nutritional values based on the ingredients in a recipe.
    Returns a dictionary with calories, protein, carbohydrates, fat, fiber,
    vitamins and minerals.
    """
    # Add up calories for every recognised ingredient.
    # Ingredients not in our table contribute 0 calories.
    calories = sum(CALORIES_PER_INGREDIENT.get(key, 0) for key in ingredient_keys)

    # If no ingredient was recognised, use a sensible default.
    if calories == 0:
        calories = 350

    # Rough macronutrient split: 15% protein, 50% carbs, 35% fat.
    protein        = int(calories * 0.15 / 4)
    carbohydrates  = int(calories * 0.50 / 4)
    fat            = int(calories * 0.35 / 9)

    # More ingredients = more fibre/vitamins/minerals (rough estimate).
    fiber    = max(2, int(len(ingredient_keys) * 0.8))
    vitamins = min(80, len(ingredient_keys) * 8)
    minerals = min(60, len(ingredient_keys) * 6)

    return {
        "calories":      min(calories, 900),
        "protein":       protein,
        "carbohydrates": carbohydrates,
        "fat":           fat,
        "fiber":         fiber,
        "vitamins":      vitamins,
        "minerals":      minerals,
    }


# -----------------------------------------------------------------------------
# SAVE RECIPE TO DATABASE
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
        recipe_data["api_source"],
    ))
    connection.commit()
    connection.close()


# -----------------------------------------------------------------------------
# FETCH RECIPES FROM THEMEALDB
# The API lets us search by first letter (search.php?f=a, ?f=b, ...).
# We loop through all 26 letters and collect up to max_recipes total.
# -----------------------------------------------------------------------------

def load_from_themealdb(max_recipes=200):
    """
    Fetches recipes from TheMealDB and saves them to the database.
    Returns the number of new recipes that were saved.
    """
    saved = 0
    letters = "abcdefghijklmnopqrstuvwxyz"

    for letter in letters:
        # Stop as soon as we have reached the limit.
        if saved >= max_recipes:
            break

        try:
            # Request all meals whose name starts with this letter.
            response = requests.get(f"{API_URL}search.php?f={letter}", timeout=10)

            if response.status_code != 200:
                continue  # Skip this letter if the request failed

            data = response.json()

            if data["meals"] is None:
                continue  # No meals starting with this letter

            for meal in data["meals"]:
                if saved >= max_recipes:
                    break

                api_id = meal["idMeal"]

                # Skip recipes we already have in the database.
                if recipe_exists(api_id):
                    continue

                # TheMealDB stores ingredients in 20 numbered fields:
                # strIngredient1, strIngredient2, ..., strIngredient20
                # and their amounts in strMeasure1, strMeasure2, ...
                ingredient_keys = []
                amount_parts = []

                for i in range(1, 21):
                    ingredient_name = meal.get(f"strIngredient{i}", "")
                    amount          = meal.get(f"strMeasure{i}", "")

                    # Empty strings mean there are no more ingredients.
                    if ingredient_name and ingredient_name.strip():
                        key = translate_ingredient(ingredient_name)
                        ingredient_keys.append(key)

                        if amount and amount.strip():
                            # Store as "key:amount" so we can parse it later.
                            amount_parts.append(f"{key}:{amount.strip()}")

                # Skip recipes that have no recognisable ingredients.
                if not ingredient_keys:
                    continue

                nutrition = estimate_nutrition(ingredient_keys)
                allergens = detect_allergens(ingredient_keys)

                # Estimate cooking time and difficulty from the number of ingredients.
                if len(ingredient_keys) <= 5:
                    time_minutes = 20
                    difficulty   = "easy"
                elif len(ingredient_keys) <= 10:
                    time_minutes = 35
                    difficulty   = "medium"
                else:
                    time_minutes = 50
                    difficulty   = "hard"

                recipe_data = {
                    "id":            get_next_id(),
                    "name":          meal["strMeal"],
                    "ingredients":   ",".join(ingredient_keys),
                    "amounts":       ",".join(amount_parts) if amount_parts else "",
                    "time_minutes":  time_minutes,
                    "difficulty":    difficulty,
                    "allergens":     allergens,
                    "calories":      nutrition["calories"],
                    "protein":       nutrition["protein"],
                    "carbohydrates": nutrition["carbohydrates"],
                    "fat":           nutrition["fat"],
                    "fiber":         nutrition["fiber"],
                    "vitamins":      nutrition["vitamins"],
                    "minerals":      nutrition["minerals"],
                    "instructions":  meal.get("strInstructions", ""),
                    "api_id":        api_id,
                    "api_source":    "TheMealDB",
                }

                save_recipe(recipe_data)

                # FIX: register every ingredient of this recipe in the
                # ingredients table so users can select them in the app.
                register_ingredients(ingredient_keys)

                saved += 1

        except Exception as error:
            print(f"Error loading letter {letter}: {error}")
            continue

    return saved


# -----------------------------------------------------------------------------
# MAIN ENTRY POINT
# Called by app.py once on startup (guarded by session_state so it only
# runs on the very first load, not on every Streamlit rerun).
# -----------------------------------------------------------------------------

def load_api_recipes():
    """
    Prepares the database columns and loads API recipes if none exist yet.
    Returns the number of newly loaded recipes (0 if already loaded before).
    """
    # Make sure the api_id and api_source columns exist.
    add_api_columns()

    # Check how many API recipes are already in the database.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes WHERE api_source = 'TheMealDB'")
    count_api_recipes = cursor.fetchone()[0]
    connection.close()

    if count_api_recipes == 0:
        # First run: fetch from the API.
        print("Loading recipes from TheMealDB API...")
        count = load_from_themealdb(max_recipes=200)
        print(f"{count} recipes loaded from TheMealDB.")
        return count
    else:
        # Already loaded on a previous run — nothing to do.
        print(f"TheMealDB recipes already present: {count_api_recipes} recipes.")
        return 0