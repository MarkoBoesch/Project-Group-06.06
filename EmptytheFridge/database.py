# database.py
# Sets up the SQLite database and saves/loads all data for the app.
#
#
# What this file does:
# - Creates the three tables the app needs: recipes, ingredients, history.
# - Seeds the ingredients table with the starter display names from
#   recipes.py so the search-page multiselect is never empty even before
#   any API recipes are loaded.
# - Provides the read functions used everywhere in the app to fetch
#   recipes, ingredients and the cooking history.
# - Provides the write functions used to log a cooked recipe and to
#   update its rating afterwards.
#
# The recipes table itself is filled exclusively by api_loader.py, which
# fetches data from TheMealDB. This file does NOT load any hardcoded
# recipes — recipes.py is now only used for lookup tables (display names,
# diet sets, prices, base ingredients).
#
# We use SQLite because it is built directly into Python (no installation
# needed) and stores everything in a single file (emptythefridge.db) that
# lives next to the code.
#
# Used by app.py on:
#   - every page (load_all_recipes, load_recipe, load_all_ingredients,
#     load_history) to display content.
#   - the History page (save_history, update_rating) when the user logs
#     a cooked recipe or rates one.
# Used by api_loader.py on:
#   - every start, since this file creates the recipes table that
#     api_loader.py writes API recipes into.
# -----------------------------------------------------------------------------

import sqlite3
# sqlite3 is built into Python — no pip install needed. It gives us a full
# SQL database in a single local file, which is perfect for a small app
# like this one.

DB_NAME = "emptythefridge.db"
# Single shared filename used by every connection. Defined as a constant
# so changing the database file name only needs one edit.


def get_connection():
    """Opens a connection to the database."""
    # row_factory = sqlite3.Row lets us access columns by name (row["id"])
    # instead of by index (row[0]), which makes the rest of the code much
    # easier to read. Every read function below relies on this.
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# CREATE DATABASE
# Builds the three tables the app needs. CREATE TABLE IF NOT EXISTS means
# this is safe to call on every run — the tables are only created once,
# and on later starts SQLite simply does nothing.

def create_database():
    """Creates all tables if they don't exist yet."""

    connection = get_connection()
    cursor = connection.cursor()

    # TABLE 1: Recipes
    # The main table. Each row is one recipe loaded from TheMealDB.
    # - id:             unique primary key, AUTOINCREMENT so api_loader.py
    #                   doesn't have to manage IDs itself.
    # - ingredients:    comma-separated list of ingredient keys. We store it
    #                   as a string instead of a separate join table to keep
    #                   the schema simple — the recommender splits it back
    #                   into a list when it needs to.
    # - amounts:        comma-separated "key:amount" pairs (e.g.
    #                   "potato:200g,onion:1"). Optional.
    # - allergens:      comma-separated list of allergens, used by the diet
    #                   filter on the search page.
    # - calories ... minerals: nutrition values used by the radar chart on
    #                   the Statistics page.
    # - api_id:         TheMealDB's own recipe ID. Used by api_loader.py to
    #                   detect duplicates so re-running the importer doesn't
    #                   insert the same recipe twice.
    # - api_source:     name of the API the recipe came from ("TheMealDB").
    #                   Useful for filtering / debugging.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT NOT NULL,
            ingredients       TEXT NOT NULL,
            amounts           TEXT,
            time_minutes      INTEGER NOT NULL,
            difficulty        TEXT NOT NULL,
            allergens         TEXT,
            calories          INTEGER,
            protein           INTEGER,
            carbohydrates     INTEGER,
            fat               INTEGER,
            fiber             INTEGER,
            vitamins          INTEGER,
            minerals          INTEGER,
            instructions      TEXT NOT NULL,
            api_id            TEXT UNIQUE,
            api_source        TEXT
        )
    """)

    # TABLE 2: Ingredient Dictionary
    # Maps an internal key (e.g. "bell_pepper") to a human-readable display
    # name (e.g. "Bell Pepper"). The multiselect on the "Enter Ingredients"
    # page reads from this table — if a key isn't in here, the user can't
    # select it, which is exactly why api_loader.py also writes to this
    # table whenever it imports a new API recipe.
    # - key is UNIQUE so INSERT OR IGNORE in api_loader.py can safely skip
    #   duplicates.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            key      TEXT NOT NULL UNIQUE,
            name     TEXT NOT NULL
        )
    """)

    # TABLE 3: Cooking History
    # One row per cooking event. The History page reads from this and the
    # recommender uses it to decide which recipe was cooked most recently.
    # - recipe_id: foreign-key-like reference to recipes.id (no FK constraint
    #              for simplicity, but the JOIN in load_history relies on it).
    # - date:      stored as a TEXT in "YYYY-MM-DD" format so chronological
    #              sorting works lexicographically.
    # - rating:    nullable on purpose — the user logs the recipe first
    #              and rates it later, so it starts as NULL.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id  INTEGER NOT NULL,
            date       TEXT NOT NULL,
            rating     INTEGER
        )
    """)

    connection.commit()
    connection.close()


# SEED INGREDIENT DICTIONARY
# Fills the ingredients table with the starter display names from recipes.py
# on the first run. We do this so that the multiselect on the search page
# already has friendly names like "Bell Pepper" available. api_loader.py
# adds more ingredients on top whenever a new API recipe introduces one.
#
# We deliberately do NOT seed any recipes here — those come exclusively
# from TheMealDB via api_loader.py.

def seed_ingredients():
    """Fills the ingredients table from recipes.py on the first run."""

    # Imported here (inside the function) instead of at the top of the file
    # to avoid a circular import: recipes.py is a pure data file, but
    # importing it eagerly would couple the database setup to the data
    # module load order.
    from recipes import ingredient_dictionary

    connection = get_connection()
    cursor = connection.cursor()

    # Only insert ingredients if the table is currently empty. This is the
    # "first run" check — on every later start the count is > 0 and we
    # skip the whole block.
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    count = cursor.fetchone()[0]

    if count == 0:
        # ingredient_dictionary is a {key: display_name} mapping in recipes.py.
        # We unpack it row by row into the ingredients table.
        for key, name in ingredient_dictionary.items():
            cursor.execute("""
                INSERT INTO ingredients (key, name)
                VALUES (?, ?)
            """, (key, name))

    connection.commit()
    connection.close()


# READ FUNCTIONS
# All functions that pull data out of the database. They each open a fresh
# connection, fetch what they need, close the connection, and return plain
# Python dictionaries (or a list of them). Returning dicts instead of
# sqlite3.Row objects means the rest of the app doesn't need to know
# anything about SQLite.

def load_all_recipes():
    """Returns all recipes from the database as a list of dictionaries."""
    # Used by app.py on the search page to get the full pool of recipes
    # to filter, and by recommender.py to build the ingredient vectors.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes")
    results = cursor.fetchall()
    connection.close()
    # Convert each Row object into a regular dict before returning, so
    # callers can treat the result like any other Python data structure.
    return [dict(row) for row in results]


def load_recipe(recipe_id):
    """Returns a single recipe by its ID."""
    # Used by app.py on the recipe detail view and on the Statistics page
    # (to look up the nutrition / ingredients of every cooked recipe).
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    result = cursor.fetchone()
    connection.close()
    # Returns None instead of a dict if no recipe with that ID exists.
    # Callers in app.py check for this with `if recipe:` before using it.
    return dict(result) if result else None


def load_all_ingredients():
    """Returns all ingredients from the dictionary."""
    # Used by app.py to populate the ingredient multiselect on the search
    # page. ORDER BY name keeps the dropdown alphabetically sorted, which
    # makes it easier for the user to scan.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ingredients ORDER BY name")
    results = cursor.fetchall()
    connection.close()
    return [dict(row) for row in results]


def load_history():
    """Returns the entire cooking history, newest first."""
    # JOIN with the recipes table so the caller gets the recipe name and
    # calories in the same query — saves us from running a second query
    # for every history entry on the History and Statistics pages.
    # ORDER BY date DESC means the most recently cooked recipe is the
    # first element of the returned list, which is exactly what the
    # recommender expects (it uses history_list[0] as the reference recipe).
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT history.id, history.recipe_id, history.date, history.rating,
               recipes.name, recipes.calories
        FROM history
        JOIN recipes ON history.recipe_id = recipes.id
        ORDER BY history.date DESC
    """)
    results = cursor.fetchall()
    connection.close()
    return [dict(row) for row in results]


# WRITE FUNCTIONS
# All functions that change data in the database. Both are called from
# app.py when the user interacts with the History page.

def save_history(recipe_id, date, rating=None):
    """Saves a cooked recipe to the history."""
    # Called when the user clicks "I cooked this" on a recipe. The rating
    # is optional and starts as None — the user typically rates the recipe
    # later via update_rating(). The id column auto-increments, so we don't
    # pass an ID ourselves.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO history (recipe_id, date, rating)
        VALUES (?, ?, ?)
    """, (recipe_id, date, rating))
    connection.commit()
    connection.close()


def update_rating(history_id, rating):
    """Updates the rating of a history entry."""
    # Called when the user picks a star rating for a previously logged
    # cooking event. We update by history_id (not recipe_id) so that
    # cooking the same recipe twice and rating each time independently
    # works correctly.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE history SET rating = ? WHERE id = ?
    """, (rating, history_id))
    connection.commit()
    connection.close()


# AUTOMATIC SETUP ON IMPORT
# These two calls run the moment any other file does `from database import ...`.
# That means by the time app.py reaches its first line of UI code, the
# database file exists, the tables are in place, and the ingredient
# dictionary is seeded. api_loader.py then fills the recipes table from
# TheMealDB.
#
# Both functions are idempotent (safe to call multiple times):
#   - create_database uses CREATE TABLE IF NOT EXISTS
#   - seed_ingredients checks COUNT(*) before inserting
# so re-running them on every app start has no negative side effects.

create_database()
seed_ingredients()
