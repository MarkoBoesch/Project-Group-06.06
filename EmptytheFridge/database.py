# database.py
# This file sets up the database and saves/loads all data.
# We use SQLite - it is built directly into Python, no installation needed!
# -----------------------------------------------------------------------------

import sqlite3
import os

DB_NAME = "emptythefridge.db"


def get_connection():
    """Opens a connection to the database."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    """Creates all tables if they don't exist yet."""

    connection = get_connection()
    cursor = connection.cursor()

    # TABLE 1: Recipes
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            key      TEXT NOT NULL UNIQUE,
            name     TEXT NOT NULL
        )
    """)

    # TABLE 3: Cooking History
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


def populate_database():
    """Fills the database with recipes from recipes.py. Only runs if the database is empty."""

    from recipes import recipes, ingredient_dictionary

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    if count == 0:
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

    cursor.execute("SELECT COUNT(*) FROM ingredients")
    count_ingredients = cursor.fetchone()[0]

    if count_ingredients == 0:
        for key, name in ingredient_dictionary.items():
            cursor.execute("""
                INSERT INTO ingredients (key, name)
                VALUES (?, ?)
            """, (key, name))

    connection.commit()
    connection.close()


# -----------------------------------------------------------------------------
# READ FUNCTIONS
# -----------------------------------------------------------------------------

def load_all_recipes():
    """Returns all recipes from the database as a list of dictionaries."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes")
    results = cursor.fetchall()
    connection.close()
    return [dict(row) for row in results]


def load_recipe(recipe_id):
    """Returns a single recipe by its ID."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    result = cursor.fetchone()
    connection.close()
    return dict(result) if result else None


def load_all_ingredients():
    """Returns all ingredients from the dictionary."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ingredients ORDER BY name")
    results = cursor.fetchall()
    connection.close()
    return [dict(row) for row in results]


def load_history():
    """Returns the entire cooking history, newest first."""
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


# -----------------------------------------------------------------------------
# WRITE FUNCTIONS
# -----------------------------------------------------------------------------

def save_history(recipe_id, date, rating=None):
    """Saves a cooked recipe to the history."""
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
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE history SET rating = ? WHERE id = ?
    """, (rating, history_id))
    connection.commit()
    connection.close()


# -----------------------------------------------------------------------------
# Automatically set up database when this file is imported
# -----------------------------------------------------------------------------

create_database()
populate_database()
