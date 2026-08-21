import sqlite3
import pandas as pd
import sys


def load_csv_to_sqlite(csv_file, db_file="fpl.db"):
    df = pd.read_csv(csv_file)

    required_columns = [
        "total_points",
        "now_cost",
        "web_name",
        "element_type",
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}"
        )

    # Keep only the columns we need
    df = df[required_columns]
    df['ppm'] = df['total_points'] * 10 / df['now_cost']

    conn = sqlite3.connect(db_file)

    df.to_sql(
        "players",
        conn,
        if_exists="replace",
        index=False,
    )

    # Useful indexes for the optimization query
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_element_type
        ON players(element_type)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_web_name
        ON players(web_name)
    """)

    conn.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM players"
    ).fetchone()[0]

    conn.close()

    print(f"Loaded {count} players into {db_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python create_table.py <csv_file> [database_file]"
        )
        sys.exit(1)

    csv_file = sys.argv[1]

    db_file = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "fpl.db"
    )

    load_csv_to_sqlite(csv_file, db_file)
