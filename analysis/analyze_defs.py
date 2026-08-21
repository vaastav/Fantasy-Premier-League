import sqlite3
import pandas as pd

import sqlite3
import pandas as pd
from itertools import combinations


def analyze_combos(
    db_file,
    current_picks,
    remaining_budget,
    remaining_slots,
    current_ppm,
    minimum_points,
):
    conn = sqlite3.connect(db_file)

    # Get only eligible midfielders first.
    #
    # This is much easier to reason about than putting all
    # filtering into the self-join.
    placeholders = ",".join("?" for _ in current_picks)

    query = """
        SELECT
            web_name,
            total_points,
            now_cost,
            ppm
        FROM players
        WHERE element_type = 2
          AND total_points >= ?
    """

    params = [minimum_points]

    if current_picks:
        query += f"""
          AND web_name NOT IN ({placeholders})
        """
        params.extend(current_picks)

    midfielders = pd.read_sql_query(
        query,
        conn,
        params=params,
    )

    conn.close()

    print(f"Eligible midfielders: {len(midfielders)}")

    if len(midfielders) < remaining_slots:
        return pd.DataFrame()

    results = []

    # Generate combinations in Python.
    # SQL is still being used to retrieve/filter the data.
    for combo in combinations(
        midfielders.itertuples(index=False),
        remaining_slots,
    ):
        combo_cost = sum(p.now_cost for p in combo)

        if combo_cost > remaining_budget:
            continue

        combo_ppm = sum(p.ppm for p in combo)
        combo_points = sum(p.total_points for p in combo)

        results.append({
            "combo_cost": combo_cost / 10,
            "total_ppm": combo_ppm,
            "total_points": combo_points,
            "new_picks": [p.web_name for p in combo],
            "remaining_budget": (
                (remaining_budget - combo_cost)/10
            ),
        })

    if not results:
        return pd.DataFrame()

    return (
        pd.DataFrame(results)
        .sort_values(
            ["total_ppm", "remaining_budget"],
            ascending=[False, False],
        )
        .head(10)
        .reset_index(drop=True)
    )


def analyze_combos_points(
    db_file,
    current_picks,
    remaining_budget,
    remaining_slots,
    current_points,
    minimum_points,
):
    """
    Find the top 10 combinations of midfielders that:

    - Are not already in current_picks
    - Have at least minimum_points total points
    - Fit within remaining_budget
    - Contain exactly remaining_slots players
    - Maximize total points

    Parameters
    ----------
    db_file : str
        Path to SQLite database.

    current_picks : list[str]
        Names of already selected players.

    remaining_budget : float
        Budget available for remaining players.

    remaining_slots : int
        Number of players still to select.

    current_points : float
        Total points of already selected players.

    minimum_points : float
        Minimum total_points required for a candidate midfielder.

    Returns
    -------
    pd.DataFrame
        Top 10 combinations ranked by total points.
    """

    conn = sqlite3.connect(db_file)

    # Get eligible midfielders
    query = """
        SELECT
            web_name,
            total_points,
            now_cost,
            ppm
        FROM players
        WHERE element_type = 2
          AND total_points >= ?
    """

    params = [minimum_points]

    if current_picks:
        placeholders = ",".join(
            "?" for _ in current_picks
        )

        query += f"""
          AND web_name NOT IN ({placeholders})
        """

        params.extend(current_picks)

    midfielders = pd.read_sql_query(
        query,
        conn,
        params=params,
    )

    conn.close()

    print(f"Eligible midfielders: {len(midfielders)}")

    if len(midfielders) < remaining_slots:
        return pd.DataFrame()

    results = []

    # Generate all possible combinations
    for combo in combinations(
        midfielders.itertuples(index=False),
        remaining_slots,
    ):
        combo_cost = sum(
            player.now_cost
            for player in combo
        )

        # Budget constraint
        if combo_cost > remaining_budget:
            continue

        combo_points = sum(
            player.total_points
            for player in combo
        )

        total_points = (
            current_points + combo_points
        )

        results.append({
            "combo_cost": combo_cost / 10,
            "total_points": total_points,
            "new_picks": [
                player.web_name
                for player in combo
            ],
            "remaining_budget": (
                (remaining_budget - combo_cost) / 10
            ),
        })

    if not results:
        return pd.DataFrame()

    # Maximize total points
    return (
        pd.DataFrame(results)
        .sort_values(
            ["total_points", "remaining_budget"],
            ascending=[False, False],
        )
        .head(10)
        .reset_index(drop=True)
    )

def budget_version():
    current_picks = []

    results = analyze_combos(
        db_file="fpl.db",
        current_picks=current_picks,
        remaining_budget=400,
        remaining_slots=5,
        current_ppm=0,
        minimum_points=90,
    )

    print(results.to_string(index=False))

def general_version():
    current_picks = []
    results = analyze_combos_points(
        db_file="fpl.db",
        current_picks=current_picks,
        remaining_budget=190,
        remaining_slots=3,
        current_points=0,
        minimum_points=90,
    )
    print(results.to_string(index=False))

def bench_fodder_version():
    current_picks = []
    
    results = analyze_combos_points(
        db_file="fpl.db",
        current_picks=current_picks,
        remaining_budget=350,
        remaining_slots=4,
        current_points=0,
        minimum_points=90,
    )
    print(results.to_string(index=False))

if __name__ == "__main__":
    general_version()

