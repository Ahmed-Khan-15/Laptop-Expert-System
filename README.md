# Computer & Laptop Troubleshooting Expert System

Rule-based expert system (68 rules) built with Python and Streamlit.

## Files
- `app.py` - Streamlit user interface
- `rules.py` - knowledge base (symptoms and 68 rules)
- `engine.py` - inference engine (forward chaining + confidence factors)
- `decision_tree.py` - decision tree for guided diagnosis
- `explain.py` - explanation of each diagnosis

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
