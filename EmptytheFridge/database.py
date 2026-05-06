# database.py
# Sets up the SQLite database and saves/loads all data for the app.
#
#
# What this file does:
# - Creates the three tables the app needs: recipes, ingredients, history.
# - Fills the recipes and ingredients tables on the very first run from
#   the hardcoded data in recipes.py (later, api_loader.py adds more
#   recipes on top from TheMealDB).
# - Provides the read functions used everywhere in the app to fetch
#   recipes, ingredients and the cooking history.
# - Provides the write functions used to log a cooked recipe and to
#   update its rating afterwards.
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
#   - first start (indirectly), since this file creates the tables that
#     api_loader.py then writes additional API recipes into.
# -----------------------------------------------------------------------------

import sqlite3
# sqlite3 is built into Python — no pip install needed. It gives us a full
# SQL database in a single local file, which is perfect for a small app
# like this one.

import os
# os is imported for path handling. We don't currently use it, but it's
# kept here because future features (e.g. resetting the database, checking
# whether the file exists) typically need it.

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
    # The main table. Each row is one recipe.
    # - id:             unique primary key (no AUTOINCREMENT because recipes.py
    #                   provides its own IDs, and api_loader.py picks IDs >= 1000
    #                   to stay out of the way of the hardcoded ones).
    # - ingredients:    comma-separated list of ingredient keys. We store it
    #                   as a string instead of a separate join table to keep
    #                   the schema simple — the recommender splits it back
    #                   into a list when it needs to.
    # - amounts:        comma-separated "key:amount" pairs (e.g.
    #                   "potato:200g,onion:1"). Optional — older recipes can
    #                   leave it empty.
    # - allergens:      comma-separated list of allergens, used by the diet
    #                   filter on the search page.
    # - calories ... minerals: nutrition values used by the radar chart on
    #                   the Statistics page.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id                INTEGER PRIMARY KEY,
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
            instructions      TEXT NOT NULL
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


# POPULATE DATABASE
# Fills the recipes and ingredients tables with the hardcoded data from
# recipes.py — but only on the first run. The COUNT(*) check makes sure
# we don't insert the same recipes again on every app start.

def populate_database():
    """Fills the database with recipes from recipes.py. Only runs if the database is empty."""

    # Imported here (inside the function) instead of at the top of the file
    # to avoid a circular import: recipes.py is a pure data file, but
    # importing it eagerly would couple the database setup to the data
    # module load order.
    from recipes import recipes, ingredient_dictionary

    connection = get_connection()
    cursor = connection.cursor()

    # Only insert recipes if the table is currently empty. This is the
    # "first run" check — on every later start the count is > 0 and we
    # skip the whole block.
    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert each recipe from recipes.py one row at a time.
        # The ingredients list is joined into a comma-separated string
        # because that is the format the rest of the app expects when
        # reading from the database.
        for r in recipes:
            cursor.execute("""
                INSERT INTO recipes (
                    id, name, ingredients, amounts,
                    time_minutes, difficulty,
                    allergens, calories, protein, carbohydrates,
                    fat, fiber, vitamins, minerals,
                    instructions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["id"],
                r["name"],
                ",".join(r["ingredients"]),
                r["amounts"],
                r["time_minutes"],
                r["difficulty"],
                r["allergens"],
                r["calories"],
                r["protein"],
                r["carbohydrates"],
                r["fat"],
                r["fiber"],
                r["vitamins"],
                r["minerals"],
                r["instructions"]
            ))

    # Same "first run" pattern for the ingredients table. We check it
    # separately from the recipes table because the two could in theory
    # get out of sync (e.g. if the recipes insert failed but the
    # ingredients insert didn't), and this way each one self-heals.
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    count_ingredients = cursor.fetchone()[0]

    if count_ingredients == 0:
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
# database file exists, the tables are in place, and the hardcoded recipes
# from recipes.py are already loaded. api_loader.py then adds API recipes
# on top of this baseline.
#
# Both functions are idempotent (safe to call multiple times):
#   - create_database uses CREATE TABLE IF NOT EXISTS
#   - populate_database checks COUNT(*) before inserting
# so re-running them on every app start has no negative side effects.

create_database()
populate_database()
