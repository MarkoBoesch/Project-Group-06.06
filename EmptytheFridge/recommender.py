# recommender.py
# This file contains the machine learning logic for recipe recommendations.
#
# NOTE: This file uses Claude-assisted ML logic.
#
# What does this file do?
# 1. It looks at which recipes the user has cooked in the past.
# 2. It converts recipes into numbers (which ingredients does it have?).
# 3. It compares these numbers with scikit-learn to find similar recipes.
# 4. It recommends recipes that are similar but not repeated too often.
# -----------------------------------------------------------------------------

from sklearn.metrics.pairwise import cosine_similarity
# cosine_similarity measures how similar two recipes are based on their ingredients.

import numpy as np
# numpy is needed for the number arrays.


def recipes_to_numbers(all_recipes, all_ingredient_keys):
    """
    Converts recipes into a table of zeros and ones.
    1 = ingredient present in recipe, 0 = not present.
    """
    table = []

    for recipe in all_recipes:
        row = []
        recipe_ingredients = recipe["ingredients"].split(",")

        for ingredient_key in all_ingredient_keys:
            if ingredient_key in recipe_ingredients:
                row.append(1)
            else:
                row.append(0)

        table.append(row)

    return np.array(table)


def calculate_recommendations(history_list, all_recipes, num_recommendations=5):
    """
    Calculates recipe recommendations based on the cooking history.

    history_list       = list of history dictionaries from the database
    all_recipes        = list of all recipe dictionaries from the database
    num_recommendations = how many recommendations to return
    """

    if len(history_list) == 0:
        return all_recipes[:num_recommendations]

    # Collect all unique ingredient keys
    all_ingredient_keys = []
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            ingredient = ingredient.strip()
            if ingredient not in all_ingredient_keys:
                all_ingredient_keys.append(ingredient)

    # Convert recipes to number vectors
    number_table = recipes_to_numbers(all_recipes, all_ingredient_keys)

    # Collect IDs of already cooked recipes
    cooked_ids = [entry["recipe_id"] for entry in history_list]

    # Track recipes cooked more than twice
    id_counter = {}
    for rid in cooked_ids:
        id_counter[rid] = id_counter.get(rid, 0) + 1

    cooked_too_often = [rid for rid, count in id_counter.items() if count > 2]

    # Find the most recently cooked recipe (history is newest first)
    last_recipe_id = cooked_ids[0]

    last_index = None
    for i, recipe in enumerate(all_recipes):
        if recipe["id"] == last_recipe_id:
            last_index = i
            break

    if last_index is None:
        return all_recipes[:num_recommendations]

    # Calculate cosine similarity between last recipe and all others
    similarities = cosine_similarity(
        [number_table[last_index]],
        number_table
    )[0]

    # Sort recipes by similarity (highest first)
    sorted_indices = np.argsort(similarities)[::-1]

    recommendations = []
    for index in sorted_indices:
        recipe = all_recipes[index]

        if recipe["id"] == last_recipe_id:
            continue
        if recipe["id"] in cooked_too_often:
            continue

        recommendations.append(recipe)

        if len(recommendations) >= num_recommendations:
            break

    # Fill up if not enough recommendations found
    if len(recommendations) < num_recommendations:
        for recipe in all_recipes:
            if recipe not in recommendations and recipe["id"] != last_recipe_id:
                recommendations.append(recipe)
            if len(recommendations) >= num_recommendations:
                break

    return recommendations


def similar_recipes(recipe_id, all_recipes, count=3):
    """
    Finds recipes similar to a specific recipe.
    Used on the recipe detail page.
    """

    all_ingredient_keys = []
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            ingredient = ingredient.strip()
            if ingredient not in all_ingredient_keys:
                all_ingredient_keys.append(ingredient)

    number_table = recipes_to_numbers(all_recipes, all_ingredient_keys)

    target_index = None
    for i, recipe in enumerate(all_recipes):
        if recipe["id"] == recipe_id:
            target_index = i
            break

    if target_index is None:
        return []

    similarities = cosine_similarity(
        [number_table[target_index]],
        number_table
    )[0]

    sorted_indices = np.argsort(similarities)[::-1]

    similar = []
    for index in sorted_indices:
        if all_recipes[index]["id"] != recipe_id:
            similar.append(all_recipes[index])
        if len(similar) >= count:
            break

    return similar
