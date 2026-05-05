# app.py
# Main file of the app. Everything comes together here.
#
# To start the app, type in the terminal: streamlit run app.py
# -----------------------------------------------------------------------------

import streamlit as st
import datetime

from database import (
    load_all_recipes,
    load_recipe,
    load_all_ingredients,
    load_history,
    save_history,
    update_rating
)
from recommender import calculate_recommendations, similar_recipes
from recipes import base_ingredients, INGREDIENT_VALUE_CHF
from api_loader import load_api_recipes

# -----------------------------------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="EmptyTheFridge",
    page_icon="👨‍🍳",
    layout="wide"
)

# -----------------------------------------------------------------------------
# LOAD API RECIPES ON START
# Only runs once thanks to session_state.
# -----------------------------------------------------------------------------

if "api_loaded" not in st.session_state:
    with st.spinner("Loading recipes from TheMealDB... (first start only)"):
        load_api_recipes()
    st.session_state.api_loaded = True

# -----------------------------------------------------------------------------
# CALCULATE COSTS
# Calculates the estimated ingredient value of a recipe in CHF.
# -----------------------------------------------------------------------------

def calculate_costs(recipe):
    """Goes through all ingredients and adds the value per ingredient."""
    total = 0
    ingredient_keys = recipe["ingredients"].split(",")
    for key in ingredient_keys:
        key = key.strip()
        total += INGREDIENT_VALUE_CHF.get(key, 0.50)  # Default 0.50 for unknown ingredients
    return round(total, 2)

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------

col_left, col_right = st.columns([4, 1])

with col_left:
    st.title("🧊 EmptyTheFridge")

st.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Enter Ingredients",
        "📜 History",
        "📊 Statistics",
    ]
)

# -----------------------------------------------------------------------------
# PAGE 1: ENTER INGREDIENTS
# -----------------------------------------------------------------------------

if page == "🏠 Enter Ingredients":

    st.header("What do you have at home?")
    st.write("Select the ingredients you want to use up.")

    all_ingredients = load_all_ingredients()
    ingredient_display_names = [i["name"] for i in all_ingredients]

    st.subheader("Select Ingredients")

    selected_display_names = st.multiselect(
        "Type to search and select your ingredients:",
        options=ingredient_display_names,
        placeholder="e.g. Potato, Egg, Tomatoes..."
    )

    # Convert display names back to keys
    selected_keys = []
    for display_name in selected_display_names:
        for ingredient in all_ingredients:
            if ingredient["name"] == display_name:
                selected_keys.append(ingredient["key"])

    # ------------------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------------------
    st.subheader("Filters")

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
        allergen_options = ["gluten", "dairy", "egg", "fish", "soy", "nuts"]
        allergies = st.multiselect("Allergies / Intolerances", options=allergen_options)

    # ------------------------------------------------------------------
    # SEARCH RECIPES
    # ------------------------------------------------------------------
    if st.button("🔍 Find Recipes", type="primary"):

        if len(selected_keys) == 0:
            st.warning("Please select at least one ingredient.")
        else:
            all_recipes = load_all_recipes()
            matching_recipes = []

            for recipe in all_recipes:

                # Check allergens
                recipe_allergens = recipe["allergens"].split(",") if recipe["allergens"] else []
                allergen_found = any(allergy in recipe_allergens for allergy in allergies)
                if allergen_found:
                    continue

                # Check time
                if recipe["time_minutes"] > max_time:
                    continue

                # Check difficulty
                if difficulty != "All" and recipe["difficulty"] != difficulty:
                    continue

                # Compare ingredients
                recipe_ingredients = recipe["ingredients"].split(",")

                present_ingredients = sum(1 for key in selected_keys if key in recipe_ingredients)

                missing_ingredients = sum(
                    1 for ingredient in recipe_ingredients
                    if ingredient not in selected_keys and ingredient not in base_ingredients
                )

                if present_ingredients > 0:
                    matching_recipes.append({
                        "recipe": recipe,
                        "present": present_ingredients,
                        "missing": missing_ingredients
                    })

            matching_recipes.sort(key=lambda x: x["missing"])
            st.session_state.search_results = matching_recipes
            st.session_state.show_results = True
            st.session_state.my_ingredients = selected_keys

    # ------------------------------------------------------------------
    # SHOW RESULTS
    # ------------------------------------------------------------------
    if "show_results" in st.session_state and st.session_state.show_results:

        results = st.session_state.search_results

        if len(results) == 0:
            st.info("No matching recipes found. Try different ingredients or filters.")
        else:
            st.subheader(f"{len(results)} recipes found")

            for entry in results:
                recipe = entry["recipe"]
                name = recipe["name"]

                with st.expander(f"🍽️ {name} — missing: {entry['missing']} ingredients"):

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Cooking time", f"{recipe['time_minutes']} min")
                    with col_b:
                        st.metric("Difficulty", recipe["difficulty"])
                    with col_c:
                        st.metric("Calories", f"{recipe['calories']} kcal")

                    st.write(recipe["instructions"])

                    # Add to history button
                    if st.button("✅ Mark as Cooked", key=f"cook_{recipe['id']}"):
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        save_history(recipe["id"], today)
                        st.success(f"'{name}' added to your cooking history!")
                        st.rerun()

    # ------------------------------------------------------------------
    # ML RECOMMENDATIONS
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("🤖 Recommendations for you")

    history = load_history()
    all_recipes = load_all_recipes()

    if len(history) == 0:
        st.info("No recommendations yet - cook your first recipe!")
    else:
        recommendations = calculate_recommendations(history, all_recipes, num_recommendations=3)
        for recipe in recommendations:
            st.write(f"👉 {recipe['name']} — {recipe['time_minutes']} min")


# -----------------------------------------------------------------------------
# PAGE 2: HISTORY
# -----------------------------------------------------------------------------

elif page == "📜 History":

    st.header("Your Cooking History")

    history = load_history()

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

        st.divider()
        st.subheader("🤖 Based on your history")
        st.caption("These recommendations are calculated using machine learning.")

        all_recipes = load_all_recipes()
        recommendations = calculate_recommendations(history, all_recipes, num_recommendations=5)

        for recipe in recommendations:
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.write(f"👉 {recipe['name']}")
            with col_b:
                st.write(f"⏱️ {recipe['time_minutes']} min")
            with col_c:
                st.write(f"📊 {recipe['difficulty']}")


# -----------------------------------------------------------------------------
# PAGE 3: STATISTICS
# -----------------------------------------------------------------------------

elif page == "📊 Statistics":

    st.header("Your Statistics")

    history = load_history()

    if len(history) == 0:
        st.info("No statistics available yet. Cook some recipes first!")
    else:

        st.subheader("Overview")

        num_recipes = len(history)
        total_costs = 0
        total_calories = 0

        for entry in history:
            recipe = load_recipe(entry["recipe_id"])
            if recipe:
                total_costs += calculate_costs(recipe)
            if entry["calories"]:
                total_calories += entry["calories"]

        total_costs = round(total_costs, 2)
        saved_co2 = round(total_costs * 0.8, 1)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Cooked Recipes", num_recipes)
        with col2:
            st.metric(
                "💰 Saved Costs",
                f"CHF {total_costs}",
                help="Based on the estimated value of the ingredients used."
            )
        with col3:
            st.metric("🌱 Saved CO2", f"{saved_co2} kg")
        with col4:
            st.metric("Total Calories", f"{total_calories} kcal")

        # ------------------------------------------------------------------
        # DAILY NUTRITION RADAR CHART
        # Shows combined nutritional values of all recipes cooked today.
        # ------------------------------------------------------------------
        st.divider()
        st.subheader("🕸️ Today's Nutritional Values")
        st.caption("Combined nutritional values of all recipes cooked today. Outer edge = 100% daily intake.")

        today = datetime.date.today().strftime("%Y-%m-%d")

        today_entries = [entry for entry in history if entry["date"] == today]

        if len(today_entries) == 0:
            st.info("No recipes cooked today yet. Cook something and come back!")
        else:
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

            # Calculate percentages of daily recommended intake
            calories_pct   = min(100, round(calories_today / 2000 * 100))
            protein_pct    = min(100, round(protein_today / 50 * 100))
            carbs_pct      = min(100, round(carbs_today / 260 * 100))
            fat_pct        = min(100, round(fat_today / 70 * 100))
            fiber_pct      = min(100, round(fiber_today / 30 * 100))
            vitamins_pct   = min(100, vitamins_today)
            minerals_pct   = min(100, minerals_today)

            import plotly.graph_objects as go

            categories = ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Vitamins", "Minerals"]

            values = [
                calories_pct, protein_pct, carbs_pct, fat_pct,
                fiber_pct, vitamins_pct, minerals_pct
            ]

            # Repeat first value at end to close the radar chart
            categories_closed = categories + [categories[0]]
            values_closed = values + [values[0]]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill="toself",
                name="Today's Daily Intake",
                line_color="green",
                fillcolor="rgba(0, 200, 0, 0.2)"
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix="%"
                    )
                ),
                showlegend=True,
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)

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
