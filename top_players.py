from getters import *
from parsers import *

def main():
    data = get_data()
    parse_top_players(data, 'data/2021-22')

if __name__ == '__main__':
    main()
