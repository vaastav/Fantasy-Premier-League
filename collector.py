import os
import sys
import csv

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
    for i in range(1,4):
        collect_gw(i, directory_name, output_dir)

def main():
    collect_all_gws(sys.argv[1], sys.argv[2])    

if __name__ == '__main__':
    main()
