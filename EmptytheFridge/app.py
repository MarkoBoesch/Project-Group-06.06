# app.py
# Main file of the app. Everything comes together here.
#
# This file is the entry point for the Streamlit app. It:
# - Sets up the page configuration
# - Loads recipes from TheMealDB API on the first run
# - Routes the user between the three main pages:
#       1. Enter Ingredients       (find recipes based on what you have at home)
#       2. History and Recommendations   (cooked recipes + ML-based recommendations)
#       3. Statistics              (cost / CO2 / nutrition overview)
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
# Machine-learning recommendation logic.
from recommender import calculate_recommendations, calculate_recommendations_by_rating
# Static data: pantry staples, diet filters, CHF prices, display name dictionary.
from constants import base_ingredients, INGREDIENT_VALUE_CHF, NON_VEGAN_INGREDIENTS, NON_VEGETARIAN_INGREDIENTS, ingredient_dictionary
# Loader that pulls all recipes from TheMealDB API into our local database.
from api_loader import load_api_recipes

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

def calculate_costs(recipe):
    """Goes through all ingredients and adds the value per ingredient."""
    total = 0
    # Ingredients are stored as a comma-separated string in the DB,
    # so we split them back into a list of keys.
    ingredient_keys = recipe["ingredients"].split(",")
    for key in ingredient_keys:
        key = key.strip()
        # Fall back to 0.50 CHF for unknown ingredients (e.g. ones added
        # by the API loader that aren't in our price table).
        total += INGREDIENT_VALUE_CHF.get(key, 0.50)
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
# diet/time/difficulty/allergen filters, and get matching recipes back.
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
    ingredient_display_names = [i["name"] for i in all_ingredients]

    st.subheader("Select Ingredients")

    selected_display_names = st.multiselect(
        "Type to search and select your ingredients:",
        options=ingredient_display_names,
        placeholder="e.g. Potato, Egg, Tomatoes..."
    )

    # Convert display names back into internal keys for matching.
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
    # filters. Recipes that pass are then ranked by how many extra
    # ingredients they still require. The ones requiring the fewest or none
    # appear higher up in the results.

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

                # Ingredient match scoring: count how many of the recipe's
                # ingredients the user has, and how many are still missing
                # (pantry staples like salt/oil are assumed to be at home
                # and are excluded from the missing count).

                recipe_ingredients = [i.strip() for i in recipe["ingredients"].split(",")]

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
                # ingredients - otherwise the result feels disconnected.
                if present_ingredients > 0:
                    matching_recipes.append({
                        "recipe": recipe,
                        "present": present_ingredients,
                        "missing": missing_ingredients
                    })

            # Sort by most matching ingredients first.
            # Primary sort: how many of the user's selected ingredients the recipe uses (more = better).
            # Tiebreaker: how many ingredients are still missing (fewer = better).
            def by_best_match(entry):
                return (-entry["present"], entry["missing"])

            matching_recipes.sort(key=by_best_match)

            # Persist results in session_state so they survive reruns
            # triggered by other widgets (e.g. "Mark as Cooked").
            st.session_state.search_results = matching_recipes
            st.session_state.show_results = True

    # SHOW RESULTS
    # Renders each matching recipe as a collapsible expander containing
    # quick stats, a colour-coded ingredient list, instructions, and a
    # "Mark as Cooked" button that writes a history entry.

    if "show_results" in st.session_state and st.session_state.show_results:

        results = st.session_state.search_results

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

                    # Render ingredients via the shared helper. Passing
                    # selected_keys enables 3-group mode (have/pantry/missing
                    # with the green tick group) plus the success message
                    # when nothing is missing.
                    render_recipe_ingredients(recipe, selected_keys=selected_keys)

                    st.divider()

                    # Cooking instructions pulled from TheMealDB (loaded via api_loader.py).
                    st.subheader("👨‍🍳 Instructions")
                    st.write(recipe["instructions"])

                    # "Mark as Cooked" writes today's date and the recipe ID
                    # into the history table, which feeds the Recommendations
                    # and Statistics pages. The unique key prevents Streamlit
                    # from confusing buttons across multiple expanders.
                    if st.button("✅ Mark as Cooked", key=f"cook_{recipe['id']}"):
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        save_history(recipe["id"], today)
                        st.success(f"'{name}' added to your cooking history!")
                        st.rerun()


# -----------------------------------------------------------------------------
# PAGE 2: HISTORY AND RECOMMENDATIONS
# Shows previously cooked recipes (with optional star ratings) and a list
# of personalised recommendations computed by the recommender module
# (cosine similarity on ingredient vectors).
# -----------------------------------------------------------------------------

# Only when the user has selected "📖 History and Recommendations" in the navigation bar
# does this whole block execute.
elif page == "📖 History and Recommendations":

    st.header("📖 History and Recommendations")

    history = load_history()
    all_recipes = load_all_recipes()

    # COOKING HISTORY
    # Each cooked recipe gets its own expander showing date, calories
    # and a 5-star rating widget. Once a rating has been saved, the
    # slider is replaced by the rating itself.

    st.subheader("Your Cooking History")

    if len(history) == 0:
        st.info("You haven't cooked any recipes yet. Go to the home page and find your first recipe!")
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

    # ML RECOMMENDATIONS — SIMILAR RECIPES (BASED ON LAST COOKED)
    # calculate_recommendations() (in recommender.py) builds a 0/1
    # ingredient matrix for all recipes and uses cosine similarity to
    # find recipes similar to the user's most recent cook.

    # Track which recipe IDs are shown in this first section so that the
    # second section (rating-based) can exclude them and avoid duplicates.
    # Initialised here so it's always defined, even when section 1 is empty.
    shown_ids = []

    st.divider()
    st.subheader("🍳 Recommendations of similar recipes")
    st.caption("Personalised suggestions calculated with machine learning based on your cooking history.")

    if len(history) == 0:
        st.info("Cook your first recipe to unlock personalised recommendations!")
    else:
        recommendations = calculate_recommendations(history, all_recipes, num_recommendations=4)

        if not recommendations:
            st.info("No recommendations available yet.")
        else:
            # Remember which IDs we are about to display so the next section
            # can skip them.
            shown_ids = [rec["id"] for rec in recommendations]

            # Render each recommendation in its own expander, similar
            # to the search results page.
            for rec in recommendations:
                rec_name = rec["name"]

                with st.expander(f"🍽️ {rec_name} — {rec['time_minutes']} min · {rec['difficulty']}"):

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Cooking time", f"{rec['time_minutes']} min")
                    with col_b:
                        st.metric("Difficulty", rec["difficulty"])
                    with col_c:
                        st.metric("Calories", f"{rec['calories']} kcal")

                    # Render ingredients via the shared helper. No
                    # selected_keys here, because on the History and 
                    # Recommendations page the user did not enter what 
                    # they currently have at home.
                    render_recipe_ingredients(rec)

                    # Instructions come from TheMealDB (loaded via api_loader.py).
                    st.divider()
                    st.subheader("👨\u200d🍳 Instructions")
                    st.write(rec["instructions"])

                    # Same "Mark as Cooked" mechanism as on the search page,
                    # but with a different key prefix to avoid conflicts.
                    if st.button("✅ Mark as Cooked", key=f"rec_cook_{rec['id']}"):
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        save_history(rec["id"], today)
                        st.success(f"'{rec_name}' added to your cooking history!")
                        st.rerun()

    # ML RECOMMENDATIONS — BECAUSE YOU LIKED IT LAST TIME (BASED ON RATINGS)
    # calculate_recommendations_by_rating() reuses the same cosine-similarity
    # logic, but builds a "user taste profile" as a weighted mean of all rated
    # recipe vectors (rating used as the weight). It then compares that
    # profile to every recipe. If the user has not cooked or rated anything
    # yet, the function returns an empty list so we can show a warning here.
    # We also pass shown_ids so the recipes already displayed in the section 
    # above are excluded, preventing the two sections from overlapping.

    st.divider()
    st.subheader("⭐ Because you liked it last time")
    st.caption("Recipes that match your taste profile, weighted by the ratings you gave to past meals.")

    if len(history) == 0:
        st.warning("You have to cook and rate a recipe first before a recommendation can be given here.")
    else:
        # Filter for entries that actually have a rating. The rating-based
        # recommender needs at least one rated recipe to build a taste profile.
        rated_history = [h for h in history if h.get("rating")]
        if not rated_history:
            st.warning("You have to rate your cooked recipes first before a recommendation can be given here.")
        else:
            rated_recommendations = calculate_recommendations_by_rating(
                history, all_recipes, num_recommendations=4, exclude_ids=shown_ids
            )

            # Same expander layout as the section above, just a different
            # button-key prefix to avoid Streamlit key collisions.
            for rec in rated_recommendations:
                rec_name = rec["name"]

                with st.expander(f"🍽️ {rec_name} — {rec['time_minutes']} min · {rec['difficulty']}"):

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Cooking time", f"{rec['time_minutes']} min")
                    with col_b:
                        st.metric("Difficulty", rec["difficulty"])
                    with col_c:
                        st.metric("Calories", f"{rec['calories']} kcal")

                    # Render ingredients via the shared helper (same as
                    # the section above — see render_recipe_ingredients).
                    render_recipe_ingredients(rec)

                    # Instructions come from TheMealDB (loaded via api_loader.py).
                    st.divider()
                    st.subheader("👨\u200d🍳 Instructions")
                    st.write(rec["instructions"])

                    # Same "Mark as Cooked" mechanism as above, but with a
                    # different key prefix (rated_cook_) so Streamlit doesn't
                    # confuse it with the buttons in the section above.
                    if st.button("✅ Mark as Cooked", key=f"rated_cook_{rec['id']}"):
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        save_history(rec["id"], today)
                        st.success(f"'{rec_name}' added to your cooking history!")
                        st.rerun()


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
                total_costs += calculate_costs(recipe)
                # Pantry staples are excluded so they don't inflate the count.
                recipe_ingredients = []
                for piece in recipe["ingredients"].split(","):
                    cleaned = piece.strip()
                    recipe_ingredients.append(cleaned)

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
                help="Based on the estimated value of the ingredients used."
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
                cost = calculate_costs(recipe)
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

            # Convert absolute values into percentages of daily intake.
            # Reference values are rough adult averages. Each percentage is
            # capped at 100 so the radar chart stays in bounds.
            # Vitamins/Minerals are already stored on a 0-100 scale.
            calories_pct   = min(100, round(calories_today / 2000 * 100))
            protein_pct    = min(100, round(protein_today / 50 * 100))
            carbs_pct      = min(100, round(carbs_today / 260 * 100))
            fat_pct        = min(100, round(fat_today / 70 * 100))
            fiber_pct      = min(100, round(fiber_today / 30 * 100))
            vitamins_pct   = min(100, vitamins_today)
            minerals_pct   = min(100, minerals_today)

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

            # Detail breakdown below the chart:
            # same numbers as in the radar, plus the absolute values
            # in parentheses so the user can see what is behind the %.
            st.write("Detail view (% of daily intake):")

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