# recipes.py
# All recipes are stored here.
# To add a new recipe, just copy the last block and fill it in.
# Instructions are split into numbered steps (separated by \n).
# -----------------------------------------------------------------------------

# Base ingredients assumed to always be available at home
base_ingredients = [
    "salt", "pepper", "oil", "butter", "sugar", "flour", "water",
    "garlic", "onion", "vegetable_broth", "olive_oil", "vinegar",
    "baking_powder", "baking_soda", "cornstarch"
]

# Ingredients that are NOT vegan (animal products)
NON_VEGAN_INGREDIENTS = {
    "egg", "milk", "butter", "cream", "cheese", "mozzarella", "parmesan",
    "yogurt", "cream_cheese", "feta", "ricotta", "sour_cream", "heavy_cream",
    "chicken_breast", "ground_beef", "bacon", "pork", "salmon", "tuna",
    "shrimp", "lamb", "turkey", "sausage", "ham", "prosciutto", "cod",
    "honey", "mayonnaise", "worcestershire",
}

# Ingredients that are NOT vegetarian (meat/fish but dairy/eggs are ok)
NON_VEGETARIAN_INGREDIENTS = {
    "chicken_breast", "ground_beef", "bacon", "pork", "salmon", "tuna",
    "shrimp", "lamb", "turkey", "sausage", "ham", "prosciutto", "cod",
    "worcestershire",
}

# Estimated CHF value per unit/portion of each ingredient
INGREDIENT_VALUE_CHF = {
    "potato": 0.30, "carrot": 0.20, "celery": 0.30, "onion": 0.20,
    "garlic": 0.10, "tomato": 0.40, "zucchini": 0.50, "bell_pepper": 0.60,
    "spinach": 0.80, "broccoli": 0.70, "mushroom": 0.80, "leek": 0.60,
    "cauliflower": 0.70, "cucumber": 0.40, "lettuce": 0.50, "corn": 0.40,
    "peas": 0.40, "green_beans": 0.50, "eggplant": 0.60, "sweet_potato": 0.50,
    "chicken_breast": 2.50, "ground_beef": 2.80, "bacon": 1.50, "pork": 2.20,
    "salmon": 3.50, "tuna": 1.20, "shrimp": 3.00, "egg": 0.40, "milk": 0.20,
    "butter": 0.30, "cream": 0.60, "cheese": 0.80, "mozzarella": 1.20,
    "parmesan": 0.90, "yogurt": 0.50, "cream_cheese": 0.70, "pasta": 0.40,
    "rice": 0.30, "bread": 0.40, "flour": 0.10, "oats": 0.20, "lentils": 0.40,
    "chickpeas": 0.50, "tomato_sauce": 0.50, "vegetable_broth": 0.20,
    "olive_oil": 0.20, "oil": 0.10, "soy_sauce": 0.15, "lemon": 0.30,
    "apple": 0.40, "banana": 0.30, "avocado": 1.20, "feta": 1.00,
    "ricotta": 0.90, "sour_cream": 0.60, "tofu": 1.50, "asparagus": 1.20,
    "kale": 0.80, "beetroot": 0.40, "spring_onion": 0.30, "ginger": 0.20,
    "lime": 0.30, "mango": 1.00, "strawberry": 1.20, "blueberry": 1.50,
    "raspberry": 1.50, "cherry": 1.20, "peach": 0.80, "pear": 0.50,
    "pumpkin": 0.60, "white_cabbage": 0.30, "red_cabbage": 0.40,
    "fennel": 0.80, "lamb": 3.50, "turkey": 2.50, "sausage": 1.50,
    "ham": 1.20, "prosciutto": 1.80, "cod": 2.50, "coconut_milk": 0.60,
    "tahini": 0.50, "pesto": 0.70, "dijon_mustard": 0.20, "honey": 0.30,
    "mayonnaise": 0.20, "hot_sauce": 0.15, "bbq_sauce": 0.30,
    "worcestershire": 0.15, "heavy_cream": 0.70,
}

# Maps ingredient keys to their English display names
ingredient_dictionary = {
    "potato": "Potato", "carrot": "Carrot", "celery": "Celery",
    "onion": "Onion", "garlic": "Garlic", "tomato": "Tomato",
    "zucchini": "Zucchini", "bell_pepper": "Bell Pepper", "spinach": "Spinach",
    "broccoli": "Broccoli", "mushroom": "Mushrooms", "leek": "Leek",
    "cauliflower": "Cauliflower", "cucumber": "Cucumber", "lettuce": "Lettuce",
    "corn": "Corn", "peas": "Peas", "green_beans": "Green Beans",
    "eggplant": "Eggplant", "sweet_potato": "Sweet Potato", "avocado": "Avocado",
    "asparagus": "Asparagus", "kale": "Kale", "beetroot": "Beetroot",
    "spring_onion": "Spring Onion", "ginger": "Ginger", "pumpkin": "Pumpkin",
    "white_cabbage": "White Cabbage", "red_cabbage": "Red Cabbage",
    "fennel": "Fennel", "lemon": "Lemon", "lime": "Lime", "apple": "Apple",
    "banana": "Banana", "mango": "Mango", "strawberry": "Strawberry",
    "blueberry": "Blueberry", "raspberry": "Raspberry", "cherry": "Cherry",
    "peach": "Peach", "pear": "Pear",
    "chicken_breast": "Chicken Breast", "ground_beef": "Ground Beef",
    "bacon": "Bacon", "pork": "Pork", "salmon": "Salmon", "tuna": "Tuna",
    "shrimp": "Shrimp", "lamb": "Lamb", "turkey": "Turkey", "sausage": "Sausage",
    "ham": "Ham", "prosciutto": "Prosciutto", "cod": "Cod",
    "egg": "Egg", "milk": "Milk", "butter": "Butter", "cream": "Cream",
    "cheese": "Cheese", "mozzarella": "Mozzarella", "parmesan": "Parmesan",
    "yogurt": "Yogurt", "cream_cheese": "Cream Cheese", "feta": "Feta",
    "ricotta": "Ricotta", "sour_cream": "Sour Cream",
    "pasta": "Pasta", "rice": "Rice", "bread": "Bread", "flour": "Flour",
    "oats": "Oats", "lentils": "Lentils", "chickpeas": "Chickpeas", "tofu": "Tofu",
    "tomato_sauce": "Tomato Sauce", "vegetable_broth": "Vegetable Broth",
    "olive_oil": "Olive Oil", "oil": "Oil", "salt": "Salt", "pepper": "Pepper",
    "sugar": "Sugar", "vinegar": "Vinegar", "soy_sauce": "Soy Sauce",
    "water": "Water", "baking_powder": "Baking Powder", "coconut_milk": "Coconut Milk",
    "tahini": "Tahini", "pesto": "Pesto", "dijon_mustard": "Dijon Mustard",
    "honey": "Honey", "mayonnaise": "Mayonnaise", "hot_sauce": "Hot Sauce",
    "bbq_sauce": "BBQ Sauce", "worcestershire": "Worcestershire Sauce",
}


recipes = [

    {
        "id": 1,
        "name": "Potato Soup",
        "ingredients": ["potato", "carrot", "celery", "onion", "vegetable_broth", "salt", "pepper"],
        "amounts": "potato:500g,carrot:2 pcs,celery:2 stalks,onion:1 pc,vegetable_broth:800ml",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "",
        "calories": 180, "protein": 4, "carbohydrates": 35, "fat": 2, "fiber": 4, "vitamins": 30, "minerals": 20,
        "instructions": "**Step 1 - Prepare the vegetables:** Peel the potatoes and carrots and cut into even 2 cm cubes. Wash the celery stalks and slice them. Peel and finely chop the onion.\n**Step 2 - Saute the onion:** Heat a large pot over medium heat. Add a tablespoon of oil and saute the onion for 3-4 minutes until translucent and soft.\n**Step 3 - Fry the vegetables:** Add potatoes, carrots and celery to the pot. Stir and fry together for 2 minutes to develop the flavours.\n**Step 4 - Add the broth:** Pour in the vegetable broth. Bring to a boil, then reduce heat to low.\n**Step 5 - Cook:** Let the soup simmer for 20-25 minutes until all vegetables are completely soft. Test with a knife - it should slide through a potato piece without resistance.\n**Step 6 - Season and serve:** Season generously with salt and pepper. Serve as is or partially blend for a creamier texture."
    },
    {
        "id": 2,
        "name": "Pancakes",
        "ingredients": ["egg", "milk", "flour", "butter", "sugar", "salt"],
        "amounts": "egg:2 pcs,milk:300ml,flour:150g,butter:20g,sugar:1 tbsp",
        "time_minutes": 20,
        "difficulty": "easy",
        "allergens": "gluten,dairy,egg",
        "calories": 320, "protein": 10, "carbohydrates": 45, "fat": 11, "fiber": 1, "vitamins": 10, "minerals": 15,
        "instructions": "**Step 1 - Mix the batter:** Sift the flour and a pinch of salt into a bowl. Make a well in the centre. Add the eggs and half the milk and whisk from the centre outwards until you have a smooth, lump-free batter.\n**Step 2 - Thin the batter:** Stir in the remaining milk and the sugar. The batter should be as thin as pouring cream. If too thick, add a splash more milk. Let the batter rest for 5 minutes.\n**Step 3 - Heat the pan:** Heat a non-stick frying pan over medium-high heat. Add a small knob of butter and let it melt until it just starts to foam.\n**Step 4 - Cook the first pancake:** Pour a ladleful of batter into the pan and immediately swirl the pan so the batter spreads out thin and even.\n**Step 5 - Flip:** Cook for 1-2 minutes until the underside is golden and the surface no longer looks wet. Flip with a spatula and cook for another 30-60 seconds.\n**Step 6 - Finish the batch:** Add a little butter for each pancake and repeat until all the batter is used. Serve warm with sugar, lemon or jam of your choice."
    },
    {
        "id": 3,
        "name": "Spaghetti Bolognese",
        "ingredients": ["pasta", "ground_beef", "tomato_sauce", "onion", "garlic", "carrot", "salt", "pepper", "olive_oil"],
        "amounts": "pasta:400g,ground_beef:300g,tomato_sauce:400g,onion:1 pc,carrot:1 pc",
        "time_minutes": 45,
        "difficulty": "medium",
        "allergens": "gluten",
        "calories": 520, "protein": 30, "carbohydrates": 60, "fat": 16, "fiber": 5, "vitamins": 20, "minerals": 25,
        "instructions": "**Step 1 - Prepare the vegetables:** Peel and finely chop the onion and garlic. Peel the carrot and cut into very small cubes.\n**Step 2 - Cook the soffritto:** Heat olive oil in a large pot over medium heat. Add the onion, garlic and carrot and cook for 5-6 minutes until soft.\n**Step 3 - Brown the beef:** Add the ground beef and break it up with a wooden spoon. Cook on higher heat for 6-8 minutes until completely browned.\n**Step 4 - Simmer the sauce:** Pour in the tomato sauce and stir well. Reduce heat to low and simmer for 20 minutes. Season with salt and pepper.\n**Step 5 - Cook the pasta:** Bring a large pot of salted water to a boil. Cook pasta al dente. Reserve 1 cup of pasta water before draining.\n**Step 6 - Combine and serve:** Add the pasta to the sauce and mix well. Add pasta water if the sauce is too thick. Serve immediately."
    },
    {
        "id": 4,
        "name": "Vegetable Frittata",
        "ingredients": ["egg", "zucchini", "bell_pepper", "onion", "cheese", "salt", "pepper", "olive_oil"],
        "amounts": "egg:4 pcs,zucchini:1 pc,bell_pepper:1 pc,onion:1 pc,cheese:50g",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "egg,dairy",
        "calories": 280, "protein": 18, "carbohydrates": 8, "fat": 20, "fiber": 3, "vitamins": 40, "minerals": 30,
        "instructions": "**Step 1 - Preheat the grill:** Preheat the oven grill to 200C.\n**Step 2 - Cut the vegetables:** Slice the zucchini into half moons. Cut the bell pepper into thin strips. Slice the onion into half rings.\n**Step 3 - Fry the vegetables:** Heat olive oil in an oven-safe pan. Saute the onion for 3 minutes. Add the bell pepper and cook for 3 more minutes. Add the zucchini and fry for another 3 minutes until lightly browned.\n**Step 4 - Prepare the eggs:** Crack the eggs into a bowl. Season with salt and pepper. Whisk until fully combined.\n**Step 5 - Pour in the eggs:** Spread vegetables evenly in the pan. Pour the egg mixture over them. Cook over medium heat for 4-5 minutes until the bottom is set.\n**Step 6 - Grill and serve:** Scatter cheese over the frittata. Place under the oven grill for 3-4 minutes until golden and set. Cut into wedges and serve."
    },
    {
        "id": 5,
        "name": "Lentil Stew",
        "ingredients": ["lentils", "carrot", "potato", "onion", "vegetable_broth", "tomato", "salt", "pepper"],
        "amounts": "lentils:250g,carrot:2 pcs,potato:2 pcs,onion:1 pc,tomato:2 pcs,vegetable_broth:800ml",
        "time_minutes": 40,
        "difficulty": "easy",
        "allergens": "",
        "calories": 310, "protein": 18, "carbohydrates": 50, "fat": 3, "fiber": 15, "vitamins": 25, "minerals": 35,
        "instructions": "**Step 1 - Prepare the vegetables:** Peel the carrots and potatoes and cut into 1-2 cm cubes. Peel and finely chop the onion. Wash the tomatoes and cut into rough chunks.\n**Step 2 - Rinse the lentils:** Rinse lentils thoroughly under cold water in a sieve.\n**Step 3 - Saute the onion:** Heat oil in a large pot. Add the onion and cook for 4-5 minutes until soft and golden.\n**Step 4 - Add the vegetables:** Add carrots and potatoes to the pot. Stir and cook for 2 minutes.\n**Step 5 - Add liquid:** Pour in the lentils and vegetable broth. Bring to a boil. Reduce heat and simmer for 20 minutes until soft.\n**Step 6 - Add tomatoes and season:** Add the tomato chunks and simmer for 5 more minutes. Season generously with salt and pepper."
    },
    {
        "id": 6,
        "name": "Chicken with Vegetables",
        "ingredients": ["chicken_breast", "zucchini", "bell_pepper", "tomato", "onion", "garlic", "olive_oil", "salt", "pepper"],
        "amounts": "chicken_breast:400g,zucchini:1 pc,bell_pepper:1 pc,tomato:2 pcs,onion:1 pc",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "",
        "calories": 350, "protein": 40, "carbohydrates": 12, "fat": 14, "fiber": 4, "vitamins": 45, "minerals": 30,
        "instructions": "**Step 1 - Prepare the chicken:** Pat chicken dry and cut into even 2 cm strips. Season with salt and pepper.\n**Step 2 - Cut the vegetables:** Slice zucchini into half moons. Deseed and slice bell pepper. Cut tomatoes into chunks. Slice onion and finely chop garlic.\n**Step 3 - Fry the chicken:** Heat olive oil in a large pan over high heat. Fry chicken strips for 4-5 minutes until golden on all sides. Remove and set aside.\n**Step 4 - Fry the vegetables:** In the same oil, saute onion and garlic for 2 minutes. Add bell pepper and cook for 3 minutes. Add zucchini and cook for 3 more minutes.\n**Step 5 - Combine:** Return the chicken to the pan. Add tomatoes. Mix well and cook over medium heat for 5-7 minutes until the chicken is fully cooked.\n**Step 6 - Season and serve:** Season again with salt and pepper. Serve with bread, rice or pasta."
    },
    {
        "id": 7,
        "name": "Spinach Cream Cheese Pasta",
        "ingredients": ["pasta", "spinach", "cream_cheese", "garlic", "parmesan", "salt", "pepper", "olive_oil"],
        "amounts": "pasta:400g,spinach:200g,cream_cheese:150g,parmesan:40g,garlic:2 cloves",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "gluten,dairy",
        "calories": 480, "protein": 20, "carbohydrates": 62, "fat": 17, "fiber": 4, "vitamins": 50, "minerals": 25,
        "instructions": "**Step 1 - Boil water:** Bring a large pot of water to a boil. Salt it generously.\n**Step 2 - Cook the pasta:** Cook pasta al dente according to packet instructions. Reserve 1 cup of pasta water before draining.\n**Step 3 - Fry the garlic:** Heat olive oil in a large pan. Finely chop garlic and cook for 1-2 minutes until fragrant.\n**Step 4 - Add the spinach:** Add spinach to the pan. Toss until fully wilted, about 2 minutes.\n**Step 5 - Make the sauce:** Add cream cheese and a splash of pasta water. Stir into a creamy sauce. Season with salt and pepper.\n**Step 6 - Add pasta and serve:** Add the drained pasta to the sauce. Mix well. Add more pasta water if too thick. Divide onto plates and top with grated parmesan."
    },
    {
        "id": 8,
        "name": "Tomato Soup",
        "ingredients": ["tomato", "onion", "garlic", "vegetable_broth", "cream", "salt", "pepper", "olive_oil"],
        "amounts": "tomato:600g,onion:1 pc,vegetable_broth:300ml,cream:100ml,garlic:2 cloves",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 160, "protein": 4, "carbohydrates": 18, "fat": 8, "fiber": 4, "vitamins": 35, "minerals": 20,
        "instructions": "**Step 1 - Prepare the tomatoes:** Wash and quarter the tomatoes.\n**Step 2 - Saute onion and garlic:** Heat olive oil in a large pot. Finely chop the onion and cook for 4-5 minutes until soft. Add garlic and cook for 1 more minute.\n**Step 3 - Add the tomatoes:** Add tomato pieces and cook for 3 minutes. Crush slightly with a spoon to release their juices.\n**Step 4 - Add broth and cook:** Pour in vegetable broth. Bring to a boil then simmer for 15 minutes until tomatoes are completely soft.\n**Step 5 - Blend:** Remove from heat. Blend completely smooth with an immersion blender.\n**Step 6 - Add cream and serve:** Return to heat. Stir in cream and heat briefly. Season with salt and pepper. Serve in warmed bowls."
    },
    {
        "id": 9,
        "name": "Fried Rice",
        "ingredients": ["rice", "egg", "carrot", "peas", "onion", "soy_sauce", "oil"],
        "amounts": "rice:300g,egg:2 pcs,carrot:1 pc,peas:100g,onion:1 pc,soy_sauce:3 tbsp",
        "time_minutes": 25,
        "difficulty": "medium",
        "allergens": "egg,soy",
        "calories": 380, "protein": 12, "carbohydrates": 65, "fat": 8, "fiber": 4, "vitamins": 20, "minerals": 20,
        "instructions": "**Step 1 - Cook and cool the rice:** Cook rice and let it cool completely. Day-old rice from the fridge works best.\n**Step 2 - Prepare the vegetables:** Peel the carrot and cut into very small cubes. Finely chop the onion.\n**Step 3 - Fry the vegetables:** Heat oil in a wok or large pan over high heat. Add onion and carrot and stir-fry for 3-4 minutes.\n**Step 4 - Add the peas:** Add peas and stir-fry for 1 minute.\n**Step 5 - Scramble the eggs:** Push everything to one side. Crack the eggs in and scramble until almost set, then mix with vegetables.\n**Step 6 - Fry the rice:** Add cold rice and fry on highest heat for 3-4 minutes, stirring constantly. Pour over soy sauce, mix well and serve immediately."
    },
    {
        "id": 10,
        "name": "Broccoli Cheese Soup",
        "ingredients": ["broccoli", "cheese", "onion", "vegetable_broth", "cream", "salt", "pepper", "butter"],
        "amounts": "broccoli:500g,cheese:100g,onion:1 pc,vegetable_broth:500ml,cream:150ml",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 290, "protein": 14, "carbohydrates": 15, "fat": 20, "fiber": 6, "vitamins": 55, "minerals": 30,
        "instructions": "**Step 1 - Prepare the broccoli:** Wash and cut into small florets. Peel the stalk and cut into cubes.\n**Step 2 - Saute the onion:** Melt butter in a large pot. Finely chop the onion and cook for 4-5 minutes until soft.\n**Step 3 - Add broccoli:** Add the broccoli and cook for 2 minutes.\n**Step 4 - Add broth and cook:** Pour in vegetable broth, bring to a boil and simmer for 12-15 minutes until very soft.\n**Step 5 - Blend:** Blend completely smooth with an immersion blender.\n**Step 6 - Melt in cheese and cream:** Return to low heat. Stir in cream. Grate the cheese and stir in gradually until fully melted and creamy. Season and serve."
    },
    {
        "id": 11,
        "name": "Lemon Salmon",
        "ingredients": ["salmon", "lemon", "garlic", "olive_oil", "salt", "pepper"],
        "amounts": "salmon:400g,lemon:1 pc,garlic:2 cloves",
        "time_minutes": 20,
        "difficulty": "easy",
        "allergens": "fish",
        "calories": 380, "protein": 42, "carbohydrates": 2, "fat": 22, "fiber": 0, "vitamins": 30, "minerals": 40,
        "instructions": "**Step 1 - Prepare the salmon:** Rinse and pat very dry with paper towels. Check for pin bones and remove.\n**Step 2 - Season:** Season both sides with salt and pepper. Squeeze half a lemon over and rub in lightly.\n**Step 3 - Heat the pan:** Heat olive oil in a pan over medium-high heat until it shimmers.\n**Step 4 - Fry the garlic:** Slice the garlic thinly and add to the oil. Fry for 30 seconds until fragrant.\n**Step 5 - Cook the salmon:** Place fillets skin-side down. Cook for 4-5 minutes without moving. Flip and cook for another 3-4 minutes until golden outside and slightly pink inside.\n**Step 6 - Rest and serve:** Let the salmon rest for 2 minutes. Serve with remaining lemon slices. Goes well with salad, rice or steamed vegetables."
    },
    {
        "id": 12,
        "name": "Chickpea Curry",
        "ingredients": ["chickpeas", "tomato", "onion", "garlic", "spinach", "vegetable_broth", "salt", "pepper", "oil"],
        "amounts": "chickpeas:400g,tomato:3 pcs,onion:1 pc,spinach:100g,vegetable_broth:200ml,garlic:2 cloves",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "",
        "calories": 310, "protein": 14, "carbohydrates": 45, "fat": 7, "fiber": 12, "vitamins": 35, "minerals": 30,
        "instructions": "**Step 1 - Prepare ingredients:** Peel and finely chop onion and garlic. Cut tomatoes into chunks. Drain and rinse chickpeas.\n**Step 2 - Fry onion and garlic:** Heat oil in a large pot. Fry onion for 5 minutes until golden. Add garlic and cook for 1 more minute.\n**Step 3 - Cook down the tomatoes:** Add tomato chunks and cook on higher heat for 5-7 minutes until they break down into a sauce.\n**Step 4 - Add chickpeas and broth:** Pour in chickpeas and vegetable broth. Stir well and bring to a boil.\n**Step 5 - Simmer:** Reduce heat and simmer for 15 minutes. Season with salt and pepper.\n**Step 6 - Stir in spinach and serve:** Stir in spinach and simmer for 2 minutes until wilted. Serve with rice or bread."
    },
    {
        "id": 13,
        "name": "Mushroom Omelette",
        "ingredients": ["egg", "mushroom", "onion", "cheese", "butter", "salt", "pepper"],
        "amounts": "egg:3 pcs,mushroom:150g,onion:1 pc,cheese:30g",
        "time_minutes": 15,
        "difficulty": "easy",
        "allergens": "egg,dairy",
        "calories": 310, "protein": 22, "carbohydrates": 6, "fat": 22, "fiber": 2, "vitamins": 20, "minerals": 20,
        "instructions": "**Step 1 - Prepare the filling:** Clean mushrooms with a damp paper towel and slice them. Finely chop the onion. Grate the cheese.\n**Step 2 - Fry the mushrooms:** Melt half the butter in a pan over medium-high heat. Fry onion for 2 minutes. Add mushrooms and cook for 4-5 minutes until golden. Season and set aside.\n**Step 3 - Prepare the eggs:** Crack eggs into a bowl. Season and whisk vigorously until fully combined.\n**Step 4 - Cook the omelette:** Melt remaining butter in the same pan. Pour in eggs and swirl the pan. Gently stir while the bottom sets.\n**Step 5 - Add the filling:** When the bottom is set but the surface is still slightly glossy, add mushrooms and cheese to one half.\n**Step 6 - Fold and serve:** Fold the other half over the filling. Slide onto a plate and serve immediately."
    },
    {
        "id": 14,
        "name": "Pasta with Tomato Sauce",
        "ingredients": ["pasta", "tomato_sauce", "garlic", "onion", "olive_oil", "salt", "pepper"],
        "amounts": "pasta:400g,tomato_sauce:500g,onion:1 pc,garlic:2 cloves",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "gluten",
        "calories": 420, "protein": 14, "carbohydrates": 80, "fat": 6, "fiber": 5, "vitamins": 20, "minerals": 15,
        "instructions": "**Step 1 - Boil water:** Bring a large pot of water to a boil and salt generously.\n**Step 2 - Prepare the sauce:** Peel and finely chop the onion and garlic.\n**Step 3 - Fry the sauce base:** Heat olive oil in a pot. Saute the onion for 4-5 minutes until soft. Add garlic and cook for 1 more minute.\n**Step 4 - Simmer the tomato sauce:** Pour in the tomato sauce. Simmer on low heat for 15 minutes. Season with salt and pepper.\n**Step 5 - Cook the pasta:** Cook pasta al dente. Reserve some pasta water.\n**Step 6 - Combine and serve:** Add pasta directly to the sauce and mix well. Add pasta water to loosen if needed. Sprinkle with parmesan if desired."
    },
    {
        "id": 15,
        "name": "Sweet Potato Mash",
        "ingredients": ["sweet_potato", "butter", "cream", "salt", "pepper"],
        "amounts": "sweet_potato:600g,butter:30g,cream:100ml",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 280, "protein": 4, "carbohydrates": 50, "fat": 9, "fiber": 6, "vitamins": 60, "minerals": 25,
        "instructions": "**Step 1 - Prepare the sweet potatoes:** Peel and cut into even 3 cm cubes.\n**Step 2 - Cook:** Place in a pot and cover with salted water. Bring to a boil and cook for 15-18 minutes until easily pierced with a knife.\n**Step 3 - Drain and steam dry:** Drain and let steam in the hot pot for 1-2 minutes to evaporate excess moisture.\n**Step 4 - Mash:** Mash vigorously with a potato masher until no large pieces remain.\n**Step 5 - Stir in butter and cream:** Add butter in small pieces and stir until melted. Then stir in cream until smooth and creamy.\n**Step 6 - Season and serve:** Season generously with salt and pepper. Goes well with meat, fish or vegetables."
    },
    {
        "id": 16,
        "name": "Tuna Salad",
        "ingredients": ["tuna", "lettuce", "tomato", "cucumber", "corn", "lemon", "olive_oil", "salt", "pepper"],
        "amounts": "tuna:200g,lettuce:1 head,tomato:2 pcs,cucumber:1 pc,corn:100g,lemon:1 pc",
        "time_minutes": 10,
        "difficulty": "easy",
        "allergens": "fish",
        "calories": 240, "protein": 28, "carbohydrates": 18, "fat": 7, "fiber": 5, "vitamins": 40, "minerals": 30,
        "instructions": "**Step 1 - Prepare the lettuce:** Wash, spin dry and tear into bite-sized pieces.\n**Step 2 - Cut the vegetables:** Slice or dice tomatoes. Slice or cut cucumber into half moons. Drain corn.\n**Step 3 - Prepare the tuna:** Drain and press out excess liquid. Flake gently with a fork.\n**Step 4 - Make the dressing:** Squeeze lemon juice into a small bowl. Whisk with olive oil, salt and pepper.\n**Step 5 - Assemble the salad:** Arrange lettuce on a plate. Distribute tomatoes, cucumber and corn on top. Add tuna.\n**Step 6 - Dress and serve:** Drizzle dressing over the salad and serve immediately."
    },
    {
        "id": 17,
        "name": "Oatmeal",
        "ingredients": ["oats", "milk", "banana", "sugar", "salt"],
        "amounts": "oats:100g,milk:300ml,banana:1 pc,sugar:1 tbsp",
        "time_minutes": 10,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 320, "protein": 10, "carbohydrates": 58, "fat": 7, "fiber": 6, "vitamins": 15, "minerals": 20,
        "instructions": "**Step 1 - Heat the milk:** Heat the milk in a pot over medium heat until it just starts to steam. Do not boil.\n**Step 2 - Stir in oats:** Stir in the oats and a pinch of salt. Reduce heat to low.\n**Step 3 - Simmer:** Cook for 4-5 minutes, stirring occasionally, until it reaches your desired consistency.\n**Step 4 - Slice the banana:** Peel and slice the banana.\n**Step 5 - Sweeten:** Stir in the sugar and taste.\n**Step 6 - Serve:** Pour into a bowl. Arrange banana slices on top. Garnish with honey, nuts or berries if desired."
    },
    {
        "id": 18,
        "name": "Scrambled Eggs with Bacon",
        "ingredients": ["egg", "bacon", "butter", "salt", "pepper"],
        "amounts": "egg:3 pcs,bacon:100g,butter:15g",
        "time_minutes": 15,
        "difficulty": "easy",
        "allergens": "egg,dairy",
        "calories": 420, "protein": 28, "carbohydrates": 1, "fat": 34, "fiber": 0, "vitamins": 10, "minerals": 15,
        "instructions": "**Step 1 - Fry the bacon:** Fry bacon in a dry pan over medium heat for 3-4 minutes per side until crispy. Drain on paper towels.\n**Step 2 - Prepare the eggs:** Crack eggs into a bowl. Season and whisk vigorously.\n**Step 3 - Clean the pan:** Pour off bacon fat and wipe briefly with paper towels.\n**Step 4 - Melt the butter:** Melt butter in the cleaned pan over low heat.\n**Step 5 - Scramble the eggs:** Pour in the egg mixture. Gently and constantly draw through with a spatula in slow, large movements. Remove briefly from heat if needed to keep them creamy.\n**Step 6 - Serve:** Remove from heat just before fully set. Add bacon alongside and serve immediately with toast."
    },
    {
        "id": 19,
        "name": "Green Beans with Potatoes",
        "ingredients": ["green_beans", "potato", "onion", "bacon", "salt", "pepper", "oil"],
        "amounts": "green_beans:400g,potato:400g,onion:1 pc,bacon:80g",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "",
        "calories": 290, "protein": 12, "carbohydrates": 38, "fat": 10, "fiber": 7, "vitamins": 30, "minerals": 25,
        "instructions": "**Step 1 - Prepare the vegetables:** Peel potatoes and cut into bite-sized chunks. Wash beans, trim the ends and cut in half.\n**Step 2 - Par-cook the potatoes:** Boil potatoes in salted water for 10 minutes.\n**Step 3 - Add the beans:** Add beans and cook for another 8-10 minutes until both are tender. Drain.\n**Step 4 - Fry bacon and onion:** Cut bacon into pieces and fry in a large dry pan until crispy. Add sliced onion and fry for 3 more minutes.\n**Step 5 - Combine everything:** Add drained potatoes and beans to the pan. Mix well and fry for 3-4 minutes so everything gets a little colour.\n**Step 6 - Season and serve:** Season generously with salt and pepper."
    },
    {
        "id": 20,
        "name": "Chicken Bell Pepper Pan",
        "ingredients": ["chicken_breast", "bell_pepper", "onion", "tomato", "garlic", "olive_oil", "salt", "pepper"],
        "amounts": "chicken_breast:400g,bell_pepper:2 pcs,onion:1 pc,tomato:2 pcs,garlic:2 cloves",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "",
        "calories": 330, "protein": 38, "carbohydrates": 15, "fat": 12, "fiber": 5, "vitamins": 50, "minerals": 30,
        "instructions": "**Step 1 - Prepare the chicken:** Pat dry, cut into 2 cm cubes and season with salt and pepper.\n**Step 2 - Prepare the vegetables:** Halve peppers, remove seeds and slice. Cut onion into half rings. Finely chop garlic. Roughly dice tomatoes.\n**Step 3 - Fry the chicken:** Heat olive oil in a large pan over high heat. Fry chicken for 5-6 minutes until golden on all sides. Remove.\n**Step 4 - Fry the vegetables:** In the same oil, saute onion and garlic for 2-3 minutes. Add bell pepper and cook for 4-5 minutes until soft.\n**Step 5 - Add tomatoes and chicken:** Add tomatoes and simmer for 3 minutes. Return chicken and stir everything together.\n**Step 6 - Finish and serve:** Cook together for 3-5 minutes over medium heat. Season and serve with rice, bread or pasta."
    },
    {
        "id": 21,
        "name": "Avocado Toast",
        "ingredients": ["avocado", "bread", "egg", "lemon", "salt", "pepper"],
        "amounts": "avocado:1 pc,bread:2 slices,egg:1 pc,lemon:0.5 pc",
        "time_minutes": 10,
        "difficulty": "easy",
        "allergens": "gluten,egg",
        "calories": 340, "protein": 12, "carbohydrates": 28, "fat": 22, "fiber": 8, "vitamins": 25, "minerals": 20,
        "instructions": "**Step 1 - Toast the bread:** Toast in a toaster or dry pan until golden.\n**Step 2 - Prepare the avocado:** Halve, remove stone and scoop flesh into a bowl.\n**Step 3 - Season the avocado:** Squeeze lemon juice over it. Season with salt and pepper. Mash roughly with a fork.\n**Step 4 - Fry the egg:** Heat a little oil or butter in a small pan. Fry egg sunny side up until white is set but yolk is still runny.\n**Step 5 - Top the toast:** Spread the seasoned avocado generously on the toast.\n**Step 6 - Add egg and serve:** Place the fried egg on the avocado. Sprinkle with pepper and chilli flakes if desired. Serve immediately."
    },
    {
        "id": 22,
        "name": "Yogurt with Fruits",
        "ingredients": ["yogurt", "strawberry", "banana", "oats", "honey"],
        "amounts": "yogurt:300g,strawberry:150g,banana:1 pc,oats:50g,honey:1 tbsp",
        "time_minutes": 5,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 280, "protein": 10, "carbohydrates": 48, "fat": 5, "fiber": 5, "vitamins": 35, "minerals": 25,
        "instructions": "**Step 1 - Wash the fruit:** Wash strawberries and remove the green tops.\n**Step 2 - Cut the fruit:** Halve or quarter strawberries. Peel and slice the banana.\n**Step 3 - Prepare the yogurt:** Put yogurt in a bowl and stir briefly until smooth.\n**Step 4 - Layer the fruit:** Place strawberries and banana slices on the yogurt.\n**Step 5 - Add the oats:** Scatter oats over the fruit.\n**Step 6 - Drizzle with honey and serve:** Drizzle honey over everything. Serve immediately."
    },
    {
        "id": 23,
        "name": "Mushroom Risotto",
        "ingredients": ["rice", "mushroom", "onion", "garlic", "parmesan", "vegetable_broth", "butter", "salt", "pepper"],
        "amounts": "rice:300g,mushroom:300g,onion:1 pc,parmesan:60g,vegetable_broth:800ml,butter:30g,garlic:2 cloves",
        "time_minutes": 40,
        "difficulty": "medium",
        "allergens": "dairy",
        "calories": 450, "protein": 14, "carbohydrates": 72, "fat": 12, "fiber": 3, "vitamins": 20, "minerals": 25,
        "instructions": "**Step 1 - Keep broth warm:** Heat vegetable broth in a small pot and keep warm on low heat.\n**Step 2 - Fry the mushrooms:** Melt half the butter in a large pan over high heat. Slice mushrooms and fry in a single layer for 4-5 minutes without stirring. Remove.\n**Step 3 - Soffritto:** Melt remaining butter. Finely chop onion and garlic and cook for 4-5 minutes until soft.\n**Step 4 - Toast the rice:** Add the risotto rice and stir for 2 minutes until it becomes slightly translucent.\n**Step 5 - Add broth ladle by ladle:** Add one ladle of warm broth and stir until absorbed. Repeat for 18-20 minutes until rice is soft with a slight bite.\n**Step 6 - Finish and serve:** Stir in fried mushrooms and grated parmesan. Season. Serve immediately."
    },
    {
        "id": 24,
        "name": "Greek Salad",
        "ingredients": ["tomato", "cucumber", "feta", "lettuce", "bell_pepper", "olive_oil", "vinegar", "salt", "pepper"],
        "amounts": "tomato:3 pcs,cucumber:1 pc,feta:150g,bell_pepper:1 pc,olive_oil:3 tbsp,vinegar:1 tbsp",
        "time_minutes": 10,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 220, "protein": 10, "carbohydrates": 12, "fat": 16, "fiber": 4, "vitamins": 45, "minerals": 25,
        "instructions": "**Step 1 - Cut the tomatoes:** Wash and cut into large chunks or eighths.\n**Step 2 - Cut the cucumber:** Cut into thick half moons, about 1 cm thick.\n**Step 3 - Cut the bell pepper:** Halve, remove seeds and cut into rings or rough chunks.\n**Step 4 - Combine in a bowl:** Place tomatoes, cucumber and bell pepper in a large bowl and toss lightly.\n**Step 5 - Make the dressing:** Mix olive oil, balsamic or red wine vinegar, salt and pepper. Pour over salad and toss gently.\n**Step 6 - Crumble feta and serve:** Break feta into large pieces and crumble over the salad. Serve immediately."
    },
    {
        "id": 25,
        "name": "Chicken Caesar Salad",
        "ingredients": ["chicken_breast", "lettuce", "parmesan", "lemon", "mayonnaise", "garlic", "salt", "pepper"],
        "amounts": "chicken_breast:300g,lettuce:1 head,parmesan:40g,lemon:1 pc,mayonnaise:3 tbsp,garlic:1 clove",
        "time_minutes": 20,
        "difficulty": "easy",
        "allergens": "dairy,egg",
        "calories": 380, "protein": 40, "carbohydrates": 8, "fat": 20, "fiber": 3, "vitamins": 35, "minerals": 25,
        "instructions": "**Step 1 - Season the chicken:** Pat dry. Rub with salt, pepper and a squeeze of lemon juice.\n**Step 2 - Fry the chicken:** Cook in a pan over medium-high heat for 6-7 minutes per side until golden and cooked through. Rest for 5 minutes.\n**Step 3 - Make the dressing:** Very finely chop or press garlic. Combine with mayonnaise, half the lemon juice, salt and pepper.\n**Step 4 - Prepare the lettuce:** Wash, spin dry and tear into bite-sized pieces.\n**Step 5 - Slice the chicken:** Slice or strip the rested chicken.\n**Step 6 - Assemble and serve:** Toss lettuce with dressing. Plate and top with chicken and shaved parmesan. Serve immediately."
    },
    {
        "id": 26,
        "name": "Salmon with Spinach and Cream",
        "ingredients": ["salmon", "spinach", "cream", "garlic", "lemon", "salt", "pepper", "olive_oil"],
        "amounts": "salmon:400g,spinach:200g,cream:150ml,garlic:2 cloves,lemon:1 pc",
        "time_minutes": 25,
        "difficulty": "medium",
        "allergens": "fish,dairy",
        "calories": 490, "protein": 45, "carbohydrates": 6, "fat": 32, "fiber": 3, "vitamins": 50, "minerals": 40,
        "instructions": "**Step 1 - Prepare the salmon:** Pat dry and season with salt and pepper.\n**Step 2 - Cook the salmon:** Heat olive oil in a pan over medium-high. Place salmon skin-side down and cook for 4-5 minutes. Flip and cook for 3 more minutes until slightly pink inside. Remove and keep warm.\n**Step 3 - Saute the garlic:** In the same pan, cook finely chopped garlic for 1 minute.\n**Step 4 - Add spinach:** Add spinach and stir for 2 minutes until fully wilted.\n**Step 5 - Make the cream sauce:** Pour in cream and squeeze in lemon juice. Reduce for 2-3 minutes until slightly thickened. Season.\n**Step 6 - Return salmon and serve:** Return salmon to the sauce and warm for 2 minutes. Plate spinach sauce first, then salmon on top. Serve with lemon wedges."
    },
    {
        "id": 27,
        "name": "Eggs Benedict",
        "ingredients": ["egg", "ham", "bread", "butter", "lemon", "salt", "pepper"],
        "amounts": "egg:4 pcs,ham:100g,bread:2 slices,butter:50g,lemon:0.5 pc",
        "time_minutes": 20,
        "difficulty": "medium",
        "allergens": "egg,dairy,gluten",
        "calories": 450, "protein": 24, "carbohydrates": 22, "fat": 30, "fiber": 1, "vitamins": 15, "minerals": 20,
        "instructions": "**Step 1 - Toast bread and prepare ham:** Toast bread until golden. Briefly warm ham in a dry pan.\n**Step 2 - Prepare poaching water:** Fill a shallow pot with water, add a splash of vinegar and bring to a simmer.\n**Step 3 - Prepare the eggs:** Crack each egg into a small cup.\n**Step 4 - Poach the eggs:** Create a swirl in the water. Slide egg in from the cup. Poach for 3 minutes until white is set but yolk is runny. Drain on paper towels.\n**Step 5 - Hollandaise (simple):** Melt butter. Whisk egg yolks with lemon juice over a bain-marie until fluffy. Drizzle in butter while whisking to create a creamy sauce.\n**Step 6 - Layer and serve:** Place toast, add ham, place poached egg on top and spoon hollandaise over. Serve with pepper."
    },
    {
        "id": 28,
        "name": "Cauliflower Curry",
        "ingredients": ["cauliflower", "chickpeas", "tomato", "onion", "garlic", "coconut_milk", "spinach", "salt", "pepper", "oil"],
        "amounts": "cauliflower:1 head,chickpeas:400g,tomato:2 pcs,onion:1 pc,coconut_milk:400ml,spinach:100g,garlic:2 cloves",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "",
        "calories": 380, "protein": 14, "carbohydrates": 48, "fat": 16, "fiber": 12, "vitamins": 55, "minerals": 35,
        "instructions": "**Step 1 - Prepare the cauliflower:** Wash and break into medium florets. Peel and dice the stalk.\n**Step 2 - Fry onion and garlic:** Heat oil in a large pot. Finely chop onion and fry for 5 minutes. Add garlic and cook for 1 minute.\n**Step 3 - Fry the cauliflower:** Add florets and fry for 3-4 minutes.\n**Step 4 - Add tomatoes:** Dice tomatoes and add. Cook for 3 minutes.\n**Step 5 - Add chickpeas and coconut milk:** Pour in drained chickpeas and coconut milk. Bring to a boil and simmer for 20 minutes until cauliflower is tender.\n**Step 6 - Stir in spinach and serve:** Add spinach and simmer for 2-3 minutes until wilted. Season and serve with rice or naan."
    },
    {
        "id": 29,
        "name": "Tzatziki with Flatbread",
        "ingredients": ["yogurt", "cucumber", "garlic", "lemon", "bread", "olive_oil", "salt", "pepper"],
        "amounts": "yogurt:400g,cucumber:1 pc,garlic:2 cloves,lemon:0.5 pc,bread:4 pcs,olive_oil:2 tbsp",
        "time_minutes": 15,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 250, "protein": 10, "carbohydrates": 30, "fat": 10, "fiber": 2, "vitamins": 15, "minerals": 20,
        "instructions": "**Step 1 - Grate the cucumber:** Wash and grate coarsely. Place in a kitchen towel.\n**Step 2 - Squeeze out the cucumber:** Twist tightly and squeeze out as much liquid as possible. This step is critical.\n**Step 3 - Prepare the garlic:** Peel and chop very finely or press through a garlic press.\n**Step 4 - Mix the tzatziki:** Place yogurt in a bowl. Add squeezed cucumber, garlic, lemon juice, olive oil, salt and pepper. Stir thoroughly.\n**Step 5 - Refrigerate:** Refrigerate for at least 10 minutes to let the flavours come together.\n**Step 6 - Serve:** Plate the tzatziki, make a well in the centre and drizzle in olive oil. Serve with flatbread."
    },
    {
        "id": 30,
        "name": "Ground Beef Pan with Rice",
        "ingredients": ["ground_beef", "rice", "bell_pepper", "onion", "tomato_sauce", "garlic", "salt", "pepper", "oil"],
        "amounts": "ground_beef:300g,rice:250g,bell_pepper:2 pcs,onion:1 pc,tomato_sauce:300g,garlic:2 cloves",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "",
        "calories": 490, "protein": 32, "carbohydrates": 55, "fat": 14, "fiber": 4, "vitamins": 30, "minerals": 25,
        "instructions": "**Step 1 - Cook the rice:** Cook rice and set aside.\n**Step 2 - Cut the vegetables:** Finely chop onion and garlic. Deseed bell pepper and cut into small cubes.\n**Step 3 - Fry onion and garlic:** Heat oil in a large pan. Cook for 3-4 minutes until soft.\n**Step 4 - Brown the beef:** Add ground beef. Break into pieces and fry over high heat for 6-8 minutes until browned. Drain excess fat.\n**Step 5 - Add peppers and sauce:** Add bell pepper and fry for 3 minutes. Pour in tomato sauce and simmer for 10 minutes.\n**Step 6 - Season and serve:** Season generously. Spoon over cooked rice and serve."
    },
    {
        "id": 31,
        "name": "Leek Soup",
        "ingredients": ["leek", "potato", "cream", "vegetable_broth", "butter", "salt", "pepper"],
        "amounts": "leek:3 stalks,potato:300g,cream:100ml,vegetable_broth:600ml,butter:20g",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 210, "protein": 4, "carbohydrates": 28, "fat": 10, "fiber": 4, "vitamins": 30, "minerals": 20,
        "instructions": "**Step 1 - Wash and cut the leek:** Cut into rings using only the white and light green parts. Rinse again as it often has sand between the layers.\n**Step 2 - Peel and cube the potatoes:** Cut into even cubes.\n**Step 3 - Saute the leek:** Melt butter in a large pot. Add leek and cook for 4-5 minutes until soft.\n**Step 4 - Add potatoes and broth:** Add potatoes and pour in broth. Bring to a boil.\n**Step 5 - Simmer:** Reduce heat and simmer for 20 minutes until potatoes are completely soft.\n**Step 6 - Blend, add cream and serve:** Blend smooth with an immersion blender. Stir in cream and heat briefly. Season and serve."
    },
    {
        "id": 32,
        "name": "Shrimp Pasta",
        "ingredients": ["shrimp", "pasta", "garlic", "lemon", "spinach", "olive_oil", "salt", "pepper"],
        "amounts": "shrimp:300g,pasta:400g,garlic:3 cloves,lemon:1 pc,spinach:100g",
        "time_minutes": 25,
        "difficulty": "medium",
        "allergens": "fish,gluten",
        "calories": 460, "protein": 32, "carbohydrates": 62, "fat": 10, "fiber": 4, "vitamins": 30, "minerals": 35,
        "instructions": "**Step 1 - Cook the pasta:** Cook pasta al dente. Reserve some pasta water before draining.\n**Step 2 - Prepare the shrimp:** Peel and devein if needed. Season with salt and pepper.\n**Step 3 - Fry the garlic:** Heat olive oil. Slice garlic thinly and cook for 1-2 minutes until golden.\n**Step 4 - Cook the shrimp:** Add shrimp and fry 2 minutes per side until pink and firm. Remove immediately.\n**Step 5 - Add spinach and lemon:** Add spinach and let wilt for 1-2 minutes. Squeeze lemon juice over.\n**Step 6 - Stir in pasta and serve:** Add drained pasta to the pan. Toss together. Add pasta water if too dry. Serve immediately."
    },
    {
        "id": 33,
        "name": "Cheese Spaetzle",
        "ingredients": ["egg", "flour", "cheese", "onion", "butter", "salt", "pepper"],
        "amounts": "egg:3 pcs,flour:300g,cheese:150g,onion:2 pcs,butter:30g",
        "time_minutes": 40,
        "difficulty": "medium",
        "allergens": "egg,gluten,dairy",
        "calories": 580, "protein": 24, "carbohydrates": 68, "fat": 24, "fiber": 2, "vitamins": 15, "minerals": 25,
        "instructions": "**Step 1 - Make the dough:** Sift flour into a large bowl. Add eggs, salt and 150 ml water. Stir vigorously until batter forms bubbles and is thick. It should drip slowly from the spoon.\n**Step 2 - Boil salted water:** Bring a large pot of salted water to a boil.\n**Step 3 - Scrape the spaetzle:** Place batter on a wet board and scrape thin strips into the boiling water with a scraper or knife. Cook until they float, about 2-3 minutes, then remove.\n**Step 4 - Caramelise the onions:** Melt butter in a large pan. Slice onions into rings and cook slowly for 15-20 minutes until golden and sweet.\n**Step 5 - Grate the cheese:** Finely grate the cheese (Emmental or Gruyere).\n**Step 6 - Layer and gratinate:** Layer spaetzle with cheese in an oven-safe dish. Bake at 200C for 10 minutes until cheese is golden. Top with caramelised onions and serve."
    },
    {
        "id": 34,
        "name": "Ricotta Gnocchi",
        "ingredients": ["ricotta", "flour", "egg", "parmesan", "tomato_sauce", "salt", "pepper"],
        "amounts": "ricotta:500g,flour:150g,egg:1 pc,parmesan:50g,tomato_sauce:400g",
        "time_minutes": 35,
        "difficulty": "medium",
        "allergens": "dairy,egg,gluten",
        "calories": 420, "protein": 20, "carbohydrates": 55, "fat": 14, "fiber": 3, "vitamins": 15, "minerals": 25,
        "instructions": "**Step 1 - Drain the ricotta:** Squeeze out excess moisture through a kitchen towel.\n**Step 2 - Mix the dough:** Combine ricotta, flour, egg, parmesan, salt and pepper into a soft dough. Do not overwork.\n**Step 3 - Prepare salted water:** Bring a large pot of salted water to a boil.\n**Step 4 - Shape the gnocchi:** Roll dough into logs about 2 cm thick. Cut into 2 cm pieces.\n**Step 5 - Cook the gnocchi:** Drop into boiling water in batches. Cook until they float, about 2-3 minutes. Remove with a slotted spoon.\n**Step 6 - Warm the sauce and serve:** Heat tomato sauce. Add gnocchi and toss briefly. Plate, add parmesan on top and serve."
    },
    {
        "id": 35,
        "name": "Chicken Shawarma Bowl",
        "ingredients": ["chicken_breast", "yogurt", "lemon", "garlic", "rice", "cucumber", "tomato", "olive_oil", "salt", "pepper"],
        "amounts": "chicken_breast:400g,yogurt:200g,rice:250g,cucumber:1 pc,tomato:2 pcs,lemon:1 pc,garlic:2 cloves",
        "time_minutes": 35,
        "difficulty": "medium",
        "allergens": "dairy",
        "calories": 480, "protein": 42, "carbohydrates": 50, "fat": 12, "fiber": 4, "vitamins": 35, "minerals": 30,
        "instructions": "**Step 1 - Marinate the chicken:** Cut into thin strips. Mix with 100g yogurt, lemon juice, pressed garlic, salt and pepper. Marinate for at least 15 minutes.\n**Step 2 - Cook the rice:** Cook rice and keep warm.\n**Step 3 - Cut the toppings:** Dice cucumber and tomatoes.\n**Step 4 - Fry the chicken:** Heat olive oil in a pan over high heat. Remove chicken from marinade and fry for 4-5 minutes per side until golden and cooked through.\n**Step 5 - Make the yogurt dip:** Stir remaining yogurt with lemon juice, salt and pepper.\n**Step 6 - Assemble the bowl:** Place rice in bowls. Arrange chicken, cucumber and tomatoes alongside. Spoon yogurt dip over. Serve with pepper and lemon."
    },
    {
        "id": 36,
        "name": "Asparagus with Egg and Butter",
        "ingredients": ["asparagus", "egg", "butter", "lemon", "salt", "pepper"],
        "amounts": "asparagus:500g,egg:2 pcs,butter:40g,lemon:0.5 pc",
        "time_minutes": 20,
        "difficulty": "easy",
        "allergens": "egg,dairy",
        "calories": 240, "protein": 14, "carbohydrates": 8, "fat": 18, "fiber": 4, "vitamins": 45, "minerals": 30,
        "instructions": "**Step 1 - Peel the asparagus:** Peel the lower third. Snap or cut off the woody end.\n**Step 2 - Boil water:** Bring a wide pot of salted water to a boil. Add a knob of butter and a pinch of sugar.\n**Step 3 - Cook the asparagus:** White: 10-12 minutes. Green: 6-8 minutes. It is done when a knife slides through without resistance.\n**Step 4 - Hard boil the eggs:** Boil eggs for 9-10 minutes. Cool under cold water, peel and cut into small cubes.\n**Step 5 - Brown the butter:** Melt butter in a small pan and let brown lightly until it smells nutty. Remove from heat immediately.\n**Step 6 - Plate and serve:** Place asparagus on plates. Scatter egg cubes over it. Pour browned butter over. Finish with lemon juice and pepper."
    },
    {
        "id": 37,
        "name": "Pumpkin Soup",
        "ingredients": ["pumpkin", "onion", "garlic", "cream", "vegetable_broth", "ginger", "salt", "pepper", "oil"],
        "amounts": "pumpkin:800g,onion:1 pc,cream:100ml,vegetable_broth:500ml,ginger:20g,garlic:1 clove",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 180, "protein": 3, "carbohydrates": 28, "fat": 7, "fiber": 4, "vitamins": 50, "minerals": 20,
        "instructions": "**Step 1 - Prepare the pumpkin:** Halve and scoop out seeds. Peel and cut into even cubes. Hokkaido pumpkin does not need peeling.\n**Step 2 - Prepare aromatics:** Peel and finely chop onion and garlic. Peel and finely grate ginger.\n**Step 3 - Saute:** Heat oil in a large pot. Add onion, garlic and ginger and cook for 4-5 minutes until soft.\n**Step 4 - Cook the pumpkin:** Add pumpkin cubes. Pour in vegetable broth. Bring to a boil and cook for 20 minutes until completely soft.\n**Step 5 - Blend:** Blend completely smooth and velvety with an immersion blender.\n**Step 6 - Add cream and serve:** Stir in cream and heat briefly. Season. Serve garnished with a swirl of cream and pumpkin seeds."
    },
    {
        "id": 38,
        "name": "Tofu Vegetable Pan",
        "ingredients": ["tofu", "broccoli", "bell_pepper", "carrot", "soy_sauce", "ginger", "garlic", "oil"],
        "amounts": "tofu:400g,broccoli:300g,bell_pepper:1 pc,carrot:2 pcs,soy_sauce:3 tbsp,ginger:15g,garlic:2 cloves",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "soy",
        "calories": 280, "protein": 20, "carbohydrates": 18, "fat": 14, "fiber": 7, "vitamins": 60, "minerals": 35,
        "instructions": "**Step 1 - Prepare the tofu:** Press between kitchen towels for 10 minutes. Cut into 2 cm cubes.\n**Step 2 - Prepare vegetables:** Divide broccoli into florets. Deseed and slice bell pepper. Peel and slice carrots diagonally. Finely chop garlic and ginger.\n**Step 3 - Fry tofu until crispy:** Heat oil in a wok over high heat. Fry tofu cubes for 4-5 minutes per side until golden and crispy. Remove.\n**Step 4 - Fry the harder vegetables:** Stir-fry carrots and broccoli for 3-4 minutes.\n**Step 5 - Add remaining vegetables and aromatics:** Add bell pepper, garlic and ginger. Stir-fry for another 2-3 minutes.\n**Step 6 - Return tofu and season:** Return crispy tofu to the wok. Pour soy sauce over and toss at high heat for 1 minute. Serve with rice."
    },
    {
        "id": 39,
        "name": "Spinach Feta Quiche",
        "ingredients": ["spinach", "feta", "egg", "cream", "flour", "butter", "onion", "salt", "pepper"],
        "amounts": "spinach:300g,feta:200g,egg:4 pcs,cream:200ml,flour:200g,butter:100g,onion:1 pc",
        "time_minutes": 55,
        "difficulty": "medium",
        "allergens": "dairy,egg,gluten",
        "calories": 480, "protein": 18, "carbohydrates": 35, "fat": 32, "fiber": 3, "vitamins": 40, "minerals": 30,
        "instructions": "**Step 1 - Preheat oven:** Preheat oven to 180C.\n**Step 2 - Make the shortcrust pastry:** Combine flour, cold butter pieces and a pinch of salt. Rub between fingertips until like coarse breadcrumbs. Add 3-4 tbsp cold water and press into a dough. Refrigerate for 15 minutes.\n**Step 3 - Prepare the filling:** Saute finely chopped onion in butter. Wilt spinach in a pan. Squeeze to remove excess water.\n**Step 4 - Roll out and line:** Roll out dough and lay into a tart tin. Press up the edges. Prick the base with a fork.\n**Step 5 - Fill:** Spread spinach and onion over the base. Break feta into pieces and scatter over. Whisk eggs with cream, salt and pepper and pour over.\n**Step 6 - Bake and serve:** Bake for 30-35 minutes until golden and set. Cool for 5 minutes before slicing."
    },
    {
        "id": 40,
        "name": "Berry Smoothie Bowl",
        "ingredients": ["raspberry", "blueberry", "banana", "yogurt", "oats", "honey"],
        "amounts": "raspberry:100g,blueberry:100g,banana:2 pcs,yogurt:200g,oats:50g,honey:1 tbsp",
        "time_minutes": 5,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 320, "protein": 8, "carbohydrates": 60, "fat": 5, "fiber": 8, "vitamins": 40, "minerals": 20,
        "instructions": "**Step 1 - Prepare the fruit:** Set aside half the raspberries and blueberries for topping. Add the rest to a blender along with bananas and yogurt.\n**Step 2 - Blend:** Blend on highest speed for 1-2 minutes until smooth and thick.\n**Step 3 - Pour into bowls:** Pour into wide, shallow bowls.\n**Step 4 - Arrange toppings:** Arrange reserved berries on top.\n**Step 5 - Add oats:** Scatter oats over the berries.\n**Step 6 - Drizzle with honey and serve:** Drizzle honey over the bowl. Serve and eat immediately."
    },
    {
        "id": 41,
        "name": "Chicken Wrap",
        "ingredients": ["chicken_breast", "lettuce", "tomato", "cucumber", "yogurt", "lemon", "bread", "salt", "pepper"],
        "amounts": "chicken_breast:300g,lettuce:4 leaves,tomato:1 pc,cucumber:0.5 pc,yogurt:100g,bread:2 pcs,lemon:0.5 pc",
        "time_minutes": 20,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 380, "protein": 38, "carbohydrates": 30, "fat": 10, "fiber": 3, "vitamins": 30, "minerals": 25,
        "instructions": "**Step 1 - Season the chicken:** Pat dry and cut into thin strips. Season with salt, pepper and lemon juice.\n**Step 2 - Fry the chicken:** Cook strips for 3-4 minutes per side until golden and cooked through. Set aside.\n**Step 3 - Make the yogurt sauce:** Mix yogurt, lemon juice, salt and pepper.\n**Step 4 - Cut the vegetables:** Slice tomatoes. Cut cucumber into thin strips. Wash and dry lettuce.\n**Step 5 - Warm the tortillas:** Heat in a dry pan or microwave so they are pliable.\n**Step 6 - Fill and roll:** Spread yogurt sauce. Layer lettuce, tomatoes and cucumber. Add chicken. Fold and roll. Serve immediately."
    },
    {
        "id": 42,
        "name": "Eggplant Parmesan",
        "ingredients": ["eggplant", "tomato_sauce", "mozzarella", "parmesan", "egg", "flour", "salt", "pepper", "olive_oil"],
        "amounts": "eggplant:2 pcs,tomato_sauce:400g,mozzarella:200g,parmesan:60g,egg:2 pcs,flour:100g",
        "time_minutes": 50,
        "difficulty": "medium",
        "allergens": "dairy,egg,gluten",
        "calories": 380, "protein": 20, "carbohydrates": 28, "fat": 22, "fiber": 6, "vitamins": 30, "minerals": 30,
        "instructions": "**Step 1 - Salt the eggplant:** Cut into 1 cm thick slices. Salt and leave for 15 minutes. Pat dry.\n**Step 2 - Preheat oven:** Preheat oven to 200C.\n**Step 3 - Bread the slices:** Coat each slice in flour, then drag through whisked eggs.\n**Step 4 - Fry the eggplant:** Fry in olive oil in batches until golden, about 3 minutes per side. Drain on paper towels.\n**Step 5 - Layer:** Spread a layer of tomato sauce in a baking dish. Add eggplant, sliced mozzarella and parmesan. Repeat, ending with cheese.\n**Step 6 - Bake and serve:** Bake for 25 minutes until cheese is golden and sauce is bubbling. Cool for 5 minutes before serving."
    },
    {
        "id": 43,
        "name": "Pasta Carbonara",
        "ingredients": ["pasta", "bacon", "egg", "parmesan", "garlic", "salt", "pepper"],
        "amounts": "pasta:400g,bacon:150g,egg:3 pcs,parmesan:80g,garlic:1 clove",
        "time_minutes": 25,
        "difficulty": "medium",
        "allergens": "gluten,egg,dairy",
        "calories": 580, "protein": 28, "carbohydrates": 62, "fat": 24, "fiber": 2, "vitamins": 10, "minerals": 25,
        "instructions": "**Step 1 - Cook the pasta:** Cook pasta al dente. Reserve at least 1 cup of pasta water.\n**Step 2 - Fry the bacon:** Cut into cubes and fry in a large pan without oil until crispy. Briefly fry garlic. Remove pan from heat.\n**Step 3 - Make the egg-cheese mixture:** Whisk eggs and parmesan in a bowl. Season generously with black pepper. This is the sauce - no cream!\n**Step 4 - Drain the pasta:** Keep reserved pasta water. Add hot pasta immediately to the pan with bacon.\n**Step 5 - Incorporate the sauce (critical):** Remove pan from heat. Pour egg-cheese mixture over pasta and stir immediately and quickly. Add hot pasta water ladle by ladle until you have a creamy sauce.\n**Step 6 - Serve immediately:** Plate on warmed plates, grate more parmesan on top and serve with plenty of black pepper."
    },
    {
        "id": 44,
        "name": "Chicken Coconut Curry",
        "ingredients": ["chicken_breast", "coconut_milk", "tomato", "onion", "garlic", "ginger", "spinach", "rice", "oil", "salt"],
        "amounts": "chicken_breast:400g,coconut_milk:400ml,tomato:2 pcs,onion:1 pc,rice:250g,ginger:15g,garlic:2 cloves,spinach:100g",
        "time_minutes": 35,
        "difficulty": "medium",
        "allergens": "",
        "calories": 520, "protein": 38, "carbohydrates": 52, "fat": 18, "fiber": 4, "vitamins": 35, "minerals": 30,
        "instructions": "**Step 1 - Cook the rice:** Cook rice and keep warm.\n**Step 2 - Prepare the chicken:** Pat dry and cut into 2 cm cubes. Season with salt.\n**Step 3 - Fry the aromatics:** Heat oil. Finely chop onion and fry for 5 minutes. Finely chop garlic and ginger and cook for 1 minute.\n**Step 4 - Brown the chicken:** Add chicken cubes and brown on all sides for 4-5 minutes.\n**Step 5 - Add tomatoes and coconut milk:** Dice tomatoes and add. Pour in coconut milk. Simmer over medium heat for 15 minutes until chicken is cooked and sauce has thickened.\n**Step 6 - Stir in spinach and serve:** Add spinach and let wilt for 2 minutes. Season. Spoon over rice and serve."
    },
    {
        "id": 45,
        "name": "Peach Yogurt",
        "ingredients": ["peach", "yogurt", "honey", "oats"],
        "amounts": "peach:2 pcs,yogurt:300g,honey:2 tbsp,oats:50g",
        "time_minutes": 5,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 260, "protein": 8, "carbohydrates": 46, "fat": 4, "fiber": 4, "vitamins": 20, "minerals": 15,
        "instructions": "**Step 1 - Wash the peaches:** Wash under cold water and pat dry.\n**Step 2 - Slice the peaches:** Halve, remove stone and slice.\n**Step 3 - Prepare the yogurt:** Put yogurt in a bowl and stir briefly until smooth.\n**Step 4 - Layer:** Spoon yogurt onto a plate or bowl. Lay peach slices on top.\n**Step 5 - Add oats:** Scatter oats over the peach.\n**Step 6 - Drizzle with honey:** Drizzle honey evenly over everything. Serve immediately."
    },
    {
        "id": 46,
        "name": "Carrot Ginger Soup",
        "ingredients": ["carrot", "ginger", "onion", "garlic", "coconut_milk", "vegetable_broth", "lemon", "oil", "salt", "pepper"],
        "amounts": "carrot:600g,ginger:30g,onion:1 pc,coconut_milk:200ml,vegetable_broth:500ml,lemon:0.5 pc,garlic:1 clove",
        "time_minutes": 30,
        "difficulty": "easy",
        "allergens": "",
        "calories": 200, "protein": 3, "carbohydrates": 30, "fat": 8, "fiber": 6, "vitamins": 50, "minerals": 20,
        "instructions": "**Step 1 - Prepare the vegetables:** Peel and slice carrots. Peel and finely chop onion and garlic. Peel and finely grate ginger.\n**Step 2 - Saute:** Heat oil. Add onion, garlic and ginger and cook for 4-5 minutes until soft.\n**Step 3 - Add the carrots:** Add carrot slices and cook for 2 minutes.\n**Step 4 - Add broth and cook:** Pour in vegetable broth. Bring to a boil and cook for 20 minutes until carrots are completely soft.\n**Step 5 - Blend:** Blend completely smooth with an immersion blender.\n**Step 6 - Stir in coconut milk and lemon:** Stir in coconut milk and lemon juice. Warm briefly. Season and serve."
    },
    {
        "id": 47,
        "name": "Caprese Salad",
        "ingredients": ["tomato", "mozzarella", "olive_oil", "vinegar", "salt", "pepper"],
        "amounts": "tomato:4 pcs,mozzarella:250g,olive_oil:3 tbsp,vinegar:1 tbsp",
        "time_minutes": 5,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 280, "protein": 16, "carbohydrates": 8, "fat": 20, "fiber": 2, "vitamins": 25, "minerals": 30,
        "instructions": "**Step 1 - Slice the tomatoes:** Wash and cut into even slices about 1 cm thick.\n**Step 2 - Slice the mozzarella:** Remove from liquid and cut into slices of the same thickness.\n**Step 3 - Arrange:** Alternate tomato and mozzarella slices on a flat plate, overlapping like roof tiles.\n**Step 4 - Season:** Season with salt and freshly ground pepper.\n**Step 5 - Add dressing:** Drizzle olive oil and then balsamic vinegar in a thin stream.\n**Step 6 - Serve:** Serve immediately as a starter or side."
    },
    {
        "id": 48,
        "name": "Shakshuka",
        "ingredients": ["egg", "tomato_sauce", "bell_pepper", "onion", "garlic", "olive_oil", "salt", "pepper"],
        "amounts": "egg:4 pcs,tomato_sauce:400g,bell_pepper:1 pc,onion:1 pc,garlic:2 cloves",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "egg",
        "calories": 260, "protein": 16, "carbohydrates": 22, "fat": 12, "fiber": 5, "vitamins": 40, "minerals": 25,
        "instructions": "**Step 1 - Prepare vegetables:** Finely chop onion and garlic. Deseed and finely dice bell pepper.\n**Step 2 - Fry the vegetables:** Heat olive oil in a large deep pan. Cook onion for 4-5 minutes. Add garlic and bell pepper and fry for another 3-4 minutes.\n**Step 3 - Add tomato sauce:** Pour in tomato sauce. Season. Simmer for 8-10 minutes until sauce thickens.\n**Step 4 - Make wells:** Press 4 wells into the sauce with a spoon.\n**Step 5 - Add the eggs:** Crack one egg into each well. Cover the pan with a lid.\n**Step 6 - Cook and serve:** Cook over medium-low heat for 6-8 minutes until whites are set but yolks still runny. Serve from the pan with bread."
    },
    {
        "id": 49,
        "name": "Banana Bread",
        "ingredients": ["banana", "flour", "egg", "sugar", "butter", "baking_powder", "salt"],
        "amounts": "banana:3 pcs,flour:200g,egg:2 pcs,sugar:80g,butter:80g,baking_powder:1 tsp",
        "time_minutes": 65,
        "difficulty": "medium",
        "allergens": "gluten,egg,dairy",
        "calories": 380, "protein": 8, "carbohydrates": 62, "fat": 12, "fiber": 3, "vitamins": 10, "minerals": 15,
        "instructions": "**Step 1 - Preheat oven and prepare tin:** Preheat to 175C. Grease and flour a loaf tin.\n**Step 2 - Mash the bananas:** Peel and mash thoroughly with a fork until almost smooth.\n**Step 3 - Mix wet ingredients:** Melt butter and let cool slightly. Add butter, sugar and eggs to bananas. Mix well.\n**Step 4 - Stir in dry ingredients:** Sift flour, baking powder and a pinch of salt over the banana mixture. Stir gently until just combined - lumps are fine.\n**Step 5 - Bake:** Pour batter into the prepared tin. Bake for 55-60 minutes. Test with a skewer after 50 minutes.\n**Step 6 - Cool and serve:** Cool in the tin for 10 minutes, then turn out onto a rack. Cool completely before slicing."
    },
    {
        "id": 50,
        "name": "Stuffed Bell Peppers",
        "ingredients": ["bell_pepper", "ground_beef", "rice", "tomato_sauce", "onion", "garlic", "cheese", "salt", "pepper", "oil"],
        "amounts": "bell_pepper:4 pcs,ground_beef:300g,rice:150g,tomato_sauce:300g,cheese:80g,onion:1 pc,garlic:2 cloves",
        "time_minutes": 50,
        "difficulty": "medium",
        "allergens": "dairy",
        "calories": 420, "protein": 28, "carbohydrates": 38, "fat": 16, "fiber": 5, "vitamins": 40, "minerals": 25,
        "instructions": "**Step 1 - Preheat oven and cook rice:** Preheat to 180C. Cook rice.\n**Step 2 - Prepare the peppers:** Cut off tops and set aside. Scoop out seeds and ribs.\n**Step 3 - Make the filling:** Saute onion and garlic. Add ground beef and fry until crumbly. Stir in cooked rice and half the tomato sauce. Season.\n**Step 4 - Fill the peppers:** Fill hollowed peppers with the mixture. Do not pack too tightly.\n**Step 5 - Bake:** Pour remaining tomato sauce into a baking dish. Stand peppers in it. Scatter cheese over filling. Place lids back on. Bake for 25-30 minutes.\n**Step 6 - Serve:** Peppers are ready when soft outside and cheese has melted. Serve with the sauce from the dish."
    },
    {
        "id": 51,
        "name": "Cabbage Soup",
        "ingredients": ["white_cabbage", "carrot", "potato", "onion", "vegetable_broth", "tomato", "salt", "pepper", "oil"],
        "amounts": "white_cabbage:0.5 head,carrot:2 pcs,potato:2 pcs,onion:1 pc,vegetable_broth:800ml,tomato:2 pcs",
        "time_minutes": 35,
        "difficulty": "easy",
        "allergens": "",
        "calories": 160, "protein": 5, "carbohydrates": 28, "fat": 3, "fiber": 6, "vitamins": 40, "minerals": 25,
        "instructions": "**Step 1 - Cut the vegetables:** Quarter cabbage, remove core and cut into fine strips. Peel and slice carrots. Peel and dice potatoes. Finely chop onion. Cut tomatoes into pieces.\n**Step 2 - Saute the onion:** Heat oil. Cook onion for 3-4 minutes.\n**Step 3 - Add harder vegetables:** Add carrots and potatoes and fry for 2 minutes.\n**Step 4 - Add cabbage and broth:** Add cabbage. Pour in vegetable broth and bring to a boil.\n**Step 5 - Simmer:** Reduce heat and simmer for 20 minutes until cabbage is soft.\n**Step 6 - Add tomatoes and season:** Add tomatoes and simmer for 5 more minutes. Season generously and serve."
    },
    {
        "id": 52,
        "name": "French Toast",
        "ingredients": ["bread", "egg", "milk", "butter", "sugar", "banana"],
        "amounts": "bread:4 slices,egg:2 pcs,milk:100ml,butter:20g,sugar:1 tbsp,banana:1 pc",
        "time_minutes": 15,
        "difficulty": "easy",
        "allergens": "gluten,egg,dairy",
        "calories": 350, "protein": 14, "carbohydrates": 48, "fat": 12, "fiber": 3, "vitamins": 12, "minerals": 18,
        "instructions": "**Step 1 - Prepare the egg mixture:** Whisk together eggs, milk and sugar.\n**Step 2 - Heat the pan:** Melt butter in a pan over medium heat until it foams.\n**Step 3 - Soak the bread:** Place each slice in the egg mixture for 15-20 seconds per side. The bread should be saturated but not falling apart.\n**Step 4 - Fry the bread:** Place soaked slices in hot butter. Fry for 2-3 minutes until the underside is golden.\n**Step 5 - Flip:** Flip and fry for 2 more minutes until golden.\n**Step 6 - Serve:** Slice banana and arrange alongside. Drizzle with honey or syrup if desired."
    },
    {
        "id": 53,
        "name": "Creamy Mushrooms on Toast",
        "ingredients": ["mushroom", "cream", "garlic", "bread", "butter", "salt", "pepper"],
        "amounts": "mushroom:400g,cream:150ml,garlic:2 cloves,bread:4 slices,butter:30g",
        "time_minutes": 15,
        "difficulty": "easy",
        "allergens": "dairy,gluten",
        "calories": 310, "protein": 8, "carbohydrates": 28, "fat": 19, "fiber": 3, "vitamins": 15, "minerals": 20,
        "instructions": "**Step 1 - Prepare the mushrooms:** Wipe with a damp paper towel and slice evenly. Finely chop garlic.\n**Step 2 - Fry the mushrooms:** Melt butter in a large pan over high heat. Place mushrooms in a single layer. Fry for 4-5 minutes without stirring until golden. Only then flip.\n**Step 3 - Add garlic:** Add garlic and cook for 1 minute. Season.\n**Step 4 - Pour in cream and reduce:** Pour cream over mushrooms. Reduce for 2-3 minutes until slightly thickened.\n**Step 5 - Toast the bread:** Toast until golden.\n**Step 6 - Serve on toast:** Spoon creamy mushrooms onto toast slices and serve immediately."
    },
    {
        "id": 54,
        "name": "Salmon Pasta with Cream Sauce",
        "ingredients": ["salmon", "pasta", "cream", "garlic", "lemon", "spinach", "parmesan", "salt", "pepper", "olive_oil"],
        "amounts": "salmon:300g,pasta:400g,cream:200ml,garlic:2 cloves,spinach:100g,parmesan:40g,lemon:0.5 pc",
        "time_minutes": 30,
        "difficulty": "medium",
        "allergens": "fish,dairy,gluten",
        "calories": 560, "protein": 38, "carbohydrates": 58, "fat": 20, "fiber": 4, "vitamins": 35, "minerals": 40,
        "instructions": "**Step 1 - Cook the pasta:** Cook al dente. Reserve pasta water.\n**Step 2 - Prepare and fry the salmon:** Pat dry and cut into cubes. Fry for 2 minutes. Remove.\n**Step 3 - Saute garlic:** Cook finely chopped garlic for 1 minute.\n**Step 4 - Make the cream sauce:** Pour in cream, bring to a boil and reduce for 3 minutes. Squeeze in lemon juice.\n**Step 5 - Add spinach and salmon:** Stir in spinach and let wilt. Return salmon and gently toss.\n**Step 6 - Stir in pasta and serve:** Add drained pasta. Sprinkle with parmesan. Serve immediately."
    },
    {
        "id": 55,
        "name": "Zucchini Soup",
        "ingredients": ["zucchini", "onion", "garlic", "cream", "vegetable_broth", "salt", "pepper", "olive_oil"],
        "amounts": "zucchini:600g,onion:1 pc,cream:100ml,vegetable_broth:500ml,garlic:1 clove",
        "time_minutes": 25,
        "difficulty": "easy",
        "allergens": "dairy",
        "calories": 150, "protein": 3, "carbohydrates": 14, "fat": 9, "fiber": 3, "vitamins": 30, "minerals": 15,
        "instructions": "**Step 1 - Prepare vegetables:** Wash zucchini and cut into rough pieces. Finely chop onion and garlic.\n**Step 2 - Saute:** Heat olive oil. Cook onion and garlic for 3-4 minutes.\n**Step 3 - Add zucchini:** Add zucchini and cook for 2 minutes.\n**Step 4 - Add broth:** Pour in vegetable broth, bring to a boil and cook for 15 minutes until soft.\n**Step 5 - Blend:** Blend completely smooth.\n**Step 6 - Add cream and serve:** Stir in cream and heat briefly. Season. Especially good with a dollop of sour cream or lemon juice."
    },
    {
        "id": 56,
        "name": "Chicken in Mushroom Cream Sauce",
        "ingredients": ["chicken_breast", "mushroom", "cream", "onion", "garlic", "butter", "salt", "pepper"],
        "amounts": "chicken_breast:400g,mushroom:250g,cream:200ml,onion:1 pc,garlic:2 cloves,butter:20g",
        "time_minutes": 30,
        "difficulty": "medium",
        "allergens": "dairy",
        "calories": 420, "protein": 42, "carbohydrates": 8, "fat": 26, "fiber": 2, "vitamins": 20, "minerals": 30,
        "instructions": "**Step 1 - Prepare the chicken:** Pat dry and season with salt and pepper.\n**Step 2 - Fry the chicken:** Melt butter in a large pan. Fry chicken for 6-7 minutes per side until golden and cooked through. Remove and keep warm.\n**Step 3 - Fry the mushrooms:** In the same fat over high heat, fry sliced mushrooms for 4-5 minutes until golden.\n**Step 4 - Add onion and garlic:** Add finely chopped onion and garlic and cook for 2-3 minutes.\n**Step 5 - Make the cream sauce:** Pour in cream, bring to a boil and reduce for 3-4 minutes until creamy. Season.\n**Step 6 - Return chicken and serve:** Return chicken to the sauce and warm for 2 minutes. Slice and serve with the mushroom sauce."
    },
    {
        "id": 57,
        "name": "Fennel Salad",
        "ingredients": ["fennel", "lemon", "olive_oil", "salt", "pepper", "lettuce"],
        "amounts": "fennel:2 bulbs,lemon:1 pc,olive_oil:3 tbsp,lettuce:0.5 head",
        "time_minutes": 10,
        "difficulty": "easy",
        "allergens": "",
        "calories": 120, "protein": 3, "carbohydrates": 16, "fat": 6, "fiber": 5, "vitamins": 35, "minerals": 20,
        "instructions": "**Step 1 - Wash the fennel:** Wash bulbs and cut off the green fronds. Set fronds aside for garnish.\n**Step 2 - Shave the fennel:** Halve and cut out the hard core. Shave very thinly with a mandoline or sharp knife.\n**Step 3 - Prepare the lettuce:** Wash, dry and tear into bite-sized pieces. Place in a bowl.\n**Step 4 - Make the dressing:** Whisk together lemon juice, olive oil, salt and pepper.\n**Step 5 - Combine:** Add shaved fennel to the lettuce. Pour dressing over and toss carefully.\n**Step 6 - Serve:** Place on plates and garnish with fennel fronds. Serve immediately."
    },
    {
        "id": 58,
        "name": "Quiche Lorraine",
        "ingredients": ["egg", "bacon", "cream", "cheese", "flour", "butter", "onion", "salt", "pepper"],
        "amounts": "egg:4 pcs,bacon:150g,cream:250ml,cheese:100g,flour:200g,butter:100g,onion:1 pc",
        "time_minutes": 55,
        "difficulty": "medium",
        "allergens": "egg,dairy,gluten",
        "calories": 520, "protein": 20, "carbohydrates": 32, "fat": 36, "fiber": 1, "vitamins": 12, "minerals": 22,
        "instructions": "**Step 1 - Preheat oven:** Preheat to 180C.\n**Step 2 - Make the shortcrust:** Combine flour, cold cubed butter and salt. Rub until like breadcrumbs. Add 3 tbsp ice water and press into dough. Refrigerate for 20 minutes.\n**Step 3 - Line the tin:** Roll out and lay into a tart tin. Prick base with a fork. Blind bake for 10 minutes.\n**Step 4 - Make the filling:** Dice bacon and fry until crispy. Finely chop and fry onion. Whisk eggs, cream, grated cheese, salt and pepper.\n**Step 5 - Fill the quiche:** Fill the pre-baked pastry with bacon and onion. Pour egg mixture evenly over.\n**Step 6 - Bake and serve:** Bake for 30-35 minutes until golden and set. Serve warm or cold."
    },
    {
        "id": 59,
        "name": "Shrimp Fried Rice",
        "ingredients": ["shrimp", "rice", "egg", "peas", "carrot", "soy_sauce", "garlic", "ginger", "oil"],
        "amounts": "shrimp:200g,rice:300g,egg:2 pcs,peas:100g,carrot:1 pc,soy_sauce:3 tbsp,garlic:2 cloves,ginger:10g",
        "time_minutes": 25,
        "difficulty": "medium",
        "allergens": "fish,egg,soy",
        "calories": 420, "protein": 26, "carbohydrates": 60, "fat": 10, "fiber": 4, "vitamins": 25, "minerals": 30,
        "instructions": "**Step 1 - Pre-cook the rice:** Cook rice and let cool completely. Cold rice is essential.\n**Step 2 - Prepare vegetables:** Peel carrot and cut into small cubes. Finely chop garlic and ginger.\n**Step 3 - Fry the shrimp:** Heat oil in wok over high heat. Fry shrimp for 1-2 minutes per side until pink. Remove.\n**Step 4 - Fry the vegetables:** Stir-fry carrots, garlic and ginger for 3 minutes. Add peas.\n**Step 5 - Scramble eggs:** Push everything to one side. Crack in eggs and scramble. Mix with vegetables.\n**Step 6 - Add rice and shrimp:** Add rice and shrimp. Stir-fry at high heat for 2-3 minutes. Pour soy sauce over and serve."
    },
    {
        "id": 60,
        "name": "Ratatouille",
        "ingredients": ["eggplant", "zucchini", "bell_pepper", "tomato", "onion", "garlic", "olive_oil", "salt", "pepper"],
        "amounts": "eggplant:1 pc,zucchini:2 pcs,bell_pepper:2 pcs,tomato:4 pcs,onion:1 pc,garlic:3 cloves",
        "time_minutes": 45,
        "difficulty": "easy",
        "allergens": "",
        "calories": 180, "protein": 4, "carbohydrates": 24, "fat": 8, "fiber": 8, "vitamins": 60, "minerals": 25,
        "instructions": "**Step 1 - Prepare the vegetables:** Cut all vegetables into even 2 cm cubes. Finely chop onion and garlic.\n**Step 2 - Salt the eggplant:** Place cubes in a sieve, salt and let sit for 10 minutes. Pat dry.\n**Step 3 - Saute onion and garlic:** Heat olive oil. Cook onion and garlic for 5 minutes.\n**Step 4 - Fry the eggplant:** Add and fry for 5 minutes until lightly coloured.\n**Step 5 - Add remaining vegetables:** Add bell pepper, zucchini and tomatoes. Stir well.\n**Step 6 - Simmer and serve:** Simmer for 20-25 minutes until soft and saucy. Season and serve with bread or rice."
    },
]

# -----------------------------------------------------------------------
# ADD NEW RECIPES BELOW
# Just copy the block above, increase the id by 1 and fill it in!
# -----------------------------------------------------------------------