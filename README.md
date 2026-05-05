This is the description of the Group number 06.06. 
We are developing a tool that helps users find suitable recipes based on the ingredients they already have at home. The app aims to reduce food waste and make everyday cooking easier by suggesting meals that fit the user’s available ingredients, preferences, and filters. 
ChatGPT and Claude was used to assist with parts of the code and documentation.

Here is how it works:

Folder structure:



## Project Structure

```
emptythefridge/
├── app.py            # Main Streamlit app
├── database.py       # SQLite database setup and queries
├── recipes.py        # All built-in recipes and ingredient data
├── recommender.py    # ML-based recommendation engine (scikit-learn)
├── api_loader.py     # TheMealDB API integration
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

