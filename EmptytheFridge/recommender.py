# recommender.py
# Machine-learning logic for the recipe recommendations.
#
#
# What this file does:
# - Turns every recipe into a numerical vector (one slot per ingredient).
# - Uses scikit-learn's cosine_similarity to measure how alike two recipes are.
# - Recommends recipes either similar to the user's last cooked recipe
#   OR similar to a "user taste profile" built as a weighted mean of all
#   rated recipes (rating used as the weight). Recipes already cooked too
#   often are skipped in both cases.
#
# Used by app.py on:
#   - the "History and Recommendations" page (calculate_recommendations,
#     calculate_recommendations_by_rating)
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


# CALCULATE RECOMMENDATIONS (BASED ON THE USER'S TASTE PROFILE)
# Second recommendation function used on the "History and Recommendations" page.
# Instead of comparing against a single recipe, this function builds a
# "user taste profile" vector by taking the WEIGHTED MEAN of all rated recipe
# vectors, with each recipe's star rating used as the weight. A 5-star recipe
# therefore pulls the profile 5x as hard as a 1-star recipe.
#
# Mathematically:
#       profile = ( r1*v1 + r2*v2 + ... + rn*vn ) / ( r1 + r2 + ... + rn )
# where ri is the rating (1-5) and vi is the 0/1 ingredient vector of recipe i.
#
# We then run the same cosine_similarity from scikit-learn between this
# profile vector and every recipe in the database. The ML toolkit (vectors,
# cosine similarity, weighted averaging) is exactly what the lecture covers;
# the only new step is combining several rated vectors into one reference
# vector before comparing.

def calculate_recommendations_by_rating(history_list, all_recipes, num_recommendations=4, exclude_ids=None):
    """
    Calculates recipe recommendations based on the user's ratings.

    history_list        = list of history dictionaries from the database
    all_recipes         = list of all recipe dictionaries from the database
    num_recommendations = how many recommendations to return
    exclude_ids         = optional list of recipe IDs to exclude (used by
                          app.py to avoid showing the same recipes that were
                          already displayed in the "similar recipes" section)

    Returns an empty list when the user has not rated any recipe yet, so that
    app.py can display a warning telling the user to cook and rate first.
    """

    # Default for the optional exclusion list. Using None as the default and
    # then converting to [] avoids the classic Python "mutable default" trap
    # where every call would share the same list.
    if exclude_ids is None:
        exclude_ids = []

    # Empty history -> nothing to base recommendations on. Returning [] lets
    # app.py show the warning ("cook a recipe first").
    if len(history_list) == 0:
        return []

    # FIND ALL RATED ENTRIES
    # Walk through the history and keep every entry that has a rating set.
    # Entries without a rating (rating is None) are ignored, because we
    # can only rely on stars the user actually gave.
    rated_entries = [entry for entry in history_list if entry["rating"]]

    # No rating yet -> return [] so app.py can show the "rate first" warning
    # instead of blindly recommending random recipes.
    if len(rated_entries) == 0:
        return []

    # COLLECT ALL UNIQUE INGREDIENTS
    # Same logic as in calculate_recommendations: build the column list
    # for the number table.
    all_ingredient_keys = []
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            ingredient = ingredient.strip()
            if ingredient not in all_ingredient_keys:
                all_ingredient_keys.append(ingredient)

    # Convert all recipes to 0/1 number vectors.
    number_table = recipes_to_numbers(all_recipes, all_ingredient_keys)

    # BUILD AN ID -> ROW INDEX LOOKUP
    # We need to translate "recipe ID 42" into "row 17 of the number table"
    # several times below. Building the dict once is cheaper than scanning
    # all_recipes in a loop every time.
    id_to_index = {}
    for i, recipe in enumerate(all_recipes):
        id_to_index[recipe["id"]] = i

    # COMPUTE THE WEIGHTED PROFILE VECTOR (THE ML PART, STEP 1)
    # For every rated entry, look up its recipe vector and add it to a running
    # sum, multiplied by the rating. We also accumulate the sum of ratings so
    # we can divide at the end (= weighted average).
    profile_vector = np.zeros(len(all_ingredient_keys))
    weight_sum = 0
    rated_recipe_ids = []  # remember which recipes contributed to the profile

    for entry in rated_entries:
        recipe_id = entry["recipe_id"]
        rating = entry["rating"]

        # Skip rated entries whose recipe is no longer in the database.
        if recipe_id not in id_to_index:
            continue

        row_index = id_to_index[recipe_id]
        # Add the rating-weighted vector to the running sum.
        # number_table[row_index] is a 0/1 vector; multiplying by the rating
        # turns its 1s into the rating value (e.g. 5 for a 5-star recipe).
        profile_vector += rating * number_table[row_index]
        weight_sum += rating
        rated_recipe_ids.append(recipe_id)

    # Safety net: if every rated recipe has disappeared from the database,
    # there is nothing to build a profile from.
    if weight_sum == 0:
        return []

    # Divide by the total weight to get the actual weighted MEAN. This keeps
    # the profile vector's values in roughly [0, 1] just like the original
    # 0/1 vectors, which makes cosine similarity behave consistently.
    profile_vector = profile_vector / weight_sum

    # COSINE SIMILARITY (THE ML PART, STEP 2)
    # Compare the user's taste profile vector to every recipe's vector.
    # Same library call as in calculate_recommendations -- the only difference
    # is that the reference vector is now a continuous weighted average
    # instead of a single recipe's 0/1 vector.
    similarities = cosine_similarity(
        [profile_vector],
        number_table
    )[0]

    # IDS OF ALREADY COOKED RECIPES (for the "cooked too often" filter)
    cooked_ids = [entry["recipe_id"] for entry in history_list]

    id_counter = {}
    for rid in cooked_ids:
        id_counter[rid] = id_counter.get(rid, 0) + 1

    cooked_too_often = [rid for rid, count in id_counter.items() if count > 2]

    # Sort indices from most to least similar.
    sorted_indices = np.argsort(similarities)[::-1]

    # BUILD THE RECOMMENDATION LIST
    # Filtering rules:
    #   1. Skip recipes the user has already rated -- those built the profile
    #      and would dominate the top of the list, defeating the purpose.
    #   2. Skip anything cooked more than twice (variety).
    #   3. Skip anything already shown in the first recommendations section
    #      (passed in via exclude_ids) so we don't display duplicates.
    recommendations = []
    for index in sorted_indices:
        recipe = all_recipes[index]

        if recipe["id"] in rated_recipe_ids:
            continue
        if recipe["id"] in cooked_too_often:
            continue
        if recipe["id"] in exclude_ids:
            continue

        recommendations.append(recipe)

        if len(recommendations) >= num_recommendations:
            break

    # Top-up if too many recipes were filtered out, so the user always
    # sees a full set of suggestions. The same exclusion rules apply, but
    # we drop the cooked_too_often filter here -- this branch only runs
    # in the rare case where the strict filters wiped out the list.
    if len(recommendations) < num_recommendations:
        for recipe in all_recipes:
            if recipe in recommendations:
                continue
            if recipe["id"] in rated_recipe_ids:
                continue
            if recipe["id"] in exclude_ids:
                continue
            recommendations.append(recipe)
            if len(recommendations) >= num_recommendations:
                break

    return recommendations
