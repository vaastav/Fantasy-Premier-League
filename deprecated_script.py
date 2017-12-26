import urllib2
import urllib
import re
import csv
import codecs
import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

# This script is now deprecated.

def main():
   all_players = []
   fpl = urllib.urlretrieve("http://fantasy.premierleague.com/player-list/","allplayers.txt")
   players = open('allplayers.txt', 'rU')
   all_player = players.read()
   names = re.findall(r'<td>(\w*|\w*\W*\w*)</td>\s*<td>(\w*\s\w*|\w*)</td>\s*<td>(\d+)</td>',all_player)
   
   output = open('players2.csv','wb');
   output.write(codecs.BOM_UTF8)
   writer = csv.writer(output,delimiter = ',',quotechar = '|',quoting = csv.QUOTE_MINIMAL)
   writer.writerow(["Name","Team","Points"])
   
   for player in names:
     (name,team,points) = player
     writer.writerow([name,team,points])

if __name__ == '__main__':
   main()