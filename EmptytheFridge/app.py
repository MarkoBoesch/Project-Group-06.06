# app.py
# Main file of the app. Everything comes together here.
#
# This file is the entry point for the Streamlit app. It:
# - Sets up the page configuration
# - Loads recipes from TheMealDB API on the first run
# - Routes the user between the three main pages:
#       1. Enter Ingredients   (find + ML-ranked recipes based on what you have)
#       2. History             (list of cooked recipes, gives ratings to feed the model)
#       3. Statistics          (cost / CO2 / nutrition overview)
#
# Recommendations are now produced by a Random Forest model
# (see recommender.py). They appear directly on the Enter Ingredients
# page as the top 5 recipes ranked by predicted user rating.
#
# To start the app, type in the terminal: streamlit run app.py
# -----------------------------------------------------------------------------

import streamlit as st
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Database functions: read recipes/ingredients/history and write history/ratings.
from db import (
    load_all_recipes,
    load_recipe,
    load_all_ingredients,
    load_history,
    save_history,
    update_rating
)
# Machine-learning recommendation logic (Random Forest).
from recommender import recommend_top_recipes, evaluate_recommender
# Static data: pantry staples, diet filters, CHF prices, display name dictionary.
from constants import base_ingredients, INGREDIENT_VALUE_CHF, NON_VEGAN_INGREDIENTS, NON_VEGETARIAN_INGREDIENTS, ingredient_dictionary
# Loader that pulls all recipes from TheMealDB API into our local database.
from api_loader import load_api_recipes


# DROPDOWN-HIDDEN INGREDIENTS
# Ingredients the user should NOT see in the search-page multiselect
# because they don't really spoil and aren't things people try to "use
# up" before they go bad — water, baking staples, oils, vinegar, salt,
# sugar, plus shelf-stable condiments like mayo, hot sauce and
# Worcestershire. These ingredients still exist everywhere else (the
# recommender can still use them as features, the recipe details still
# show them, the cost calculator still treats them sensibly), they're
# just hidden from this specific UI element.
#
# Note: many of these (oil, olive_oil, salt, sugar, flour, baking_powder,
# vinegar, water) are already in `base_ingredients` from constants.py,
# which means the cost calculator and ingredient-overlap matcher already
# treat them as pantry staples. The only behaviour change here is the
# multiselect dropdown.

HIDDEN_FROM_DROPDOWN = {
    "water",
    "baking_powder",
    "oil",
    "olive_oil",
    "salt",
    "sugar",
    "vinegar",
    "flour",
    "bbq_sauce",
    "dijon_mustard",
    "hot_sauce",
    "mayonnaise",
    "worcestershire",
}


# PAGE SETTINGS
# Browser tab title, icon and full-width ("wide") layout.

st.set_page_config(
    page_title="EmptyTheFridge",
    page_icon="👨‍🍳",
    layout="wide"
)

# LOAD API RECIPES ON START
# Streamlit reruns the script on every interaction, so we use session_state
# as a one-time guard to make sure the (slow) API import only runs once.

if "api_loaded" not in st.session_state:
    with st.spinner("Loading recipes from TheMealDB... (first start only)"):
        load_api_recipes()
    st.session_state.api_loaded = True

# CALCULATE COSTS
# Helper used on the Statistics page to estimate how many CHF worth of
# ingredients were "saved" by cooking a recipe instead of letting them spoil.

def calculate_costs(recipe, used_ingredients=None):
    """
    Estimates the CHF value of the ingredients the user was actually trying
    to use up, meaning only the ingredients they selected on the search page.

    Only the fresh items the user had in their fridge, which might otherwise 
    have spoiled, count as real savings.For this reason, staples and items 
    such as spices are not included in the cost calculations.

    used_ingredients: comma-separated string of ingredient keys stored in
    the history table (e.g. "chicken_breast,carrot,spinach"). When None or
    empty (e.g. for old history entries or recommendation cooks), falls back
    to pricing ALL non-base ingredients in the recipe.

    Pricing is proportional by weight/quantity using the amounts field:
      banana at CHF 2.40/kg × 0.250 kg = CHF 0.60
    """
    import re

    # Determine which ingredient keys to price.
    if used_ingredients:
        keys_to_price = set(k.strip() for k in used_ingredients.split(",") if k.strip())
    else:
        # Fallback for history entries without saved keys (e.g. old data,
        # or recipes cooked from the Recommendations page where no
        # ingredient selection was made).
        all_keys = [k.strip() for k in recipe["ingredients"].split(",")]
        keys_to_price = set(k for k in all_keys if k and k not in base_ingredients)

    # Build amounts dict from "key:amount,key:amount,..." string
    amounts_dict = {}
    if recipe.get("amounts"):
        for entry in recipe["amounts"].split(","):
            if ":" in entry:
                parts = entry.split(":", 1)
                amounts_dict[parts[0].strip()] = parts[1].strip()

    # Piece-sold items: price per unit rather than per kg
    UNIT_PRICED = {
        "egg", "lemon", "lime", "avocado",
        "butter", "cream", "heavy_cream", "yogurt", "cream_cheese",
        "mozzarella", "parmesan", "feta", "ricotta", "sour_cream", "cheese",
        "milk",
    }
    LIQUID_DENSITY = {
        "olive_oil": 0.92, "oil": 0.92, "milk": 1.03,
        "cream": 1.01, "heavy_cream": 1.00, "soy_sauce": 1.06,
        "vegetable_broth": 1.00, "coconut_milk": 1.00,
        "worcestershire": 1.09, "hot_sauce": 1.00, "bbq_sauce": 1.05,
        "vinegar": 1.01, "honey": 1.40,
    }
    DEFAULT_PRICE_PER_KG = 3.00
    DEFAULT_PORTION_KG   = 0.150

    def parse_amount(key, raw):
        price = INGREDIENT_VALUE_CHF.get(key, DEFAULT_PRICE_PER_KG)
        raw = raw.strip().lower()

        m = re.match(r"^([\d.]+)\s*g$", raw)
        if m:
            if key in UNIT_PRICED:
                std_g = {"yogurt": 500, "butter": 250, "cream": 200,
                         "heavy_cream": 500, "mozzarella": 150,
                         "cream_cheese": 200, "feta": 200,
                         "ricotta": 250, "sour_cream": 200,
                         "cheese": 250, "parmesan": 100}.get(key, 250)
                return price * float(m.group(1)) / std_g
            return price * float(m.group(1)) / 1000.0

        m = re.match(r"^([\d.]+)\s*kg$", raw)
        if m:
            return price * float(m.group(1))

        m = re.match(r"^([\d.]+)\s*ml$", raw)
        if m:
            density = LIQUID_DENSITY.get(key, 1.00)
            return price * float(m.group(1)) / 1000.0 * density

        m = re.match(r"^([\d.]+)\s*l$", raw)
        if m:
            density = LIQUID_DENSITY.get(key, 1.00)
            return price * float(m.group(1)) * density

        m = re.match(r"^([\d.]+)\s*(tbsp|tsp)$", raw)
        if m:
            vol_ml = float(m.group(1)) * (15 if m.group(2) == "tbsp" else 5)
            return price * (vol_ml / 1000.0) * LIQUID_DENSITY.get(key, 0.90)

        m = re.match(r"^([\d.]+)$", raw)
        if m:
            count = float(m.group(1))
            if key in UNIT_PRICED:
                return price * count
            return price * count * DEFAULT_PORTION_KG

        return price * DEFAULT_PORTION_KG

    total = 0.0
    for key in keys_to_price:
        raw_amount = amounts_dict.get(key, "")
        if raw_amount:
            total += parse_amount(key, raw_amount)
        else:
            price = INGREDIENT_VALUE_CHF.get(key, DEFAULT_PRICE_PER_KG)
            total += price if key in UNIT_PRICED else price * DEFAULT_PORTION_KG

    return round(total, 2)


# RENDER RECIPE INGREDIENTS
# Used three times in the app (on the search page and twice on the History
# page) to display a recipe's ingredient list grouped and colour-coded.
# Pulled out into a helper to avoid copy-pasting the same ~25 lines in
# three places.
#
# Two display modes:
#   - selected_keys = None  (History page)
#       Two groups: pantry staples (grey) and everything else (orange).
#       The user did not enter any ingredients on this page, so we cannot
#       say which ones they already have.
#   - selected_keys = [list of keys]  (Search page)
#       Three groups: ingredients the user said they have (green), pantry
#       staples (grey), still missing (orange). Also shows a success
#       message if all ingredients are covered.

def render_recipe_ingredients(recipe, selected_keys=None):
    """Renders a recipe's ingredients as colour-coded groups."""

    # Build a {key: amount} dictionary from the "amounts" string, which is
    # stored as "key:amount,key:amount,...". Used to display "potato — 200g"
    # instead of just "potato".
    amounts_dict = {}
    if recipe.get("amounts"):
        for entry_amt in recipe["amounts"].split(","):
            if ":" in entry_amt:
                parts = entry_amt.split(":", 1)
                amounts_dict[parts[0].strip()] = parts[1].strip()

    # Split the ingredients string back into a clean list of keys.
    ingredient_keys = [piece.strip() for piece in recipe["ingredients"].split(",")]

    # Sort each ingredient into one of two or three groups depending on
    # whether the caller passed selected_keys (search page) or not (history).
    group_have = []      # only used when selected_keys is provided
    group_pantry = []
    group_missing = []

    for key in ingredient_keys:
        if selected_keys is not None and key in selected_keys:
            group_have.append(key)
        elif key in base_ingredients:
            group_pantry.append(key)
        else:
            group_missing.append(key)

    # Small inner helper to render one coloured group at a time. Keeps the
    # three (or two) display blocks below short and identical-looking.
    def render_group(keys, header, colour):
        if not keys:
            return
        st.markdown(header)
        for key in keys:
            display = ingredient_dictionary.get(key, key)
            amount = amounts_dict.get(key, "as needed")
            st.markdown(
                f"<span style='color:{colour}'>• **{display}** — {amount}</span>",
                unsafe_allow_html=True,
            )

    st.subheader("🛒 Ingredients for 2 portions")

    # The "have" group only exists in search-page mode (selected_keys given).
    if selected_keys is not None:
        render_group(group_have,    "✅ **You have these ingredients:**",            "#00cc00")
        render_group(group_pantry,  "🏠 **Basic pantry items (assumed at home):**", "#888888")
        render_group(group_missing, "🛒 **These ingredients are still missing:**",  "#ff8800")
        # Encouraging success message — only meaningful on the search page,
        # where "missing" actually reflects what the user has at home.
        if not group_missing:
            st.success("You have all the ingredients at home!")
    else:
        render_group(group_pantry,  "🏠 **Basic pantry items (assumed at home):**", "#888888")
        render_group(group_missing, "🛒 **Ingredients you will need:**",            "#ff8800")


# NAVIGATION
# Top header plus a sidebar radio menu. The chosen `page` value drives the
# if/elif blocks below to decide which page to render.

col_left, col_right = st.columns([4, 1])

with col_left:
    st.title("👨‍🍳 EmptyTheFridge")

st.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🥕 Enter Ingredients",
        "📖 History and Recommendations",
        "📊 Statistics",
    ]
)

# -----------------------------------------------------------------------------
# PAGE 1: ENTER INGREDIENTS
# Main "search" page. Users select what they have at home, optionally apply
# diet/time/difficulty/allergen filters, and get the top 5 recipes back as
# ranked by the Random Forest model. Each card shows the predicted user
# rating so the user can see WHY a recipe ranked where it did.
# -----------------------------------------------------------------------------

# Only when the user has selected "🥕 Enter Ingredients" in the navigation bar 
# does this whole block execute.
if page == "🥕 Enter Ingredients":

    st.header("What do you have at home?")
    st.write("Select the ingredients you want to use up.")

    # Load all known ingredients. Each entry has both an internal key
    # (e.g. "bell_pepper") and a human-readable display name (e.g. "Bell Pepper").
    # Display names are shown to the user, but matching is done with keys.
    all_ingredients = load_all_ingredients()

    # Filter out ingredients that don't really spoil (water, salt, sugar,
    # oil, flour, shelf-stable condiments etc.) so the user only sees
    # things they might actually want to "use up". The hidden items are
    # still available everywhere else in the app — the cost calculator,
    # the ingredient-display helper, and the recommender all still see
    # them as normal ingredients.
    visible_ingredients = [
        i for i in all_ingredients
        if i["key"] not in HIDDEN_FROM_DROPDOWN
    ]
    ingredient_display_names = [i["name"] for i in visible_ingredients]

    st.subheader("Select Ingredients")

    selected_display_names = st.multiselect(
        "Type to search and select your ingredients:",
        options=ingredient_display_names,
        placeholder="e.g. Potato, Egg, Tomatoes..."
    )

    # Convert display names back into internal keys for matching.
    # We look up against the full list (not visible_ingredients) so that
    # any old session_state leftover with a hidden ingredient still
    # resolves correctly.
    selected_keys = []
    for display_name in selected_display_names:
        for ingredient in all_ingredients:
            if ingredient["name"] == display_name:
                selected_keys.append(ingredient["key"])

    # FILTERS
    # Diet, cooking time, difficulty and allergen filters. Diet uses
    # buttons (instead of a dropdown) so the active option is highlighted.
    
    st.subheader("Filters")

    # Diet filter (button-based)
    # The chosen diet is persisted in session_state so it survives reruns.
    if "diet_filter" not in st.session_state:
        st.session_state.diet_filter = "All"

    st.write("**Diet**")
    diet_col1, diet_col2, diet_col3, diet_col4 = st.columns(4)


    # When a button is clicked, it saves its value into session_state.diet_filter
    # and then forces the page to rerun. On that rerun, the just-clicked button
    # notices it is now the "active" one and re-renders itself in the highlighted
    # primary style with a checkmark in front, while the other three buttons
    # fall back to the plain secondary style with their food emoji.
    with diet_col1:
        if st.button(
            "✅ All" if st.session_state.diet_filter == "All" else "🍽️ All",
            use_container_width=True,
            type="primary" if st.session_state.diet_filter == "All" else "secondary"
        ):
            st.session_state.diet_filter = "All"
            st.rerun()

    with diet_col2:
        if st.button(
            "✅ With Meat" if st.session_state.diet_filter == "meat" else "🥩 With Meat",
            use_container_width=True,
            type="primary" if st.session_state.diet_filter == "meat" else "secondary"
        ):
            st.session_state.diet_filter = "meat"
            st.rerun()

    with diet_col3:
        if st.button(
            "✅ Vegetarian" if st.session_state.diet_filter == "vegetarian" else "🥗 Vegetarian",
            use_container_width=True,
            type="primary" if st.session_state.diet_filter == "vegetarian" else "secondary"
        ):
            st.session_state.diet_filter = "vegetarian"
            st.rerun()

    with diet_col4:
        if st.button(
            "✅ Vegan" if st.session_state.diet_filter == "vegan" else "🌱 Vegan",
            use_container_width=True,
            type="primary" if st.session_state.diet_filter == "vegan" else "secondary"
        ):
            st.session_state.diet_filter = "vegan"
            st.rerun()

    st.write("")  # spacing

    # Other filters (time, difficulty, allergens).
    col1, col2, col3 = st.columns(3)

    with col1:
        max_time = st.slider(
            "Maximum cooking time (minutes)",
            min_value=10, max_value=120, value=60, step=5
        )
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            options=["All", "easy", "medium", "hard"]
        )
    with col3:
        # Any recipe containing one of the chosen allergens is filtered out below.
        allergen_options = ["gluten", "dairy", "egg", "fish", "soy", "nuts"]
        allergies = st.multiselect("Allergies / Intolerances", options=allergen_options)

    # SEARCH RECIPES
    # When "Find Recipes" is clicked, every recipe is checked against all
    # filters. Recipes that pass the filters become the "candidate" set,
    # which is then handed to the Random Forest model. The model predicts
    # a star rating for every candidate, and we keep the top 5.

    if st.button("🔍 Find Recipes", type="primary"):

        # If no ingredient is selected, warn the user and stop. Otherwise, load
        # all recipes and start with an empty list to collect the matches.
        if len(selected_keys) == 0:
            st.warning("Please select at least one ingredient.")
        else:
            all_recipes = load_all_recipes()
            matching_recipes = []

            # Walk through every recipe and apply each filter in turn.
            # `continue` is used to skip recipes that fail a filter.
            for recipe in all_recipes:

                # Allergen filter: skip if recipe contains any chosen allergen.
                recipe_allergens = recipe["allergens"].split(",") if recipe["allergens"] else []
                allergen_found = any(allergy in recipe_allergens for allergy in allergies)
                if allergen_found:
                    continue

                # Time and difficulty filters.
                if recipe["time_minutes"] > max_time:
                    continue
                if difficulty != "All" and recipe["difficulty"] != difficulty:
                    continue

                # Diet filter:
                # - vegan       = no animal products at all
                # - vegetarian  = dairy/eggs ok, no meat/fish
                # - meat        = at least one meat/fish ingredient required
                
                # .strip() is used so that API recipe ingredients with
                # accidental whitespace around the key still match correctly.
                recipe_ingredients = [i.strip() for i in recipe["ingredients"].split(",")]
                diet = st.session_state.diet_filter

                if diet == "vegan":
                    if any(i in NON_VEGAN_INGREDIENTS for i in recipe_ingredients):
                        continue
                elif diet == "vegetarian":
                    if any(i in NON_VEGETARIAN_INGREDIENTS for i in recipe_ingredients):
                        continue
                elif diet == "meat":
                    if not any(i in NON_VEGETARIAN_INGREDIENTS for i in recipe_ingredients):
                        continue

                # INGREDIENT MATCH SCORING (legacy logic)
                # Count how many of the recipe's ingredients the user has
                # selected, and how many are still missing (pantry staples
                # like salt/oil are assumed to be at home and are excluded
                # from the missing count). The two counts are then used to
                # sort recipes: most matching ingredients first, fewest
                # missing as a tiebreaker.

                # Count how many of the user's selected ingredients appear in this recipe.
                present_ingredients = 0
                for key in selected_keys:
                    if key in recipe_ingredients:
                        present_ingredients += 1

                # Count how many recipe ingredients the user is still missing,
                # ignoring pantry staples.
                missing_ingredients = 0
                for ingredient in recipe_ingredients:
                    if ingredient not in selected_keys and ingredient not in base_ingredients:
                        missing_ingredients += 1

                # Only keep recipes that use at least one of the user's
                # ingredients — otherwise the result feels disconnected
                # from "what's in my fridge".
                if present_ingredients > 0:
                    matching_recipes.append({
                        "recipe": recipe,
                        "present": present_ingredients,
                        "missing": missing_ingredients
                    })

            # Sort by best ingredient match.
            # Primary: most matching ingredients (more = better, hence -present).
            # Tiebreaker: fewest missing ingredients (smaller = better).
            def by_best_match(entry):
                return (-entry["present"], entry["missing"])

            matching_recipes.sort(key=by_best_match)

            # Persist results in session_state so they survive reruns
            # triggered by other widgets (e.g. "Mark as Cooked").
            st.session_state.search_results = matching_recipes
            st.session_state.search_selected_keys = list(selected_keys)
            st.session_state.show_results = True

    # SHOW RESULTS
    # Renders each matching recipe as a collapsible expander containing
    # quick stats, a colour-coded ingredient list, instructions, and a
    # "Mark as Cooked" button. No ML / predicted ratings on this page —
    # the search page is purely about finding what to cook with what's
    # in the fridge. Personalised recommendations live on the History
    # and Recommendations page.

    if "show_results" in st.session_state and st.session_state.show_results:

        results = st.session_state.search_results
        # Pull the selected_keys captured at search time so the rendered
        # ingredient groups still work even if the user later un-ticks
        # something in the multiselect.
        result_selected_keys = st.session_state.get("search_selected_keys", [])

        # Show a hint if there are no matches, otherwise display the result count.
        if len(results) == 0:
            st.info("No matching recipes found. Try different ingredients or filters.")
        else:
            count = len(results)
            st.subheader(f"{count} recipes found")

            # Walk through every matching recipe and pull out its data for display.
            for entry in results:
                recipe = entry["recipe"]
                name = recipe["name"]

                with st.expander(f"🍽️ {name} — missing: {entry['missing']} ingredients"):

                    # Quick stats row: time / difficulty / calories.
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Cooking time", f"{recipe['time_minutes']} min")
                    with col_b:
                        st.metric("Difficulty", recipe["difficulty"])
                    with col_c:
                        st.metric("Calories", f"{recipe['calories']} kcal")

                    # INGREDIENTS: Static display for 2 portions.
                    # Amounts come straight from TheMealDB.
                    # Each ingredient is sorted into one of three groups
                    # (have / pantry / missing) for colour-coded display.
                    render_recipe_ingredients(recipe, selected_keys=result_selected_keys)

                    st.divider()

                    # Cooking instructions pulled from TheMealDB (loaded via api_loader.py).
                    st.subheader("👨‍🍳 Instructions")
                    st.write(recipe["instructions"])

                    # "Mark as Cooked" writes today's date and the recipe ID
                    # into the history table, which feeds the Random Forest
                    # model on the History and Recommendations page. The
                    # unique key prevents Streamlit from confusing buttons
                    # across multiple expanders.
                    if st.button("✅ Mark as Cooked", key=f"cook_{recipe['id']}"):
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        used = ",".join(result_selected_keys) if result_selected_keys else ""
                        try:
                            save_history(recipe["id"], today, None, used)
                        except TypeError:
                            # Fallback for older db.py without used_ingredients
                            save_history(recipe["id"], today)
                        st.success(f"'{name}' added to your cooking history!")
                        st.rerun()


# -----------------------------------------------------------------------------
# PAGE 2: HISTORY AND RECOMMENDATIONS
# Three sections:
#   1. Cooking History — every cooked recipe + a 5-star rating widget.
#      Ratings here feed the Random Forest model.
#   2. Top recommendations — 5 recipes the model thinks the user will
#      love most, drawn from the ENTIRE recipe DB (not just fridge
#      matches). Recipes already cooked 4+ times are excluded so the
#      suggestions stay fresh.
#   3. Model evaluation — MAE / MSE on a held-out 20% test split, the
#      lecture's slide-55 generalization test.
# -----------------------------------------------------------------------------

# Only when the user has selected "📖 History and Recommendations" in the
# navigation bar does this whole block execute.
elif page == "📖 History and Recommendations":

    st.header("📖 History and Recommendations")

    history = load_history()

    # SECTION 1: COOKING HISTORY
    # Each cooked recipe gets its own expander showing date, calories
    # and a 5-star rating widget. Once a rating has been saved, the
    # slider is replaced by the rating itself. Ratings feed the Random
    # Forest model in the recommendations section below.

    st.subheader("Your Cooking History")
    st.caption(
        "Rate the recipes you cooked so the recommendation model learns "
        "your taste. Newer ratings count more strongly than older ones."
    )

    if len(history) == 0:
        st.info("You haven't cooked any recipes yet. Go to the Enter Ingredients page and find your first recipe!")
    else:
        st.write(f"You have cooked {len(history)} recipes so far.")

        for entry in history:
            name = entry["name"]

            with st.expander(f"📅 {entry['date']} — {name}"):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.write("Calories:", entry["calories"], "kcal")

                with col_b:
                    # If a rating exists, show stars. Otherwise, show
                    # a slider + save button.
                    if entry["rating"]:
                        st.write("Your rating:", "⭐" * entry["rating"])
                    else:
                        rating = st.slider(
                            "Rate this recipe:",
                            min_value=1, max_value=5, value=3,
                            key=f"rating_{entry['id']}"
                        )
                        if st.button("Save rating", key=f"save_{entry['id']}"):
                            update_rating(entry["id"], rating)
                            st.rerun()

    # SECTION 2: TOP 5 RECOMMENDATIONS (Random Forest)
    # The model is trained on synthetic + real history every time this
    # page loads. We score the ENTIRE recipe DB, exclude recipes the
    # user has already cooked 4+ times, and show the top 5 by predicted
    # rating. Each card displays the predicted rating so the ML output
    # is visible to the user.

    st.divider()
    st.subheader("⭐ Top 5 Recommendations for You")
    st.caption(
        "Recipes ranked by predicted user rating using a Random Forest "
        "machine-learning model trained on your taste profile. Recipes "
        "you have cooked 4 or more times are excluded so suggestions "
        "stay fresh."
    )

    all_recipes_for_recs = load_all_recipes()

    # Filter out recipes the user has already cooked 4+ times so the
    # suggestions stay fresh. We do this filter HERE (rather than passing
    # a keyword argument into recommend_top_recipes) so the call works
    # regardless of which version of recommender.py is deployed.
    cook_counts = {}
    for h_entry in history:
        rid = h_entry.get("recipe_id")
        if rid is not None:
            cook_counts[rid] = cook_counts.get(rid, 0) + 1

    fresh_recipes = [
        recipe for recipe in all_recipes_for_recs
        if cook_counts.get(recipe["id"], 0) < 4
    ]

    # Edge case: if the user has cooked everything ≥4 times, fall back
    # to the full DB so the recommendations panel never shows blank.
    if not fresh_recipes:
        fresh_recipes = all_recipes_for_recs

    recommendations = recommend_top_recipes(
        fresh_recipes,
        history,
        all_recipes_for_recs,
        num_recommendations=5,
    )

    if not recommendations:
        st.info("No recommendations available — the recipe database appears to be empty.")
    else:
        # Render each recommendation as a collapsible expander, similar
        # to the search results page but with the predicted rating shown.
        for rec, predicted_rating in recommendations:
            rec_name = rec["name"]

            expander_label = (
                f"🍽️ {rec_name} — ⭐ predicted: {predicted_rating:.1f} / 5"
            )

            with st.expander(expander_label):

                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Predicted rating",
                              f"⭐ {predicted_rating:.1f} / 5")
                with col_b:
                    st.metric("Cooking time", f"{rec['time_minutes']} min")
                with col_c:
                    st.metric("Difficulty", rec["difficulty"])
                with col_d:
                    st.metric("Calories", f"{rec['calories']} kcal")

                # Render ingredients via the shared helper. No
                # selected_keys here, because the History page is in
                # discovery mode rather than fridge-search mode — the
                # user did not enter what they currently have at home.
                render_recipe_ingredients(rec)

                st.divider()
                st.subheader("👨‍🍳 Instructions")
                st.write(rec["instructions"])

                # "Mark as Cooked" writes a history entry. Different key
                # prefix from the search page ("rec_cook_") so Streamlit
                # doesn't confuse the buttons across pages.
                if st.button("✅ Mark as Cooked", key=f"rec_cook_{rec['id']}"):
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    save_history(rec["id"], today)
                    st.success(f"'{rec_name}' added to your cooking history!")
                    st.rerun()

    # SECTION 3: MODEL EVALUATION (held-out test split)
    # Slide 55 of the lecture: "we need a second data set to test the
    # generalization. If and only if the error is acceptable on this
    # second data set, we can report success." We split the training
    # data 80/20, fit on the 80%, and report the prediction error on
    # the 20% the model never saw. MAE = how far off in stars on
    # average; MSE = same idea but squared (penalises big misses).

    st.divider()
    st.subheader("📊 Model Accuracy")

    mae, mse, n_test = evaluate_recommender(history, all_recipes_for_recs)

    if mae is None:
        st.info("Not enough rating data to evaluate the model yet.")
    else:
        eval_col1, eval_col2 = st.columns(2)
        with eval_col1:
            st.metric(
                "🎯 Model Accuracy (MAE)",
                f"± {mae:.2f} stars",
                help=(
                    "Mean Absolute Error. Average distance between the "
                    "model's predicted rating and the actual rating, "
                    f"measured on a held-out 20% test split ({n_test} "
                    "recipes the model never saw during training). "
                    "Lower is better — closer to 0 means more accurate."
                ),
            )
        with eval_col2:
            st.metric(
                "📐 Model Accuracy (MSE)",
                f"{mse:.2f} stars²",
                help=(
                    "Mean Squared Error. Like MAE, but squares each "
                    "prediction error so big misses are penalised "
                    "more heavily than small ones. Reported in stars². "
                    "Lower is better."
                ),
            )
        st.caption(
            "Evaluation: the model was trained on 80% of the synthetic "
            "and real ratings and tested on the remaining 20% it had "
            "never seen. These numbers describe the model's "
            "generalization, not the predictions shown above."
        )


# -----------------------------------------------------------------------------
# PAGE 3: STATISTICS
# Aggregates data from the cooking history into visual statistics:
#   - Top KPI row: number of recipes, saved CHF, saved ingredients
#   - Bar+line chart: CO2 saved per session and cumulatively (matplotlib)
#   - Radar chart: nutritional values for everything cooked TODAY (matplotlib)
# -----------------------------------------------------------------------------

# Only when the user has selected "📊 Statistics" in the navigation bar does 
# this whole block execute.
elif page == "📊 Statistics":

    st.header("Your Statistics")

    history = load_history()

    # If there is no history yet, all charts and metrics would be empty,
    # so we show a warning instead.
    if len(history) == 0:
        st.info("No statistics available yet. Cook some recipes first!")
    else:

        st.subheader("Overview")

        # Aggregate over the whole history: total cost, plus the set of
        # unique non-pantry ingredients used (= ingredients "saved").
        num_recipes = len(history)
        total_costs = 0
        saved_ingredients_set = set()

        for entry in history:
            recipe = load_recipe(entry["recipe_id"])
            if recipe:
                total_costs += calculate_costs(recipe, entry.get("used_ingredients"))
                # Only count the ingredients the user selected as "saved",
                # excluding staples — same logic as the cost calculation.
                used = entry.get("used_ingredients")
                if used:
                    saved_keys = [k.strip() for k in used.split(",") if k.strip()]
                else:
                    saved_keys = [k.strip() for k in recipe["ingredients"].split(",")
                                  if k.strip() and k.strip() not in base_ingredients]
                recipe_ingredients = saved_keys

                for ingredient in recipe_ingredients:
                    if ingredient and ingredient not in base_ingredients:
                        saved_ingredients_set.add(ingredient)

        total_costs = round(total_costs, 2)
        num_saved_ingredients = len(saved_ingredients_set)

        # Three-column KPI row at the top of the page:
        # Number of recipes, saved CHF, saved ingredients.
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Cooked Recipes", num_recipes)
        with col2:
            st.metric(
                "💰 Saved Costs",
                f"CHF {total_costs:.2f}",
                help="Based on the estimated value of the selected ingredients used."
                )          
        with col3:
            st.metric(
                "🧺 Saved Ingredients",
                num_saved_ingredients,
                help="Unique non-basic ingredients used across all cooked recipes."
            )

        # CUMULATIVE CO2 SAVED BAR CHART (matplotlib)
        # Combined chart with two layers:
        #   - Bars: how much CO2 was saved on each individual cooking day
        #   - Line: running total ("how much have I saved so far")
        # Both are plotted on the same axis using matplotlib.

        st.divider()
        st.subheader("🌱 CO2 Savings Over Time")
        st.caption("CO2 saved per cooking session (bars) and cumulative total (line).")

        # AGGREGATE BY DATE
        # Multiple cooking sessions on the same day get summed into a single
        # bar so we don't end up with overlapping bars at the same x-position.
        # We use a {date_object: total_co2} dict for easy summing.
        co2_by_date = {}
        for entry in history:
            recipe = load_recipe(entry["recipe_id"])
            if recipe:
                cost = calculate_costs(recipe, entry.get("used_ingredients"))
                session_co2 = round(cost * 0.8, 2)
                # Convert "YYYY-MM-DD" strings into real date objects so the
                # x-axis can treat them as a continuous time scale.
                date_obj = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
                co2_by_date[date_obj] = co2_by_date.get(date_obj, 0) + session_co2

        # BUILD THE TIME WINDOW
        # First cook = anchor on the left side. From there we always show
        # at least 7 days into the future, but if the user has cooked
        # something further out than that, we extend the window so the
        # latest entry is visible on the chart.
        sorted_dates = sorted(co2_by_date.keys())
        first_date = sorted_dates[0]
        last_date  = sorted_dates[-1]
        window_end = max(
            first_date + datetime.timedelta(days=7),
            last_date  + datetime.timedelta(days=1),
        )

        # Build the full continuous list of dates from anchor to window end.
        # Days without any cooking are still on the x-axis (with bar height 0).
        all_dates = []
        d = first_date
        while d <= window_end:
            all_dates.append(d)
            d += datetime.timedelta(days=1)

        # PER-DAY VALUES (for the bars)
        # Bars are plotted across the full window. Days without any
        # cooking simply get a height of 0 and don't show up visually,
        # but they keep the x-axis spread out evenly.
        co2_per_day = [co2_by_date.get(d, 0) for d in all_dates]

        # CUMULATIVE LINE (for the line plot)
        # Only includes days where the user actually cooked, so the line
        # connects bar to bar.
        cook_dates = sorted(co2_by_date.keys())
        cook_cumulative = []
        running_co2 = 0
        for d in cook_dates:
            running_co2 = round(running_co2 + co2_by_date[d], 2)
            cook_cumulative.append(running_co2)

        # Build the figure: bars first, line on top so it draws over them.
        fig_co2, ax_co2 = plt.subplots(figsize=(9, 3.5))

        ax_co2.bar(
            all_dates,
            co2_per_day,
            color="#3d9a6e",
            alpha=0.7,
            width=0.8,  # narrower bars so single entries don't span the chart
            label="CO2 per session"
        )
        ax_co2.plot(
            cook_dates,
            cook_cumulative,
            color="#1d6e45",
            linewidth=2,
            marker="o",
            markersize=5,
            label="Cumulative CO2"
        )

        ax_co2.set_ylabel("kg CO2")
        ax_co2.legend(loc="upper left")

        # Y-AXIS RANGE
        # Use a minimum ceiling of 25 kg, with ~30% headroom above the
        # current cumulative total for visual appeal.
        current_max = max(cook_cumulative) if cook_cumulative else 0
        y_max = max(25, current_max * 1.3)
        ax_co2.set_ylim(0, y_max)

        # Format the x-axis as proper dates. The locator picks roughly 8
        # tick labels regardless of how wide the window grows, so a 7-day
        # chart shows every day while a 60-day chart shows every ~week.
        ax_co2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        tick_step = max(1, len(all_dates) // 8)
        ax_co2.xaxis.set_major_locator(mdates.DayLocator(interval=tick_step))
        plt.setp(ax_co2.get_xticklabels(), rotation=30, ha="right")

        fig_co2.tight_layout()

        st.pyplot(fig_co2)

        # DAILY NUTRITION RADAR CHART (matplotlib)
        # Sums up the nutritional values of all recipes cooked TODAY and
        # plots them as percentages of the standard daily intake.
        # The outer edge of the radar = 100% of the daily intake.

        st.divider()
        st.subheader("🕸️ Today's Nutritional Values")
        st.caption("Combined nutritional values of all recipes cooked today. Outer edge = 100% daily intake.")

        # Filter the history down to entries with today's date.
        today = datetime.date.today().strftime("%Y-%m-%d")
        today_entries = [entry for entry in history if entry["date"] == today]

        if len(today_entries) == 0:
            st.info("No recipes cooked today yet. Cook something and come back!")
        else:
            # Sum each nutrient across every recipe cooked today, treating None as 0.
            calories_today = 0
            protein_today = 0
            carbs_today = 0
            fat_today = 0
            fiber_today = 0
            vitamins_today = 0
            minerals_today = 0

            today_names = []

            for entry in today_entries:
                recipe = load_recipe(entry["recipe_id"])
                if recipe:
                    calories_today += (recipe["calories"] or 0)
                    protein_today += (recipe["protein"] or 0)
                    carbs_today += (recipe["carbohydrates"] or 0)
                    fat_today += (recipe["fat"] or 0)
                    fiber_today += (recipe["fiber"] or 0)
                    vitamins_today += (recipe["vitamins"] or 0)
                    minerals_today += (recipe["minerals"] or 0)
                    today_names.append(recipe["name"])

            st.write("Cooked today:", ", ".join(today_names))

            # ── DAILY REFERENCE VALUES ────────────────────────────────────
            # Source: Swiss Federal Food Safety and Veterinary Office (BLV)
            #   "Schweizer Referenzwerte für die Nährstoffzufuhr" (2022)
            #   blv.admin.ch — Hauptnährstoffe (Protein, Kohlenhydrate, Fett)
            #   Confirmed against WHO Healthy Diet fact-sheet (Jan 2026)
            #   who.int/news-room/fact-sheets/detail/healthy-diet
            #
            # We use the midpoint between the BLV sedentary-adult targets
            # for men (2 200 kcal, 70 kg reference) and women (1 800 kcal,
            # 57 kg reference) to get a gender-neutral reference person.
            #
            #   Nutrient   Man    Woman   Average used here
            #   ─────────────────────────────────────────────
            #   Calories   2200   1800    2000 kcal
            #   Protein      58     47      52 g  (0.83 g/kg BW/day)
            #   Carbs       275    225     250 g  (45-60% of energy, BLV)
            #   Fat          69     57      63 g  (20-35% of energy, BLV)
            #   Fiber        30     25      30 g  (BLV/SGE adult target)
            #
            # Vitamins and Minerals are stored on a 0–100 scale by the
            # recipe data (TheMealDB estimate), so 100 = full daily cover.

            DAILY_CALORIES = 2000   # kcal
            DAILY_PROTEIN  =   52   # g
            DAILY_CARBS    =  250   # g
            DAILY_FAT      =   63   # g
            DAILY_FIBER    =   30   # g

            # Convert absolute totals into % of daily reference.
            # Capped at 100 so the spider chart never draws outside its circle.
            calories_pct = min(100, round(calories_today / DAILY_CALORIES * 100))
            protein_pct  = min(100, round(protein_today  / DAILY_PROTEIN  * 100))
            carbs_pct    = min(100, round(carbs_today    / DAILY_CARBS    * 100))
            fat_pct      = min(100, round(fat_today      / DAILY_FAT      * 100))
            fiber_pct    = min(100, round(fiber_today    / DAILY_FIBER    * 100))
            vitamins_pct = min(100, vitamins_today)
            minerals_pct = min(100, minerals_today)

            categories = ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Vitamins", "Minerals"]
            values = [
                calories_pct, protein_pct, carbs_pct, fat_pct,
                fiber_pct, vitamins_pct, minerals_pct
            ]

            # Build the radar chart manually with matplotlib's polar projection.
            # Each category occupies one slice of the circle. We compute the
            # angle for every category and repeat the first value at the end
            # so the polygon closes cleanly.
            import math

            num_vars = len(categories)
            angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
            angles_closed = angles + [angles[0]]
            values_closed = values + [values[0]]

            fig_radar, ax_radar = plt.subplots(
                figsize=(4, 4),
                subplot_kw=dict(polar=True)
            )

            # Draw the green-filled polygon plus its outline.
            ax_radar.plot(angles_closed, values_closed, color="green", linewidth=2)
            ax_radar.fill(angles_closed, values_closed, color="green", alpha=0.2)

            # Place category labels around the circle and fix the radial
            # axis at 0-100% so different days are visually comparable.
            ax_radar.set_xticks(angles)
            ax_radar.set_xticklabels(categories, fontsize=9)
            ax_radar.set_ylim(0, 100)
            ax_radar.set_yticks([20, 40, 60, 80, 100])
            ax_radar.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=8)

            fig_radar.tight_layout()

            # Render the radar chart in the middle of three columns so it
            # only takes up ~1/3 of the page width instead of expanding
            # to the full width of the main container.
            radar_left, radar_center, radar_right = st.columns([1, 2, 1])
            with radar_center:
                st.pyplot(fig_radar)

            # Detail breakdown below the chart.
            st.write("Detail view (% of daily reference — BLV/WHO avg adult):")
            st.caption(
                "Daily targets: 2 000 kcal · 52 g protein · 250 g carbs · "
                "63 g fat · 30 g fiber  "
                "_(Source: BLV Schweizer Referenzwerte 2022, avg. man/woman)_"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"🔥 Calories: {calories_pct}% ({calories_today} kcal)")
                st.write(f"💪 Protein: {protein_pct}% ({protein_today}g)")
                st.write(f"🍞 Carbs: {carbs_pct}% ({carbs_today}g)")
                st.write(f"🧈 Fat: {fat_pct}% ({fat_today}g)")
            with col_b:
                st.write(f"🌾 Fiber: {fiber_pct}% ({fiber_today}g)")
                st.write(f"🍋 Vitamins: {vitamins_pct}%")
                st.write(f"⚡ Minerals: {minerals_pct}%")
