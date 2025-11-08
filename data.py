import pandas as pd
import sqlite3
from sqlalchemy import create_engine

def build_db(csv_path="data/gapminder_data.csv", db_path="data/data.db", table="data"):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    eng = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table, eng, if_exists="replace", index=False, method="multi")

    sql = f"""
    CREATE UNIQUE INDEX IF NOT EXISTS ux_{table}_country_year ON {table}(country, year);
    CREATE INDEX IF NOT EXISTS idx_{table}_continent ON {table}(continent);
    CREATE INDEX IF NOT EXISTS idx_{table}_year ON {table}(year);

    UPDATE {table}
    SET continent = 'North America'
    WHERE continent = 'Americas' AND country IN (
      'Canada','United States','Mexico','Cuba','Dominican Republic','Haiti',
      'Jamaica','Trinidad and Tobago','Costa Rica','Panama','Honduras',
      'Guatemala','El Salvador','Nicaragua','Belize','Puerto Rico'
    );

    UPDATE {table}
    SET continent = 'South America'
    WHERE continent = 'Americas' AND country IN (
      'Brazil','Argentina','Chile','Uruguay','Paraguay','Bolivia',
      'Peru','Ecuador','Colombia','Venezuela','Guyana','Suriname'
    );
    """
    with sqlite3.connect(db_path) as con:
        con.executescript(sql)
