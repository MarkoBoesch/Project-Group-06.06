# recommender.py
# Machine-learning logic for the recipe recommendations.
#
#
# What this file does:
# - Turns every recipe into a numerical vector (one slot per ingredient).
# - Uses scikit-learn's cosine_similarity to measure how alike two recipes are.
# - Recommends recipes that are similar to the user's last cooked recipe
#   OR similar to the user's highest-rated recipe, while skipping anything
#   they have already cooked too often.
#
# Used by app.py on:
#   - the "History and Recommendations" page (calculate_recommendations,
#     calculate_recommendations_by_rating)
#   - the recipe detail view ("You might also like...", similar_recipes)
# -----------------------------------------------------------------------------

from sklearn.metrics.pairwise import cosine_similarity
# cosine_similarity compares two vectors and returns a number between 0 and 1.
# 1 = identical ingredient pattern, 0 = no overlap at all.

import numpy as np
# numpy is needed because cosine_similarity expects numerical arrays.


# RECIPES TO NUMBERS (VECTORIZATION)
# Converts the recipes into a matrix of 0s and 1s so the ML library can work
# with them. Each row is one recipe, each column is one ingredient.

def recipes_to_numbers(all_recipes, all_ingredient_keys):
    """
    Converts recipes into a table of zeros and ones.
    1 = ingredient is present in the recipe, 0 = not present.
    """
    table = []

    # Go through every recipe and build one row of 0s/1s for it.
    for recipe in all_recipes:
        row = []
        # Ingredients are stored as a comma-separated string in the DB,
        # so we split them back into a list (e.g. "tomato, onion, garlic"
        # becomes ["tomato", " onion", " garlic"]).
        recipe_ingredients = recipe["ingredients"].split(",")

        # For every known ingredient, check if this recipe contains it.
        # The order of all_ingredient_keys is the same for every recipe,
        # so column 5 always means the same ingredient across all rows.
        for ingredient_key in all_ingredient_keys:
            if ingredient_key in recipe_ingredients:
                row.append(1)
            else:
                row.append(0)

        table.append(row)

    # Convert the Python list-of-lists into a numpy array because
    # cosine_similarity from scikit-learn expects numpy arrays.
    return np.array(table)


# CALCULATE RECOMMENDATIONS (BASED ON LAST COOKED RECIPE)
# Main recommendation function used on the "History and Recommendations" page.
# Takes the user's cooking history, finds the most recently cooked recipe and
# recommends recipes that are similar to it (but not yet cooked too often).

def calculate_recommendations(history_list, all_recipes, num_recommendations=5):
    """
    Calculates recipe recommendations based on the cooking history.

    history_list        = list of history dictionaries from the database
    all_recipes         = list of all recipe dictionaries from the database
    num_recommendations = how many recommendations to return
    """

    # Safety net for an empty history. In practice app.py already catches
    # this case and shows an info banner instead of calling this function,
    # so this only protects against the function being called from elsewhere.
    if len(history_list) == 0:
        return all_recipes[:num_recommendations]

    # COLLECT ALL UNIQUE INGREDIENTS
    # Walk through every recipe and build a list of all distinct ingredient
    # keys. This list defines the "columns" of our number table, e.g. if 
    # there are 60 unique ingredients across all recipes, every recipe will 
    # be represented by a 60-dimensional vector.
    all_ingredient_keys = []
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            ingredient = ingredient.strip()
            if ingredient not in all_ingredient_keys:
                all_ingredient_keys.append(ingredient)

    # Convert recipes to number vectors.
    number_table = recipes_to_numbers(all_recipes, all_ingredient_keys)

    # IDS OF ALREADY COOKED RECIPES
    # Extract just the recipe IDs from the history entries so we can later
    # check how often a specific recipe was cooked.
    cooked_ids = [entry["recipe_id"] for entry in history_list]

    # Count how often each recipe was cooked. We don't want to recommend
    # something the user already cooked three or more times because it would
    # feel repetitive even if the algorithm thinks it's a perfect match.
    id_counter = {}
    for rid in cooked_ids:
        id_counter[rid] = id_counter.get(rid, 0) + 1

    cooked_too_often = [rid for rid, count in id_counter.items() if count > 2]

    # FIND THE MOST RECENT RECIPE
    # The history is sorted newest first, so the first entry is the most
    # recently cooked recipe. We use it as the reference recipe and compare 
    # every other recipe against it.
    last_recipe_id = cooked_ids[0]

    # Find the row index of this reference recipe in the number_table so we
    # know which vector to compare against.
    last_index = None
    for i, recipe in enumerate(all_recipes):
        if recipe["id"] == last_recipe_id:
            last_index = i
            break

    # Safety net in case the last cooked recipe is no longer in the database. 
    # In practice app.py guards against this before calling the function.
    if last_index is None:
        return all_recipes[:num_recommendations]

    # COSINE SIMILARITY (THE ML PART)
    # Compare the reference recipe's vector to every other recipe's vector.
    # The result is an array of similarity scores, one per recipe.
    # Higher score = more similar ingredient pattern.
    similarities = cosine_similarity(
        [number_table[last_index]],
        number_table
    )[0]

    # np.argsort returns the indices that would sort the array. The [::-1]
    # reverses it, so we get indices from most to least similar.
    sorted_indices = np.argsort(similarities)[::-1]

    # BUILD THE RECOMMENDATION LIST
    # Walk through the sorted list and pick the top recommendations,
    # while skipping the reference recipe itself and any recipe cooked too often.
    recommendations = []
    for index in sorted_indices:
        recipe = all_recipes[index]

        # Skip the reference recipe (it would always be the most similar to itself).
        if recipe["id"] == last_recipe_id:
            continue
        # Skip recipes that were already cooked more than twice (variety).
        if recipe["id"] in cooked_too_often:
            continue

        recommendations.append(recipe)

        # Stop once we have enough recommendations.
        if len(recommendations) >= num_recommendations:
            break

    # Edge case: if too many recipes were filtered out (e.g. the user has
    # cooked almost everything more than twice), the list might still be
    # shorter than requested. In that case we top it up with any remaining
    # recipes so the user always sees a full set of suggestions.
    if len(recommendations) < num_recommendations:
        for recipe in all_recipes:
            if recipe not in recommendations and recipe["id"] != last_recipe_id:
                recommendations.append(recipe)
            if len(recommendations) >= num_recommendations:
                break

    return recommendations


# CALCULATE RECOMMENDATIONS (BASED ON HIGHEST RATED RECIPE)
# Second recommendation function used on the "History and Recommendations" page.
# Takes the user's cooking history, finds the recipe the user rated highest and
# recommends recipes that are similar to it (but not yet cooked too often).
# Same ML logic as calculate_recommendations, only the reference recipe differs:
# instead of "the last one cooked" we pick "the one the user liked most".

def calculate_recommendations_by_rating(history_list, all_recipes, num_recommendations=4):
    """
    Calculates recipe recommendations based on the user's ratings.

    history_list        = list of history dictionaries from the database
    all_recipes         = list of all recipe dictionaries from the database
    num_recommendations = how many recommendations to return

    Returns an empty list when the user has not rated any recipe yet, so that
    app.py can display a warning telling the user to cook and rate first.
    """

    # Empty history -> nothing to base recommendations on. Returning [] lets
    # app.py show the warning ("rate your meals first or cook first").
    if len(history_list) == 0:
        return []

    # FIND THE HIGHEST-RATED ENTRY
    # Walk through the history and keep the entry with the best rating.
    # Entries without a rating (rating is None) are ignored, because we
    # can only rely on stars the user actually gave.
    rated_entries = [entry for entry in history_list if entry["rating"]]

    # No rating yet -> return [] so app.py can show the warning instead of
    # blindly recommending random recipes.
    if len(rated_entries) == 0:
        return []

    # Pick the entry with the highest rating. Ties are broken by recency:
    # because history is already sorted newest-first, max() returns the
    # most recent entry among those that share the top rating.
    best_entry = max(rated_entries, key=lambda entry: entry["rating"])
    best_recipe_id = best_entry["recipe_id"]

    # COLLECT ALL UNIQUE INGREDIENTS
    # Same logic as in calculate_recommendations: build the column list
    # for the number table.
    all_ingredient_keys = []
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            ingredient = ingredient.strip()
            if ingredient not in all_ingredient_keys:
                all_ingredient_keys.append(ingredient)

    # Convert recipes to number vectors.
    number_table = recipes_to_numbers(all_recipes, all_ingredient_keys)

    # IDS OF ALREADY COOKED RECIPES (for the "cooked too often" filter)
    cooked_ids = [entry["recipe_id"] for entry in history_list]

    id_counter = {}
    for rid in cooked_ids:
        id_counter[rid] = id_counter.get(rid, 0) + 1

    cooked_too_often = [rid for rid, count in id_counter.items() if count > 2]

    # Find the row index of the highest-rated recipe in the number_table so
    # we know which vector to compare against.
    best_index = None
    for i, recipe in enumerate(all_recipes):
        if recipe["id"] == best_recipe_id:
            best_index = i
            break

    # Safety net in case the rated recipe is no longer in the database.
    if best_index is None:
        return []

    # COSINE SIMILARITY (THE ML PART)
    # Compare the highest-rated recipe's vector to every other recipe's vector.
    similarities = cosine_similarity(
        [number_table[best_index]],
        number_table
    )[0]

    # Sort indices from most to least similar.
    sorted_indices = np.argsort(similarities)[::-1]

    # BUILD THE RECOMMENDATION LIST
    # Same filtering rules as the other function: skip the reference recipe
    # itself and skip anything cooked more than twice.
    recommendations = []
    for index in sorted_indices:
        recipe = all_recipes[index]

        if recipe["id"] == best_recipe_id:
            continue
        if recipe["id"] in cooked_too_often:
            continue

        recommendations.append(recipe)

        if len(recommendations) >= num_recommendations:
            break

    # Top-up if too many recipes were filtered out, so the user always
    # sees a full set of suggestions.
    if len(recommendations) < num_recommendations:
        for recipe in all_recipes:
            if recipe not in recommendations and recipe["id"] != best_recipe_id:
                recommendations.append(recipe)
            if len(recommendations) >= num_recommendations:
                break

    return recommendations


# SIMILAR RECIPES
# Used on the recipe detail page ("You might also like..."). Takes a single
# recipe ID and returns a few recipes whose ingredient pattern is closest to it.

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
