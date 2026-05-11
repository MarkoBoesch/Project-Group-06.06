This is the description of the Group number 06.06. 
We are developing a tool that helps users find suitable recipes based on the ingredients they already have at home. The app aims to reduce food waste and make everyday cooking easier by suggesting meals that fit the user’s available ingredients, preferences, and filters. 
ChatGPT and Claude was used to assist with parts of the code and documentation.

Here is how it works:

## Project Structure

EmptytheFridge/
├── app.py              # Main Streamlit app (UI, pages, navigation)
├── db.py               # SQLite setup + read/write functions
├── api_loader.py       # TheMealDB API loader (fetch, clean, save recipes)
├── recommender.py      # ML-based recommendations (scikit-learn Random Forest)
├── constants.py        # Lookup tables (pantry staples, diet sets, prices, display names)
├── requirements.txt    # Python dependencies
└── README.md           # This file

