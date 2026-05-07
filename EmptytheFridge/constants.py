# constants.py
# Static lookup tables used across the app.
#
#
# What this file does:
# - Defines `base_ingredients`: spices & oils always assumed to be at home.
#   These are EXCLUDED from "money saved" calculations — only ingredients
#   the user actually selected on the search page count toward savings.
# - Defines `NON_VEGAN_INGREDIENTS` and `NON_VEGETARIAN_INGREDIENTS`: lookup
#   sets the diet filter on the search page uses to exclude recipes.
# - Defines `INGREDIENT_PRICE_PER_KG_CHF` / `INGREDIENT_VALUE_CHF`: real
#   Swiss supermarket prices (Migros/Coop) used by the Statistics page.
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

# BASE INGREDIENTS (spices & oils only)
# Rule: only things that live in the spice rack or oil shelf and are
# virtually never "used up" or likely to spoil qualify here.
# Everything else — vegetables, dairy, meat, pasta, eggs, etc. — is a
# real ingredient that the user selects on the search page.
#
# Two consequences of being in this list:
#   1. The recipe-matching algorithm on the search page treats these as
#      "always available", so a recipe that needs salt/cumin is never
#      penalised for the user not ticking those boxes.
#   2. These are EXCLUDED from the "money saved" calculation on the
#      Statistics page, because nobody enters salt as a fridge ingredient
#      they're trying to use up before it spoils.

base_ingredients = [
    # Oils & vinegars
    "oil", "olive_oil", "vinegar",
    # Basic seasonings
    "salt", "pepper",
    # Baking fundamentals
    "sugar", "flour", "baking_powder", "baking_soda", "cornstarch", "water",
    # Spices & dried herbs
    "garlic",           # dried / garlic powder (fresh garlic IS selectable)
    "paprika",
    "cumin",
    "cinnamon",
    "nutmeg",
    "curry_powder",
    "chili_flakes",
    "dried_herbs",      # covers oregano, thyme, basil, rosemary, etc.
    "bay_leaves",
    "turmeric",
    "ginger_powder",    # dried; fresh ginger IS selectable as an ingredient
    "cayenne",
    "cloves",
    "allspice",
    "cardamom",
    "coriander_powder",
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

# INGREDIENT PRICE TABLE (CHF per kg or per unit)
# Real Swiss supermarket prices based on Migros / Coop regular (non-sale) shelf
# prices as of April / May 2026.  Sources: rappn.ch April 2026 price comparison
# (migros.ch + coop.ch verified), K-Tipp August 2025, and blick.ch/bonus.ch.
#
# All prices are stored as CHF PER KILOGRAM for weight-sold ingredients, or
# CHF PER UNIT for piece/portion items (marked with a comment).
#
# calculate_costs() in app.py reads the "amounts" field of each recipe
# (format: "key:200g,key:3,key:0.5kg,...") and multiplies the per-kg price
# by the actual weight used, giving a proportional cost.  Piece-sold
# ingredients (eggs, lemons, avocados …) fall back to per-unit pricing when
# the amounts field contains a plain count (no unit suffix).
#
# Ingredients not found here fall back to CHF 3.00/kg in app.py
# (≈ a mid-range Swiss vegetable), which is intentionally conservative.

INGREDIENT_PRICE_PER_KG_CHF = {
    # ── Vegetables (CHF/kg) ──────────────────────────────────────────────────
    "potato":        1.60,   # CHF 3.50–4.50 for 2.5 kg bag → ~1.60/kg
    "sweet_potato":  3.20,
    "carrot":        1.80,   # Migros Tiefpreis ~1.50–2.00/kg
    "celery":        3.50,   # bunch ~1.50, ~430g → ~3.50/kg
    "onion":         1.50,
    "garlic":        8.00,   # ~1.00 per 125g bulb
    "tomato":        3.50,   # CHF 2.50–4.50/kg depending on variety
    "zucchini":      3.20,
    "bell_pepper":   5.00,   # ~1.50–2.00 per piece, ~300–400g
    "spinach":       8.00,   # 200g bag ~1.60
    "broccoli":      3.50,   # ~1 head ~500g → ~2.00 → ~4.00/kg; avg 3.50
    "mushroom":      9.00,   # 400g ~3.50
    "leek":          3.50,   # 500g ~1.80
    "cauliflower":   3.00,   # 800g head ~2.50
    "cucumber":      2.50,   # ~1.00 per piece, ~400g
    "lettuce":       4.00,   # 1 head ~200g, ~0.80
    "corn":          2.50,   # canned 425g ~1.10
    "peas":          4.00,   # frozen 750g ~3.00
    "green_beans":   4.50,   # 400g ~1.80
    "eggplant":      3.50,   # 1 piece ~400g, ~1.40
    "kale":          7.00,   # 200g bag ~1.40
    "beetroot":      2.50,   # 500g ~1.25
    "spring_onion":  5.00,   # bunch ~0.80, ~160g
    "ginger":       12.00,   # ~1.20 per 100g piece
    "pumpkin":       2.50,
    "white_cabbage": 1.50,
    "red_cabbage":   2.00,
    "fennel":        3.50,   # 1 bulb ~400g, ~1.40
    "asparagus":    12.00,   # 500g ~6.00 (CH asparagus)

    # ── Fruits (CHF/kg) ──────────────────────────────────────────────────────
    "apple":         3.60,   # Migros CH Äpfel ~3.50–3.80/kg
    "banana":        2.40,   # Migros ~2.20–2.60/kg (Tiefpreis)
    "mango":         5.00,   # ~2.50 per piece, ~500g
    "strawberry":    8.00,   # 500g ~4.00
    "blueberry":    14.00,   # 250g ~3.50
    "raspberry":    16.00,   # 125g ~2.00
    "cherry":       10.00,   # 500g ~5.00
    "peach":         4.00,   # ~1.00 per piece, ~250g
    "pear":          3.50,

    # ── Meat & Fish (CHF/kg) ─────────────────────────────────────────────────
    "chicken_breast": 13.80,  # M-Budget ~13.80/kg; Coop Prix Garantie 11.50/kg
    "ground_beef":   19.50,   # M-Classic ~9.75 per 500g
    "bacon":         20.00,   # ~5.00 per 200g pack
    "pork":          18.00,   # pork shoulder/neck typical price
    "salmon":        39.00,   # fresh fillet ~3.90 per 100g
    "tuna":          16.00,   # canned 155g ~2.50
    "shrimp":        30.00,   # frozen 300g ~9.00
    "lamb":          38.00,
    "turkey":        15.00,
    "sausage":       14.00,   # Bratwurst 4-pack M-Budget ~3.80 / ~270g → ~14/kg
    "ham":           18.00,   # 100g ~1.80
    "prosciutto":    38.00,   # 100g ~3.80
    "cod":           28.00,   # fillet ~2.80/100g

    # ── Dairy – UNIT-PRICED items (CHF per standard unit) ───────────────────
    # These are listed per typical purchase unit; calculate_costs()
    # will use them when the recipe amounts field gives a plain count.
    "egg":            0.45,   # 10-pack ~4.50 (Migros M-Budget)
    "milk":           1.05,   # per litre (M-Budget 2L ~2.05 → 1.03/L)
    "butter":         2.95,   # per 250g block (M-Budget)
    "cream":          2.50,   # per 200ml carton
    "heavy_cream":    4.80,   # per 500ml
    "cheese":         4.40,   # Emmentaler ~250g block ~4.40
    "mozzarella":     2.10,   # 150g ball (M-Classic)
    "parmesan":       3.50,   # 100g grated
    "yogurt":         0.80,   # 500g M-Budget nature
    "cream_cheese":   2.20,   # 200g
    "feta":           3.20,   # 200g pack
    "ricotta":        2.50,   # 250g
    "sour_cream":     1.80,   # 200g

    # ── Dairy – also provide per-kg fallback ─────────────────────────────────
    # (used when amounts are given in grams)
    "butter_kg":     11.80,   # CHF 2.95 per 250g
    "cheese_kg":     17.60,   # CHF 4.40 per 250g
    "mozzarella_kg": 14.00,
    "parmesan_kg":   35.00,
    "yogurt_kg":      1.60,
    "cream_cheese_kg": 11.00,
    "feta_kg":       16.00,
    "ricotta_kg":    10.00,
    "sour_cream_kg":  9.00,

    # ── Pantry / dry goods (CHF/kg) ──────────────────────────────────────────
    "pasta":          1.20,   # M-Budget Spaghetti 1kg
    "rice":           1.80,   # M-Budget 1kg
    "bread":          2.00,   # Ruchbrot 500g ~1.00
    "flour":          1.00,   # M-Budget 1kg
    "oats":           1.80,   # 500g ~0.90
    "lentils":        3.00,   # 500g ~1.50
    "chickpeas":      3.00,   # canned 400g ~1.20
    "tofu":           7.00,   # 400g ~2.80

    # ── Sauces, oils, condiments (CHF/kg or litre) ───────────────────────────
    "tomato_sauce":   2.50,   # Pelati 400g ~1.00
    "vegetable_broth": 2.00,  # 1L carton ~2.00
    "olive_oil":      7.40,   # M-Classic 1L ~7.40
    "oil":            3.50,   # Rapsöl 1L ~3.50
    "soy_sauce":      7.00,   # 250ml ~1.75
    "tahini":         9.00,   # 250g ~2.25
    "pesto":         10.00,   # 190g ~1.90
    "dijon_mustard":  5.00,   # 200g ~1.00
    "honey":         14.00,   # 500g ~7.00
    "mayonnaise":     5.00,   # 265g ~1.30
    "hot_sauce":      8.00,   # 150ml ~1.20
    "bbq_sauce":      5.00,   # 370g ~1.85
    "worcestershire": 6.00,   # 150ml ~0.90
    "coconut_milk":   3.50,   # 400ml can ~1.40

    # ── Piece-sold items (CHF per piece) ─────────────────────────────────────
    "lemon":          0.70,   # ~0.65–0.75 per piece
    "lime":           0.60,
    "avocado":        1.60,   # Migros ~1.50–2.00 per piece
}

# BACKWARD-COMPATIBLE ALIAS
# app.py originally imported INGREDIENT_VALUE_CHF.  We keep the old name
# pointing at the same table so existing code keeps working unchanged.
INGREDIENT_VALUE_CHF = INGREDIENT_PRICE_PER_KG_CHF

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