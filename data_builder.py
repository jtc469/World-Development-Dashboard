import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text

def build_db(csv_path="data/gapminder_data.csv", db_path="data/data.db", table="data"):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    dtype_map = {
        "country": "TEXT",
        "continent": "TEXT",
        "year": "INTEGER",
        "lifeexp": "REAL",
        "pop": "INTEGER",
        "gdppercap": "REAL"
    }
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        cols = ", ".join([f"{k} {v}" for k, v in dtype_map.items()])
        conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.execute(text(f"CREATE TABLE {table} ({cols}, PRIMARY KEY(country, year))"))
        df.to_sql(table, conn, if_exists="append", index=False)
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_continent ON {table}(continent)"))
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_year ON {table}(year)"))

    sql = """
    UPDATE data
    SET continent = 'North America'
    WHERE continent = 'Americas' AND country IN (
      'Canada','United States','Mexico','Cuba','Dominican Republic','Haiti',
      'Jamaica','Trinidad and Tobago','Costa Rica','Panama','Honduras',
      'Guatemala','El Salvador','Nicaragua','Belize','Puerto Rico'
    );
    UPDATE data
    SET continent = 'South America'
    WHERE continent = 'Americas' AND country IN (
      'Brazil','Argentina','Chile','Uruguay','Paraguay','Bolivia',
      'Peru','Ecuador','Colombia','Venezuela','Guyana','Suriname'
    );
    """
    with sqlite3.connect(db_path) as con:
        con.executescript(sql)

if __name__ == "__main__":
    build_db()
