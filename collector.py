import os
import sys
import csv

def get_teams(directory):
    teams = {}
    fin = open(directory + "/teams.csv", 'r')
    reader = csv.DictReader(fin)
    for row in reader:
        teams[int(row['id'])] = row['name']
    return teams


def get_fixtures(directory):
    fixtures_home = {}
    fixtures_away = {}
    fin = open(directory + "/fixtures.csv", 'r')
    reader = csv.DictReader(fin)
    for row in reader:
        fixtures_home[int(row['id'])] = int(row['team_h'])
        fixtures_away[int(row['id'])] = int(row['team_a'])
    return fixtures_home, fixtures_away


def get_positions(directory):
    positions = {}
    names = {}
    pos_dict = {'1': "GK", '2': "DEF", '3': "MID", '4': "FWD", '5': "AM"}
    fin = open(directory + "/players_raw.csv", 'r',encoding="utf-8")
    reader = csv.DictReader(fin)
    for row in reader:
        positions[int(row['id'])] = pos_dict[row['element_type']] 
        names[int(row['id'])] = row['first_name'] + ' ' + row['second_name']
    return names, positions

def get_expected_points(gw, directory):
    xPoints = {}
    try:
        fin = open(os.path.join(directory, 'xP' + str(gw) + '.csv'), 'r')
        reader = csv.DictReader(fin)
        for row in reader:
            xPoints[int(row['id'])] = row['xP']
    except:
        return xPoints    
    return xPoints

def merge_gw(gw, gw_directory):
    """Merge a single gameweek file into merged_gw.csv.
    
    Handles schema changes by:
    1. Reading existing merged_gw.csv columns (if exists)
    2. Merging with new gameweek columns
    3. Rewriting the file with unified schema when columns change
    """
    merged_gw_filename = "merged_gw.csv"
    gw_filename = "gw" + str(gw) + ".csv"
    gw_path = os.path.join(gw_directory, gw_filename)
    out_path = os.path.join(gw_directory, merged_gw_filename)
    
    # Read the new gameweek data
    with open(gw_path, 'r', encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        new_fieldnames = list(reader.fieldnames) + ["GW"]
        new_rows = []
        for row in reader:
            row["GW"] = gw
            new_rows.append(row)
    
    print(f"Processing GW{gw}: {len(new_rows)} rows")
    
    # Check if merged file exists and read existing data
    existing_rows = []
    existing_fieldnames = []
    if os.path.exists(out_path) and gw != 1:
        with open(out_path, 'r', encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            existing_fieldnames = list(reader.fieldnames)
            for row in reader:
                existing_rows.append(row)
    
    # Merge fieldnames - preserve order, add new columns at the end (before GW)
    if existing_fieldnames:
        # Remove GW from both lists for comparison
        existing_cols = [f for f in existing_fieldnames if f != "GW"]
        new_cols = [f for f in new_fieldnames if f != "GW"]
        
        # Find columns that are new
        new_only_cols = [c for c in new_cols if c not in existing_cols]
        
        if new_only_cols:
            print(f"  New columns detected: {new_only_cols}")
            # Insert new columns before GW, maintaining their relative order
            # Find the position where new columns should be inserted
            final_fieldnames = existing_cols + new_only_cols + ["GW"]
        else:
            final_fieldnames = existing_fieldnames
    else:
        final_fieldnames = new_fieldnames
    
    # Combine all rows
    all_rows = existing_rows + new_rows
    
    # Write all data with unified schema
    with open(out_path, 'w', encoding="utf-8", newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=final_fieldnames, 
                               lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for row in all_rows:
            # Fill missing columns with empty string
            filled_row = {field: row.get(field, '') for field in final_fieldnames}
            writer.writerow(filled_row)

def collect_gw(gw, directory_name, output_dir, root_directory_name="data/2025-26"):
    rows = []
    fieldnames = []
    fixtures_home, fixtures_away = get_fixtures(root_directory_name)
    teams = get_teams(root_directory_name)
    names, positions = get_positions(root_directory_name)
    xPoints = get_expected_points(gw, output_dir)
    for root, dirs, files in os.walk(u"./" + directory_name):
        for fname in files:
            if fname == 'gw.csv':
                fpath = os.path.join(root, fname)
                fin = open(fpath, 'r')
                reader = csv.DictReader(fin)
                fieldnames = reader.fieldnames
                for row in reader:
                    if int(row['round']) == gw:
                        id = int(os.path.basename(root).split('_')[-1])
                        name = names[id]
                        position = positions[id]
                        fixture = int(row['fixture'])
                        if row['was_home'] == True or row['was_home'] == "True":
                            row['team'] = teams[fixtures_home[fixture]]
                        else:
                            row['team'] = teams[fixtures_away[fixture]]
                        row['name'] = name
                        row['position'] = position
                        if id in xPoints:
                            row['xP'] = xPoints[id]
                        else:
                            row['xP'] = 0.0
                        rows += [row]

    fieldnames = ['name', 'position', 'team', 'xP'] + fieldnames
    outf = open(os.path.join(output_dir, "gw" + str(gw) + ".csv"), 'w', encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

def collect_all_gws(directory_name, output_dir, root_dir):
    for i in range(1,17):
        collect_gw(i, directory_name, output_dir, root_dir)

def merge_all_gws(num_gws, gw_directory):
    """Merge all gameweeks into merged_gw.csv.
    
    Args:
        num_gws: Number of gameweeks to merge (inclusive)
        gw_directory: Directory containing gw*.csv files
    """
    for i in range(1, num_gws + 1):
        merge_gw(i, gw_directory)


def regenerate_merged_gw(gw_directory):
    """Regenerate merged_gw.csv from all individual gw*.csv files.
    
    This function rebuilds the merged file from scratch, properly handling
    schema changes across gameweeks.
    
    Args:
        gw_directory: Directory containing gw*.csv files
    """
    merged_gw_filename = "merged_gw.csv"
    out_path = os.path.join(gw_directory, merged_gw_filename)
    
    # Find all gameweek files and sort them
    gw_files = []
    for fname in os.listdir(gw_directory):
        if fname.startswith('gw') and fname.endswith('.csv') and fname != merged_gw_filename:
            try:
                gw_num = int(fname[2:-4])  # Extract number from 'gw{num}.csv'
                gw_files.append((gw_num, fname))
            except ValueError:
                continue
    
    gw_files.sort(key=lambda x: x[0])
    
    if not gw_files:
        print("No gameweek files found")
        return
    
    print(f"Found {len(gw_files)} gameweek files")
    
    # First pass: collect all unique column names across all files
    all_columns = set()
    for gw_num, fname in gw_files:
        gw_path = os.path.join(gw_directory, fname)
        with open(gw_path, 'r', encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            all_columns.update(reader.fieldnames)
    
    # Define column order: standard columns first, then any extras, then GW
    # Standard columns based on typical FPL data structure
    standard_order = [
        'name', 'position', 'team', 'xP', 'assists', 'bonus', 'bps', 
        'clean_sheets', 'creativity', 'element', 'expected_assists',
        'expected_goal_involvements', 'expected_goals', 'expected_goals_conceded',
        'fixture', 'goals_conceded', 'goals_scored', 'ict_index', 'influence',
        'kickoff_time', 'minutes'
    ]
    
    # Manager columns (added mid-2024-25 season)
    manager_cols = [c for c in sorted(all_columns) if c.startswith('mng_')]
    
    # Remaining standard columns
    remaining_standard = [
        'modified', 'opponent_team', 'own_goals', 'penalties_missed',
        'penalties_saved', 'red_cards', 'round', 'saves', 'selected',
        'starts', 'team_a_score', 'team_h_score', 'threat', 'total_points',
        'transfers_balance', 'transfers_in', 'transfers_out', 'value',
        'was_home', 'yellow_cards'
    ]
    
    # Build final column order
    final_columns = []
    for col in standard_order:
        if col in all_columns:
            final_columns.append(col)
            all_columns.discard(col)
    
    for col in manager_cols:
        if col in all_columns:
            final_columns.append(col)
            all_columns.discard(col)
    
    for col in remaining_standard:
        if col in all_columns:
            final_columns.append(col)
            all_columns.discard(col)
    
    # Add any remaining columns not in our predefined lists
    for col in sorted(all_columns):
        if col != 'GW':
            final_columns.append(col)
    
    final_columns.append('GW')
    
    print(f"Final schema: {len(final_columns)} columns")
    
    # Second pass: read all data and write with unified schema
    all_rows = []
    for gw_num, fname in gw_files:
        gw_path = os.path.join(gw_directory, fname)
        with open(gw_path, 'r', encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                row['GW'] = gw_num
                all_rows.append(row)
        print(f"  GW{gw_num}: loaded")
    
    # Write the merged file
    with open(out_path, 'w', encoding="utf-8", newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=final_columns, 
                               lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for row in all_rows:
            filled_row = {field: row.get(field, '') for field in final_columns}
            writer.writerow(filled_row)
    
    print(f"Wrote {len(all_rows)} rows to {out_path}")

def main():
    """Main entry point for the collector script.
    
    Usage:
        python collector.py merge <num_gws> <gw_directory>
            Merge gameweeks 1 through num_gws into merged_gw.csv
        
        python collector.py regenerate <gw_directory>
            Regenerate merged_gw.csv from all gw*.csv files
            (fixes schema drift issues)
        
        python collector.py collect <player_dir> <output_dir> <root_dir>
            Collect gameweek data from player files
    
    Examples:
        python collector.py merge 38 data/2024-25/gws
        python collector.py regenerate data/2024-25/gws
    """
    if len(sys.argv) < 2:
        print("Usage: python collector.py <command> [args...]")
        print("Commands: merge, regenerate, collect")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "merge":
        if len(sys.argv) < 4:
            print("Usage: python collector.py merge <num_gws> <gw_directory>")
            sys.exit(1)
        num_gws = int(sys.argv[2])
        gw_directory = sys.argv[3]
        merge_all_gws(num_gws, gw_directory)
    
    elif command == "regenerate":
        if len(sys.argv) < 3:
            print("Usage: python collector.py regenerate <gw_directory>")
            sys.exit(1)
        gw_directory = sys.argv[2]
        regenerate_merged_gw(gw_directory)
    
    elif command == "collect":
        if len(sys.argv) < 5:
            print("Usage: python collector.py collect <player_dir> <output_dir> <root_dir>")
            sys.exit(1)
        collect_all_gws(sys.argv[2], sys.argv[3], sys.argv[4])
    
    else:
        # Legacy mode: assume it's num_gws for backwards compatibility
        try:
            num_gws = int(sys.argv[1])
            if len(sys.argv) >= 3:
                merge_all_gws(num_gws, sys.argv[2])
            else:
                print("Usage: python collector.py <num_gws> <gw_directory>")
                sys.exit(1)
        except ValueError:
            print(f"Unknown command: {command}")
            sys.exit(1)


if __name__ == '__main__':
    main()
