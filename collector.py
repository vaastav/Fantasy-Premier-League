import os
import sys
import csv

def merge_gw(gw, gw_directory):
    merged_gw_filename = "merged_gw.csv"
    gw_filename = "gw" + str(gw) + ".csv"
    gw_path = os.path.join(gw_directory, gw_filename)
    fin = open(gw_path, 'rU')
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    fieldnames += ["GW"]
    rows = []
    for row in reader:
        row["GW"] = gw
        rows += [row]
    out_path = os.path.join(gw_directory, merged_gw_filename)
    fout = open(out_path,'a')
    writer = csv.DictWriter(fout, fieldnames=fieldnames, lineterminator='\n')
    if gw == 1:
        writer.writeheader()
    for row in rows:
        writer.writerow(row)

def collect_gw(gw, directory_name, output_dir):
    rows = []
    fieldnames = []
    for root, dirs, files in os.walk(u"./" + directory_name):
        for fname in files:
            if fname == 'gw.csv':
                fpath = os.path.join(root, fname)
                fin = open(fpath, 'rU')
                reader = csv.DictReader(fin)
                fieldnames = reader.fieldnames
                for row in reader:
                    if int(row['round']) == gw:
                        row['name'] = os.path.basename(root)
                        rows += [row]

    fieldnames = ['name'] + fieldnames
    outf = open(os.path.join(output_dir, "gw" + str(gw) + ".csv"), 'w')
    writer = csv.DictWriter(outf, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

def collect_all_gws(directory_name, output_dir):
    for i in range(1,5):
        collect_gw(i, directory_name, output_dir)

def merge_all_gws(num_gws, gw_directory):
    for i in range(1, num_gws):
        merge_gw(i, gw_directory)

def main():
    #collect_all_gws(sys.argv[1], sys.argv[2])
    merge_all_gws(int(sys.argv[1]), sys.argv[2])

if __name__ == '__main__':
    main()
