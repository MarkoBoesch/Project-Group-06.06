# recommender.py
# Machine-learning logic for the recipe recommendations.
#
#
# What this file does:
# - Turns every recipe into a numerical feature vector (ingredients +
#   vegetarian/vegan flags + preparation time + difficulty).
# - Generates 60 synthetic rating entries representing one realistic user
#   taste profile so the model has data to learn from BEFORE the real user
#   has rated anything ("cold-start" problem).
# - Trains a Random Forest regressor (sklearn) on those entries plus any
#   real ratings the user has given via the History page.
# - Newer ratings are weighted more strongly than older ratings, so the
#   model gradually shifts toward the real user's taste as data accumulates.
# - Predicts a 1-5 star rating for every candidate recipe so the search
#   page can rank recipes by "what the user is most likely to enjoy".
# - Evaluates the model on a held-out 20% test split (slide 55 of the
#   lecture) and reports Mean Absolute Error (MAE) and Mean Squared Error
#   (MSE) so the user can see how reliable the predictions actually are.
#
# Used by app.py on:
#   - the "Enter Ingredients" search page (recommend_top_recipes), where
#     the top 5 ranked recipes are shown after the user clicks "Find Recipes".
#   - the "Enter Ingredients" search page (evaluate_recommender), where
#     the model's accuracy metrics are shown above the recommendations.
# -----------------------------------------------------------------------------

import numpy as np
# numpy is needed because scikit-learn expects numerical arrays as input
# (X, y, sample_weight). We also use it to build the feature matrix.

from sklearn.ensemble import RandomForestRegressor
# RandomForestRegressor predicts a continuous number (here: a star rating
# between 1 and 5). It works by training many small decision trees on
# different random subsets of the data and averaging their predictions.
# This averaging makes the prediction more reliable than a single tree
# and is exactly the "wisdom of the crowd" effect we covered in the lecture.

from sklearn.model_selection import train_test_split
# train_test_split is the standard sklearn helper for splitting a dataset
# into training and test halves. The lecture uses it on slide 59.

from sklearn.metrics import mean_absolute_error, mean_squared_error
# Two textbook metrics for regression problems. MAE is in stars and easy
# to interpret ("off by 0.6 stars on average"). MSE is in stars² and
# penalizes large errors more heavily than small ones.

from constants import NON_VEGETARIAN_INGREDIENTS, NON_VEGAN_INGREDIENTS
# These two sets are reused so we can derive a "is vegetarian" and
# "is vegan" flag for every recipe. The recipes table doesn't store
# these flags, so we compute them on the fly from the ingredient list.


# DIFFICULTY ENCODING
# The Random Forest expects numbers, not strings. We map our three
# difficulty levels to small integers so they can be used as a feature.
DIFFICULTY_MAP = {"easy": 1, "medium": 2, "hard": 3}


# FEATURE VECTOR BUILDER
# Converts a single recipe (dict from the database) into a numeric feature
# vector. Every recipe has:
#   - one 0/1 column per ingredient (multi-hot encoding)
#   - one column for "is vegetarian"
#   - one column for "is vegan"
#   - one column for preparation time in minutes
#   - one column for difficulty (1=easy, 2=medium, 3=hard)
#
# all_ingredient_keys is the master list of every ingredient that appears
# anywhere in the recipe database. We pass it in so every recipe ends up
# with the same number of columns in the same order. Without this, two
# recipes could end up with different vector lengths and the model would
# refuse to train.

def build_recipe_vector(recipe, all_ingredient_keys):
    """Returns a 1D numpy array of features for a single recipe."""

    # Split the comma-separated ingredient string back into a clean list.
    # Same logic as in app.py — a recipe stores ingredients as
    # "potato,onion,garlic" and we want the individual keys.
    recipe_ingredients = [i.strip() for i in recipe["ingredients"].split(",")]

    # Multi-hot ingredient encoding: one column per known ingredient,
    # 1 if this recipe contains it, 0 otherwise. Identical to the lecture's
    # "feature representation" idea (slide 47).
    ingredient_flags = []
    for key in all_ingredient_keys:
        if key in recipe_ingredients:
            ingredient_flags.append(1)
        else:
            ingredient_flags.append(0)

    # Vegetarian / vegan flags derived from the ingredient list.
    # If ANY non-vegetarian ingredient is present, the recipe is not
    # vegetarian. Same idea for vegan, just with a stricter set.
    is_vegetarian = 1
    is_vegan = 1
    for ingredient in recipe_ingredients:
        if ingredient in NON_VEGETARIAN_INGREDIENTS:
            is_vegetarian = 0
        if ingredient in NON_VEGAN_INGREDIENTS:
            is_vegan = 0

    # Preparation time and difficulty as plain numbers.
    # If the API didn't store a difficulty for this recipe, we default to
    # "medium" (2) so the model still has a value to work with.
    time_minutes = recipe["time_minutes"] if recipe["time_minutes"] else 30
    difficulty_num = DIFFICULTY_MAP.get(recipe["difficulty"], 2)

    # Combine everything into a single numeric vector. The order MUST be
    # identical for every recipe — that's why we use the master ingredient
    # list above.
    features = ingredient_flags + [is_vegetarian, is_vegan,
                                   time_minutes, difficulty_num]
    return np.array(features, dtype=float)


# COLLECT ALL UNIQUE INGREDIENT KEYS
# Walks through every recipe and builds a single deduplicated list of all
# ingredient keys that exist in the database. This is the master list used
# above so every feature vector has the same length and column order.

def collect_all_ingredient_keys(all_recipes):
    """Returns a sorted list of every distinct ingredient key in the recipes."""
    seen = set()
    for recipe in all_recipes:
        for ingredient in recipe["ingredients"].split(","):
            key = ingredient.strip()
            if key:
                seen.add(key)
    # sorted() makes the order deterministic — important so the same recipe
    # always produces the same feature vector across app restarts.
    return sorted(seen)


# SYNTHETIC TRAINING DATA — RICH PERSONA
# The persona is an Italian/Mediterranean-leaning home cook who:
#   - Loves Italian, Mediterranean and fresh-vegetable ingredients
#   - Likes some lighter Asian and Middle-Eastern flavours
#   - Dislikes very heavy meats (bacon, sausage, pork) and most seafood
#   - Is lukewarm on baking-only ingredients (flour, sugar, butter)
#
# The richer set (~30 loved + ~20 disliked instead of the original 11+9)
# gives the Random Forest a more nuanced training signal. Each recipe gets
# a more meaningful score, so the 5 rating buckets are clearly separated
# instead of bunching at the middle. This produces a stronger pattern for
# the model to learn — small persona = noisy training data, rich persona
# = more learnable structure.

LOVED_INGREDIENTS = {
    # Italian/Mediterranean core
    "tomato", "mozzarella", "basil", "olive_oil", "pasta", "garlic",
    "onion", "parmesan", "ricotta", "pesto",
    # Fresh vegetables (loves vegetable-forward dishes)
    "spinach", "bell_pepper", "zucchini", "broccoli", "kale",
    "asparagus", "fennel", "leek",
    # Citrus and fresh accents
    "lemon", "lime",
    # Light Asian & Middle Eastern flavours
    "ginger", "tofu", "chickpeas", "lentils",
    # Eggs & light dairy (vegetarian-leaning)
    "egg", "yogurt", "feta",
    # Light grains
    "rice", "oats",
    # Fruits used in cooking
    "avocado",
}

DISLIKED_INGREDIENTS = {
    # Heavy / cured meats
    "bacon", "sausage", "pork", "ham", "prosciutto", "ground_beef",
    # Seafood (the persona doesn't enjoy fish/seafood at all)
    "shrimp", "salmon", "tuna", "cod",
    # Strong/heavy flavours the persona avoids
    "lamb", "turkey",
    # Heavy / processed condiments
    "mayonnaise", "bbq_sauce", "hot_sauce", "worcestershire",
    # Sweet baking ingredients (persona prefers savoury cooking)
    "sugar", "honey",
    # Some heavy dairy
    "heavy_cream", "sour_cream",
}


def generate_synthetic_history(all_recipes, rng_seed=42):
    """
    Returns a list of 60 synthetic history entries shaped like the real
    history rows in db.py:
        {"recipe_id": int, "rating": 1-5, "date": "YYYY-MM-DD"}

    The 'date' is only used for recency weighting — older synthetic
    entries get smaller weights than newer ones during training.

    The 60-entry size (12 per star level × 5 levels) gives the Random
    Forest enough data per rating class to learn meaningful splits while
    still leaving a reasonable 20% (12 entries) for the held-out test set.
    """
    rng = np.random.default_rng(rng_seed)

    # Score every recipe against the persona's preferences.
    scored = []
    for recipe in all_recipes:
        recipe_ingredients = [i.strip() for i in recipe["ingredients"].split(",")]

        # +1 for each loved ingredient, -1 for each disliked one.
        score = 0
        for ingredient in recipe_ingredients:
            if ingredient in LOVED_INGREDIENTS:
                score += 1
            if ingredient in DISLIKED_INGREDIENTS:
                score -= 1

        # Add a tiny bit of random noise so identical-scoring recipes don't
        # all collapse to the same rating. This makes the data look more
        # like what real-world ratings look like.
        score = score + rng.normal(0, 0.5)
        scored.append((recipe, score))

    # Sort by score (highest first) and convert the score into a star rating.
    # We split the recipe list into 5 buckets so we get a healthy mix of
    # ratings from 1 to 5 — the model NEEDS to see low ratings too,
    # otherwise it can't learn what "I won't like this" looks like.
    scored.sort(key=lambda x: x[1], reverse=True)

    history = []
    target_per_bucket = 12   # 12 entries per star level × 5 stars = 60 total

    # Top 20% → 5 stars, next 20% → 4 stars, … bottom 20% → 1 star.
    bucket_size = max(1, len(scored) // 5)

    for star in [5, 4, 3, 2, 1]:
        # Slice out this bucket from the score-sorted list.
        start = (5 - star) * bucket_size
        end = start + bucket_size
        bucket = scored[start:end]

        # Sample up to target_per_bucket recipes from this bucket. If the
        # database is small and the bucket has fewer than 12 entries, we
        # take whatever is there.
        sample_size = min(target_per_bucket, len(bucket))
        if sample_size == 0:
            continue
        chosen_indices = rng.choice(len(bucket), size=sample_size, replace=False)

        for idx in chosen_indices:
            recipe = bucket[idx][0]
            history.append({
                "recipe_id": recipe["id"],
                "rating": star,
                "date": "2024-01-01",  # all synthetic entries get an old date
            })

    return history


# RECENCY WEIGHTS
# Builds an array of training-sample weights, one per history entry,
# where newer entries get bigger weights. The weights are passed to
# RandomForestRegressor.fit() via the sample_weight argument — sklearn
# will then count newer samples more heavily when growing each tree.
#
# Why this matters: synthetic entries all have date "2024-01-01" so they
# end up at the bottom of the date-sorted list with weight ~1. Real
# ratings from the user have today's date and end up at the top with
# weight ~3. As the user rates more recipes, the model's predictions
# shift toward their actual taste.

def build_sample_weights(history):
    """Returns a numpy array of weights aligned with the history list."""

    n = len(history)
    if n == 0:
        return np.array([])

    # Sort the history entries by date so we can rank them. Older entries
    # come first, newer entries come last.
    sorted_history = sorted(history, key=lambda h: h["date"])

    # Build a {entry_position_in_original_list: rank} lookup.
    # rank 0 = oldest, rank n-1 = newest.
    rank_by_id = {}
    for rank, entry in enumerate(sorted_history):
        # id() gives us a unique handle to the dict object itself.
        rank_by_id[id(entry)] = rank

    # Map each rank to a weight between 1.0 (oldest) and 3.0 (newest).
    # A linear scale is simple and easy to explain in the video.
    weights = []
    for entry in history:
        rank = rank_by_id[id(entry)]
        if n == 1:
            weight = 1.0
        else:
            weight = 1.0 + 2.0 * (rank / (n - 1))
        weights.append(weight)

    return np.array(weights)


# BUILD X (features) AND y (ratings) FROM A HISTORY LIST
# Pulled out into its own helper because we need to do this in three
# places: when training the production model, when evaluating the model
# on a held-out test split, and when filtering valid entries before
# weighting them.

def build_X_y(history, all_recipes, all_ingredient_keys):
    """
    Returns (X, y, valid_history) where:
      - X is a 2D numpy array of feature vectors (one row per history entry)
      - y is a 1D numpy array of ratings
      - valid_history is the subset of history entries that successfully
        matched a recipe in the database (used so sample_weights line up).
    """
    recipe_by_id = {recipe["id"]: recipe for recipe in all_recipes}

    X_rows = []
    y_values = []
    valid_history = []

    for entry in history:
        recipe = recipe_by_id.get(entry["recipe_id"])
        if recipe is None:
            continue
        X_rows.append(build_recipe_vector(recipe, all_ingredient_keys))
        y_values.append(entry["rating"])
        valid_history.append(entry)

    X = np.array(X_rows)
    y = np.array(y_values, dtype=float)
    return X, y, valid_history


# TRAIN THE RANDOM FOREST
# Combines the synthetic 60-entry history with whatever real ratings the
# user has given, builds X (features) and y (target ratings), and fits
# the Random Forest. Returns the trained model along with the master
# ingredient list, both needed later to score new recipes.

def train_recommender(real_history, all_recipes):
    """
    Trains a Random Forest on the combined synthetic + real history.
    Returns (model, all_ingredient_keys) so the caller can score recipes.
    """

    # Build the master ingredient list once — used both for training and
    # for scoring later.
    all_ingredient_keys = collect_all_ingredient_keys(all_recipes)

    # SYNTHETIC + REAL HISTORY
    # Synthetic data gives the model a starting point so it works even
    # before the user has rated anything. Real history is appended on top
    # so the model gradually learns the user's actual taste.
    synthetic_history = generate_synthetic_history(all_recipes)

    # Only keep real history entries that actually have a rating —
    # unrated entries can't be used as training labels.
    rated_real_history = [h for h in real_history if h.get("rating")]

    combined_history = synthetic_history + rated_real_history

    # Build X and y from the combined history.
    X, y, valid_history = build_X_y(combined_history, all_recipes,
                                    all_ingredient_keys)

    # Build sample weights so newer ratings count more heavily than older
    # ones. Synthetic entries (dated 2024-01-01) are oldest, real ratings
    # are newest.
    sample_weights = build_sample_weights(valid_history)

    # CREATE AND FIT THE MODEL
    # n_estimators=100 → 100 small decision trees in the forest
    # random_state=42  → makes the results reproducible across runs
    # max_depth=10     → caps tree depth so the model doesn't just
    #                    memorise the training data ("overfit")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )
    model.fit(X, y, sample_weight=sample_weights)

    return model, all_ingredient_keys


# EVALUATE THE MODEL ON A HELD-OUT TEST SPLIT
# This is the lecture's "generalization test" (slides 13-17 and 55).
# We split the available data 80/20 with sklearn's train_test_split,
# fit a fresh Random Forest on the 80% training portion, and use the
# 20% test portion (which the model has NEVER seen) to compute two
# standard regression metrics:
#
#   MAE = Mean Absolute Error
#       Average absolute distance between predicted and actual rating.
#       Reported in stars. Easy to interpret: "the model is off by ~X
#       stars on average."
#
#   MSE = Mean Squared Error
#       Average squared distance. Reported in stars². Penalises large
#       errors much more heavily than small ones, so a model that is
#       occasionally very wrong gets a worse MSE than one that is
#       consistently a little wrong.
#
# Both metrics come from sklearn.metrics — no manual math needed.

def evaluate_recommender(real_history, all_recipes, test_size=0.2,
                         random_state=42):
    """
    Trains a fresh Random Forest on 80% of the data and reports MAE
    and MSE on the held-out 20%. Returns (mae, mse, n_test).

    n_test is also returned so the UI can mention how many entries
    were in the held-out set (e.g. "evaluated on 12 held-out recipes").
    """

    all_ingredient_keys = collect_all_ingredient_keys(all_recipes)

    # Same combined-history logic as train_recommender, so we evaluate
    # the model on data that looks like what we actually train on.
    synthetic_history = generate_synthetic_history(all_recipes)
    rated_real_history = [h for h in real_history if h.get("rating")]
    combined_history = synthetic_history + rated_real_history

    X, y, valid_history = build_X_y(combined_history, all_recipes,
                                    all_ingredient_keys)

    # If there aren't enough samples to split, return None values so the
    # UI can show a friendly "not enough data yet" message. We need at
    # least 5 samples to make an 80/20 split sensible.
    if len(y) < 5:
        return None, None, 0

    sample_weights = build_sample_weights(valid_history)

    # 80/20 split. random_state makes the split reproducible so the
    # evaluation number doesn't jitter between reruns of the same data.
    # We split the weights too so each row keeps its weight after the
    # shuffle.
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y, sample_weights,
        test_size=test_size,
        random_state=random_state,
    )

    # Fit a FRESH model on only the training portion. Important: this
    # is a separate model from the production one — we don't want to
    # contaminate the real predictions with the test data.
    eval_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=random_state,
    )
    eval_model.fit(X_train, y_train, sample_weight=w_train)

    # Predict on the held-out test set the model has never seen.
    y_pred = eval_model.predict(X_test)

    # Compute the two metrics. Both are simple averages over the
    # test set — sklearn does the math, we just call the function.
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    return float(mae), float(mse), len(y_test)


# SCORE & RANK RECIPES
# Main function called by the search page. Takes the candidate recipes
# the user filtered down to (already filtered by allergens, diet, time
# limit, difficulty, "must use at least one selected ingredient"),
# predicts a star rating for each one, and returns the top 5.

def recommend_top_recipes(candidate_recipes, real_history, all_recipes,
                          num_recommendations=5):
    """
    Returns a list of (recipe, predicted_rating) tuples, sorted from
    highest predicted rating to lowest, capped at num_recommendations.

    candidate_recipes : list of recipe dicts already filtered by the search
                        page's allergen/diet/time/difficulty filters.
    real_history      : the user's actual cooking history from db.py.
    all_recipes       : the full recipe database — needed so the master
                        ingredient list is built from ALL recipes, not
                        just the candidates.
    """

    # If there are no candidates to score, return immediately to avoid
    # building a model for nothing.
    if not candidate_recipes:
        return []

    # Train the Random Forest on synthetic + real history.
    model, all_ingredient_keys = train_recommender(real_history, all_recipes)

    # Build the feature matrix for the candidate recipes.
    X_candidates = []
    for recipe in candidate_recipes:
        X_candidates.append(build_recipe_vector(recipe, all_ingredient_keys))
    X_candidates = np.array(X_candidates)

    # Ask the model to predict a rating for every candidate recipe.
    # predict() returns a 1D array of predicted ratings, one per recipe.
    predictions = model.predict(X_candidates)

    # Pair each recipe with its predicted rating, then sort highest first.
    scored = list(zip(candidate_recipes, predictions))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    # Cap predictions to the valid 1-5 range — the trees can occasionally
    # extrapolate slightly outside this range, which would look weird in
    # the UI ("predicted: 5.3 / 5").
    capped = []
    for recipe, pred in scored[:num_recommendations]:
        clipped = max(1.0, min(5.0, float(pred)))
        capped.append((recipe, clipped))

    return capped
