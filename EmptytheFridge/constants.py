# constants.py
# Static lookup tables used across the app.
#
#
# What this file does:
# - Defines `base_ingredients`: pantry staples the search algorithm assumes
#   are always at home (so the user doesn't have to tick them every time).
# - Defines `NON_VEGAN_INGREDIENTS` and `NON_VEGETARIAN_INGREDIENTS`: lookup
#   sets the diet filter on the search page uses to exclude recipes.
# - Defines `INGREDIENT_VALUE_CHF`: rough Swiss-Franc value per ingredient,
#   used by the Statistics page to estimate the money saved by cooking
#   instead of letting food spoil.
# - Defines `ingredient_dictionary`: maps internal keys (e.g. "bell_pepper")
#   to readable display names (e.g. "Bell Pepper") shown in the UI.
#
# This file contains NO logic and NO recipe data — it's pure constants.
# All recipes themselves come from TheMealDB API (see api_loader.py) and
# are stored in the SQLite database. The app reads recipes only from the
# database, never from this file.
#
# Used by app.py on:
#   - the Enter Ingredients page (base_ingredients, NON_VEGAN/VEGETARIAN
#     for the diet filter, ingredient_dictionary for display names)
#   - the Statistics page (INGREDIENT_VALUE_CHF for the cost calculation)
# Used by db.py on:
#   - first run, to seed the ingredients table with these starter
#     display names so the multiselect on the search page is never empty.
# -----------------------------------------------------------------------------


# BASE INGREDIENTS
# Pantry staples that we assume are always at home. The search page in app.py
# automatically treats these as "available" without the user having to select
# them — otherwise every recipe with salt or oil would never match.
# Also used on the Statistics page to count "saved ingredients": only
# non-base ingredients count, because using up salt isn't really preventing
# food waste.

base_ingredients = [
    "salt", "pepper", "oil", "butter", "sugar", "flour", "water",
    "garlic", "onion", "vegetable_broth", "olive_oil", "vinegar",
    "baking_powder", "baking_soda", "cornstarch"
]

# DIET FILTER SETS
# Used by the diet buttons on the search page (All / With Meat / Vegetarian /
# Vegan). The filter logic in app.py does a simple set check: if a recipe's
# ingredients overlap with the relevant set, the recipe is excluded from
# the results.
#
# We use Python sets (not lists) because membership lookups (`x in set`)
# are O(1) instead of O(n) — and the filter runs over every recipe on
# every search.


# Ingredients that are NOT vegan: all animal products, including dairy and eggs.
# A recipe with any of these is hidden when the user picks the "Vegan" filter.
NON_VEGAN_INGREDIENTS = {
    "egg", "milk", "butter", "cream", "cheese", "mozzarella", "parmesan",
    "yogurt", "cream_cheese", "feta", "ricotta", "sour_cream", "heavy_cream",
    "chicken_breast", "ground_beef", "bacon", "pork", "salmon", "tuna",
    "shrimp", "lamb", "turkey", "sausage", "ham", "prosciutto", "cod",
    "honey", "mayonnaise", "worcestershire",
}

# Ingredients that are NOT vegetarian: meat and fish only — dairy and eggs
# are fine for vegetarians, so they are NOT in this set.
# A recipe with any of these is hidden when the user picks the "Vegetarian"
# filter. (Worcestershire is included because it traditionally contains
# anchovies.)
NON_VEGETARIAN_INGREDIENTS = {
    "chicken_breast", "ground_beef", "bacon", "pork", "salmon", "tuna",
    "shrimp", "lamb", "turkey", "sausage", "ham", "prosciutto", "cod",
    "worcestershire",
}

# INGREDIENT VALUE TABLE (CHF)
# Estimated value in Swiss Francs per unit/portion of each ingredient.
# Used by app.py's calculate_costs() on the Statistics page to estimate how
# much money was "saved" by cooking a recipe instead of letting the
# ingredients spoil in the fridge.
#
# The numbers are rough averages from Swiss supermarkets — accurate enough
# for the savings KPIs on the dashboard without pretending to be a real
# pricing engine. Ingredients not in this table fall back to 0.50 CHF
# (handled in app.py via the .get() default).

INGREDIENT_VALUE_CHF = {
    "potato": 0.30, "carrot": 0.20, "celery": 0.30, "onion": 0.20,
    "garlic": 0.10, "tomato": 0.40, "zucchini": 0.50, "bell_pepper": 0.60,
    "spinach": 0.80, "broccoli": 0.70, "mushroom": 0.80, "leek": 0.60,
    "cauliflower": 0.70, "cucumber": 0.40, "lettuce": 0.50, "corn": 0.40,
    "peas": 0.40, "green_beans": 0.50, "eggplant": 0.60, "sweet_potato": 0.50,
    "chicken_breast": 2.50, "ground_beef": 2.80, "bacon": 1.50, "pork": 2.20,
    "salmon": 3.50, "tuna": 1.20, "shrimp": 3.00, "egg": 0.40, "milk": 0.20,
    "butter": 0.30, "cream": 0.60, "cheese": 0.80, "mozzarella": 1.20,
    "parmesan": 0.90, "yogurt": 0.50, "cream_cheese": 0.70, "pasta": 0.40,
    "rice": 0.30, "bread": 0.40, "flour": 0.10, "oats": 0.20, "lentils": 0.40,
    "chickpeas": 0.50, "tomato_sauce": 0.50, "vegetable_broth": 0.20,
    "olive_oil": 0.20, "oil": 0.10, "soy_sauce": 0.15, "lemon": 0.30,
    "apple": 0.40, "banana": 0.30, "avocado": 1.20, "feta": 1.00,
    "ricotta": 0.90, "sour_cream": 0.60, "tofu": 1.50, "asparagus": 1.20,
    "kale": 0.80, "beetroot": 0.40, "spring_onion": 0.30, "ginger": 0.20,
    "lime": 0.30, "mango": 1.00, "strawberry": 1.20, "blueberry": 1.50,
    "raspberry": 1.50, "cherry": 1.20, "peach": 0.80, "pear": 0.50,
    "pumpkin": 0.60, "white_cabbage": 0.30, "red_cabbage": 0.40,
    "fennel": 0.80, "lamb": 3.50, "turkey": 2.50, "sausage": 1.50,
    "ham": 1.20, "prosciutto": 1.80, "cod": 2.50, "coconut_milk": 0.60,
    "tahini": 0.50, "pesto": 0.70, "dijon_mustard": 0.20, "honey": 0.30,
    "mayonnaise": 0.20, "hot_sauce": 0.15, "bbq_sauce": 0.30,
    "worcestershire": 0.15, "heavy_cream": 0.70,
}

# INGREDIENT DICTIONARY
# Maps internal keys to human-readable English display names. The whole app
# uses keys internally for matching (so "bell_pepper" in one recipe equals
# "bell_pepper" in another), but the user only ever sees the values from
# this dictionary in the multiselect dropdown and on recipe cards.
#
# db.py loads this dictionary into the `ingredients` table on first
# run as a starter set, and api_loader.py adds more entries on top whenever
# it imports new recipes from TheMealDB.

ingredient_dictionary = {
    "potato": "Potato", "carrot": "Carrot", "celery": "Celery",
    "onion": "Onion", "garlic": "Garlic", "tomato": "Tomato",
    "zucchini": "Zucchini", "bell_pepper": "Bell Pepper", "spinach": "Spinach",
    "broccoli": "Broccoli", "mushroom": "Mushrooms", "leek": "Leek",
    "cauliflower": "Cauliflower", "cucumber": "Cucumber", "lettuce": "Lettuce",
    "corn": "Corn", "peas": "Peas", "green_beans": "Green Beans",
    "eggplant": "Eggplant", "sweet_potato": "Sweet Potato", "avocado": "Avocado",
    "asparagus": "Asparagus", "kale": "Kale", "beetroot": "Beetroot",
    "spring_onion": "Spring Onion", "ginger": "Ginger", "pumpkin": "Pumpkin",
    "white_cabbage": "White Cabbage", "red_cabbage": "Red Cabbage",
    "fennel": "Fennel", "lemon": "Lemon", "lime": "Lime", "apple": "Apple",
    "banana": "Banana", "mango": "Mango", "strawberry": "Strawberry",
    "blueberry": "Blueberry", "raspberry": "Raspberry", "cherry": "Cherry",
    "peach": "Peach", "pear": "Pear",
    "chicken_breast": "Chicken Breast", "ground_beef": "Ground Beef",
    "bacon": "Bacon", "pork": "Pork", "salmon": "Salmon", "tuna": "Tuna",
    "shrimp": "Shrimp", "lamb": "Lamb", "turkey": "Turkey", "sausage": "Sausage",
    "ham": "Ham", "prosciutto": "Prosciutto", "cod": "Cod",
    "egg": "Egg", "milk": "Milk", "butter": "Butter", "cream": "Cream",
    "cheese": "Cheese", "mozzarella": "Mozzarella", "parmesan": "Parmesan",
    "yogurt": "Yogurt", "cream_cheese": "Cream Cheese", "feta": "Feta",
    "ricotta": "Ricotta", "sour_cream": "Sour Cream",
    "pasta": "Pasta", "rice": "Rice", "bread": "Bread", "flour": "Flour",
    "oats": "Oats", "lentils": "Lentils", "chickpeas": "Chickpeas", "tofu": "Tofu",
    "tomato_sauce": "Tomato Sauce", "vegetable_broth": "Vegetable Broth",
    "olive_oil": "Olive Oil", "oil": "Oil", "salt": "Salt", "pepper": "Pepper",
    "sugar": "Sugar", "vinegar": "Vinegar", "soy_sauce": "Soy Sauce",
    "water": "Water", "baking_powder": "Baking Powder", "coconut_milk": "Coconut Milk",
    "tahini": "Tahini", "pesto": "Pesto", "dijon_mustard": "Dijon Mustard",
    "honey": "Honey", "mayonnaise": "Mayonnaise", "hot_sauce": "Hot Sauce",
    "bbq_sauce": "BBQ Sauce", "worcestershire": "Worcestershire Sauce",
}
