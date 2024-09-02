"""
Make a round-robin schedule.

Usage:

python main.py player1 player2 player3
"""

import argparse
import sys
from collections import namedtuple
from itertools import combinations
from pprint import pprint

Player = namedtuple("Player", "name")
Match = namedtuple("Match", "player1 player2")

def round_robin(players):
    return [Match(*c) for c in combinations(players, 2)]
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='',
                    description='Round-Robin schedule maker',
                    epilog='',
                    usage='python main.py player1 player2 ...')
    parser.add_argument('players', type=str, nargs='+',
                    help='Players in the round-robin')
    args = parser.parse_args()      
    players = args.players
    if len(players) == 1:
        print(f"Nr of players passed is only 1! Pass at least 2.")
        sys.exit(1)
    players_unique = set(players)
    
    if len(players_unique) < len(players):
        print(f"At least one player name was passed multiple time! Give only unique names.")
        sys.exit(1)

    players = [Player(name=player) for player in players_unique]

    pprint(round_robin(players))

    