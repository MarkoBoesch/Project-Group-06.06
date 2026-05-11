# api_loader.py
# Loads recipes from TheMealDB API and saves them to our local database.
#
#
# What this file does:
# - Connects to TheMealDB's free public API (no API key required).
# - Fetches recipes letter-by-letter (search.php?f=a, ?f=b, ...) up to a limit.
# - Translates TheMealDB ingredient names into our internal ingredient keys
#   (e.g. "chicken breast" -> "chicken_breast") so they match the rest of the app.
# - Estimates allergens, cooking time, difficulty and nutritional values that
#   the API does not provide.
# - Registers ingredients from API recipes in the ingredients table so
#   users can select them in the search page (excluding filtered-out
#   items like water, spices, etc.).
#
# This is the only source of recipes in the app. The recipes table is empty
# until this file fills it on the first run.
#
# Used by app.py on:
#   - the very first start of the app (load_api_recipes), guarded by
#     st.session_state so it only runs once per session.
#
# API documentation: https://www.themealdb.com/api.php
# -----------------------------------------------------------------------------

import requests
# requests handles the HTTP calls to TheMealDB.

import sqlite3
# sqlite3 lets us read/write the local recipe database. We open our own
# connections here to keep this file self-contained and avoid circular imports.

DB_NAME = "emptythefridge.db"
API_URL = "https://www.themealdb.com/api/json/v1/1/"


# HELPER FUNCTIONS

def get_connection():
    """Opens a connection to the database."""
    # row_factory = sqlite3.Row lets us access columns by name (row["id"])
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def recipe_exists(api_id):
    """Checks if a recipe with this API ID already exists in the database."""
    # We check by api_id (TheMealDB's own ID) rather than our internal id,
    # because the internal id is generated locally and would not help us
    # detect duplicates from the API. This prevents the same recipe from
    # being inserted twice if load_api_recipes() is ever called more than once.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM recipes WHERE api_id = ?", (api_id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None


# INGREDIENT TRANSLATION
# TheMealDB uses plain English names like "chicken breast".
# Our app uses internal keys like "chicken_breast".
# This dictionary maps the most common TheMealDB names to our keys.
# If a name is not in this dictionary, translate_ingredient() uses a
# simple fallback: replace spaces with underscores.
#
# Why this matters: the Random Forest (recommender.py) uses ingredient
# keys as features, so inconsistent keys for the same ingredient hurt
# prediction quality. Forcing every variant to the same key makes sure 
# the model sees them as one ingredient.

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
    # Lowercase and strip whitespace first so "Chicken Breast " and
    # "chicken breast" both find the same dictionary entry.
    name_lower = ingredient_name.lower().strip()
    if name_lower in INGREDIENT_MAPPING:
        return INGREDIENT_MAPPING[name_lower]
    # Fallback: turn the raw name into a key-shaped string. It will at
    # least be consistent across all API recipes that use the same name.
    return name_lower.replace(" ", "_").replace("-", "_")


def make_display_name(ingredient_key):
    """
    Turns an internal key into a readable display name for the ingredient selector.
    Example: "chicken_breast"  ->  "Chicken Breast"
    """
    # title() capitalises the first letter of every word, good enough for
    # most ingredient names. Edge cases like "olive oil" come out fine.
    return ingredient_key.replace("_", " ").title()


# REGISTER INGREDIENTS
#
# The ingredients table is what populates the ingredient selector on the
# "Enter Ingredients" page in app.py. db.py seeds the table with a
# starter set of display names. Whenever an API recipe brings in a new
# ingredient that isn't in that starter set, we register it here so users
# can actually select it in the multiselect.
#
# Without this step, users could never select API-only ingredients, so
# those recipes would never match a search and stay invisible.

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

        # INSERT OR IGNORE: if the key already exists in the UNIQUE column,
        # SQLite silently does nothing instead of raising an error. This
        # lets us call register_ingredients() once per recipe without
        # worrying about duplicates.
        cursor.execute(
            "INSERT OR IGNORE INTO ingredients (key, name) VALUES (?, ?)",
            (key, display_name)
        )

    connection.commit()
    connection.close()


# ALLERGEN DETECTION
# TheMealDB does not tag allergens, so we check the ingredient list ourselves
# against a few hand-picked lists of "ingredients that contain X".
# The result is a comma-separated string used by the allergen filter on
# the search page.

def detect_allergens(ingredient_keys):
    """Detects allergens based on the ingredients and returns them as a comma-separated string."""
    allergens = []

    # These four lists cover the most common allergen filters in the app.
    # They are intentionally short and conservative. If an ingredient isn't
    # in here, we simply don't tag the allergen rather than risk false alarms.
    gluten_ingredients  = ["flour", "pasta", "bread", "oats"]
    dairy_ingredients   = ["milk", "butter", "cream", "cheese", "mozzarella", "parmesan", "yogurt", "cream_cheese"]
    egg_ingredients     = ["egg"]
    fish_ingredients    = ["salmon", "tuna", "shrimp"]

    # Walk through every ingredient and add the matching allergen to the list.
    # The "not in allergens" check stops us from adding the same allergen twice
    # (e.g. a recipe with both "milk" and "butter" should only tag "dairy" once).
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


# NUTRITION ESTIMATION
# TheMealDB does not return nutritional values, so we estimate them
# based on which ingredients are in the recipe. The numbers are rough
# per-portion estimates, good enough to power the radar chart on the
# Statistics page in app.py without being misleading.

# Estimated calories contributed by each ingredient (rough values per portion).
# Only ingredients that significantly affect calorie count are listed; small
# additions like spices or herbs are simply ignored (they contribute ~0 kcal).
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
    # Ingredients not in our table contribute 0 calories. That's fine for
    # spices and herbs but means a recipe full of unknown ingredients would
    # end up at 0 kcal, which is why we have the fallback below.
    calories = sum(CALORIES_PER_INGREDIENT.get(key, 0) for key in ingredient_keys)

    # If no ingredient was recognised, use a sensible default so the
    # statistics page doesn't show zeros for these recipes.
    if calories == 0:
        calories = 350

    # Rough macronutrient split: 15% protein, 50% carbs, 35% fat.
    # We divide by 4 (kcal per gram of protein/carbs) and 9 (kcal per gram
    # of fat) to convert kilocalories into grams.
    protein        = int(calories * 0.15 / 4)
    carbohydrates  = int(calories * 0.50 / 4)
    fat            = int(calories * 0.35 / 9)

    # More ingredients = more fibre/vitamins/minerals (rough heuristic).
    # The min/max calls keep the values inside sane ranges so they look
    # reasonable on the radar chart even for very long ingredient lists.
    fiber    = max(2, int(len(ingredient_keys) * 0.8))
    vitamins = min(80, len(ingredient_keys) * 8)
    minerals = min(60, len(ingredient_keys) * 6)

    return {
        # Cap calories at 900 so a single recipe can't dominate the
        # "daily calories" radar slice on the Statistics page.
        "calories":      min(calories, 900),
        "protein":       protein,
        "carbohydrates": carbohydrates,
        "fat":           fat,
        "fiber":         fiber,
        "vitamins":      vitamins,
        "minerals":      minerals,
    }


# SAVE RECIPE TO DATABASE
# Inserts one fully-prepared recipe dictionary into the recipes table.
# The id column AUTOINCREMENTs, so we don't pass an ID ourselves.

def save_recipe(recipe_data):
    """Saves a single recipe to the database."""
    connection = get_connection()
    cursor = connection.cursor()
    # INSERT OR IGNORE protects against duplicates via the UNIQUE constraint
    # on api_id. If for any reason a recipe with the same api_id is already
    # there, the row is silently skipped instead of raising an IntegrityError.
    cursor.execute("""
        INSERT OR IGNORE INTO recipes (
            name, ingredients, amounts,
            time_minutes, difficulty,
            allergens, calories, protein, carbohydrates,
            fat, fiber, vitamins, minerals,
            instructions, api_id, api_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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


# FETCH RECIPES FROM THEMEALDB
# Main loop that actually talks to the API.
#
# TheMealDB lets us search by first letter (search.php?f=a, ?f=b, ...).
# We loop through all 26 letters and collect up to max_recipes total.
# Each meal returned by the API is then translated, enriched with our
# own estimates (allergens, nutrition, time, difficulty) and saved.

def load_from_themealdb(max_recipes=200):
    """
    Fetches recipes from TheMealDB and saves them to the database.
    Returns the number of new recipes that were saved.
    """
    saved = 0
    letters = "abcdefghijklmnopqrstuvwxyz"

    for letter in letters:
        # Stop as soon as we have reached the limit. Without this, we would
        # always fetch all 26 letters even if max_recipes was reached early.
        if saved >= max_recipes:
            break

        # The whole letter loop is wrapped in try/except so one bad request
        # (timeout, network blip, malformed JSON) doesn't kill the whole
        # import. We just skip that letter and continue with the next one.
        try:
            # Request all meals whose name starts with this letter.
            # timeout=10 prevents the app startup from hanging forever if
            # TheMealDB is slow or down.
            response = requests.get(f"{API_URL}search.php?f={letter}", timeout=10)

            if response.status_code != 200:
                continue  # Skip this letter if the request failed

            data = response.json()

            # TheMealDB returns {"meals": null} (not an empty list) when no
            # meals match the search letter, so we have to check for None
            # explicitly before trying to iterate.
            if data["meals"] is None:
                continue  # No meals starting with this letter

            for meal in data["meals"]:
                if saved >= max_recipes:
                    break

                api_id = meal["idMeal"]

                # Skip recipes we already have in the database. This makes
                # it safe to re-run the importer without ending up with
                # duplicates.
                if recipe_exists(api_id):
                    continue

                # PARSE INGREDIENTS AND AMOUNTS
                # TheMealDB stores ingredients in 20 numbered fields:
                # strIngredient1, strIngredient2, ..., strIngredient20
                # and their amounts in strMeasure1, strMeasure2, ...
                # Unused slots are empty strings, which is how we know
                # where the ingredient list ends.
                ingredient_keys = []
                amount_parts = []

                for i in range(1, 21):
                    ingredient_name = meal.get(f"strIngredient{i}", "")
                    amount          = meal.get(f"strMeasure{i}", "")

                    # Empty / whitespace strings mean there are no more
                    # ingredients in this recipe. We can't break here
                    # though, because some recipes have gaps (slot 5 empty,
                    # slot 6 filled), so we just skip the empty ones.
                    if ingredient_name and ingredient_name.strip():
                        key = translate_ingredient(ingredient_name)
                        ingredient_keys.append(key)

                        if amount and amount.strip():
                            # Store as "key:amount" so app.py can parse it
                            # back into a dictionary when displaying the
                            # recipe detail view.
                            amount_parts.append(f"{key}:{amount.strip()}")

                # Skip recipes that have no recognisable ingredients.
                # they would never match a search anyway.
                if not ingredient_keys:
                    continue

                # ENRICH WITH OUR OWN ESTIMATES
                # The API doesn't give us nutrition, allergens, time or
                # difficulty, so we derive them from the ingredient list.
                nutrition = estimate_nutrition(ingredient_keys)
                allergens = detect_allergens(ingredient_keys)

                # Estimate cooking time and difficulty from the number of
                # ingredients. Crude but surprisingly accurate: short
                # ingredient lists tend to mean simple, fast recipes.
                if len(ingredient_keys) <= 5:
                    time_minutes = 20
                    difficulty   = "easy"
                elif len(ingredient_keys) <= 10:
                    time_minutes = 35
                    difficulty   = "medium"
                else:
                    time_minutes = 50
                    difficulty   = "hard"

                # Build the dictionary in the exact shape that save_recipe()
                # (and the recipes table) expects.
                recipe_data = {
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

                # Register every ingredient of this recipe in the
                # ingredients table so users can select them on the
                # search page (see the REGISTER INGREDIENTS section above
                # for why this is essential).
                register_ingredients(ingredient_keys)

                saved += 1

        except Exception as error:
            # Log and move on. One broken letter shouldn't take down the
            # entire import. The user will still get all the recipes from
            # the other 25 letters.
            print(f"Error loading letter {letter}: {error}")
            continue

    return saved


# MAIN ENTRY POINT
# Called by app.py once on startup (guarded by st.session_state so it only
# runs on the very first load, not on every Streamlit rerun). On subsequent
# starts it sees that recipes are already in the database and exits
# immediately without making any network calls.

def load_api_recipes():
    """
    Loads API recipes if the recipes table is still empty.
    Returns the number of newly loaded recipes (0 if already loaded before).
    """
    # Check how many recipes are already in the database. We use this as
    # the signal for "have we ever run the importer before?". Since the
    # API is now the only source of recipes, an empty recipes table means
    # we are on the very first run.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]
    connection.close()

    if count == 0:
        # First run: fetch from the API. The print statements show up in
        # the terminal where Streamlit is running and are useful for
        # debugging if the import seems stuck.
        print("Loading recipes from TheMealDB API...")
        new_count = load_from_themealdb(max_recipes=200)
        print(f"{new_count} recipes loaded from TheMealDB.")
        return new_count
    else:
        # Already loaded on a previous run, nothing to do. Returning 0
        # signals "no new recipes" to the caller in app.py.
        print(f"Recipes already present: {count} recipes.")
        return 0
