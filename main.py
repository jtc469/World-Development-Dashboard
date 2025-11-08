import os
from data import build_db

csv_path = "data/gapminder_data.csv"
db_path = "data/data.db"

if not os.path.exists(db_path):
    build_db(csv_path, db_path)

os.system("streamlit run dashboard.py --server.port 8080")