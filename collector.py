import os
import sys
import csv

def get_teams(directory):
    teams = {}
    fin = open(directory + "/teams.csv", 'rU')
    reader = csv.DictReader(fin)
    for row in reader:
        teams[int(row['id'])] = row['name']
    return teams


def get_fixtures(directory):
    fixtures_home = {}
    fixtures_away = {}
    fin = open(directory + "/fixtures.csv", 'rU')
    reader = csv.DictReader(fin)
    for row in reader:
        fixtures_home[int(row['id'])] = int(row['team_h'])
        fixtures_away[int(row['id'])] = int(row['team_a'])
    return fixtures_home, fixtures_away


def get_positions(directory):
    positions = {}
    names = {}
    pos_dict = {'1': "GK", '2': "DEF", '3': "MID", '4': "FWD"}
    fin = open(directory + "/players_raw.csv", 'rU',encoding="utf-8")
    reader = csv.DictReader(fin)
    for row in reader:
        positions[int(row['id'])] = pos_dict[row['element_type']] 
        names[int(row['id'])] = row['first_name'] + ' ' + row['second_name']
    return names, positions

def get_expected_points(gw, directory):
    xPoints = {}
    try:
        fin = open(os.path.join(directory, 'xP' + str(gw) + '.csv'), 'rU')
        reader = csv.DictReader(fin)
        for row in reader:
            xPoints[int(row['id'])] = row['xP']
    except:
        return xPoints    
    return xPoints

def merge_gw(gw, gw_directory):
    merged_gw_filename = "merged_gw.csv"
    gw_filename = "gw" + str(gw) + ".csv"
    gw_path = os.path.join(gw_directory, gw_filename)
    fin = open(gw_path, 'rU', encoding="utf-8")
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    fieldnames += ["GW"]
    rows = []
    for row in reader:
        row["GW"] = gw
        rows += [row]
    out_path = os.path.join(gw_directory, merged_gw_filename)
    fout = open(out_path,'a', encoding="utf-8")
    writer = csv.DictWriter(fout, fieldnames=fieldnames, lineterminator='\n')
    print(gw)
    if gw == 1:
        writer.writeheader()
    for row in rows:
        writer.writerow(row)

def collect_gw(gw, directory_name, output_dir, root_directory_name="data/2021-22"):
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
                fin = open(fpath, 'rU')
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
    for i in range(1, num_gws):
        merge_gw(i, gw_directory)

def main():
    #collect_all_gws(sys.argv[1], sys.argv[2], sys.argv[3])
    merge_all_gws(int(sys.argv[1]), sys.argv[2])
    #collect_gw(35, sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
