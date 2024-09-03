"""
Make a round-robin schedule.

Usage:

python main.py player1 player2 player3
"""

import argparse
import sys
from collections import namedtuple
from itertools import combinations, product
from pprint import pprint
import pandas as pd
from datetime import time as timeofday

Player = namedtuple("Player", "name")
Match = namedtuple("Match", "player1 player2")
TimeSlot = namedtuple("TimeSlot", "court_nr start_time end_time")

def round_robin(players):
    return [Match(*c) for c in combinations(players, 2)]
    
def time_slots():
    dates = ["2024-09-07", "2024-09-28", "2024-10-12", "2024-11-02", "2024-11-16", "2024-12-07"]
    def start_times(day, match_duration):
        start = pd.Timestamp.fromisoformat(day + " 11:00:00")
        end = pd.Timestamp.fromisoformat(day + " 14:00:00")
        return pd.date_range(start, end, freq=match_duration, inclusive="left")

    match_duration = pd.Timedelta("30min")
    courts = [10, 11, 12]
    slots_start = [start_times(day, match_duration) for day in dates]
    slots_start = [s for ss in slots_start for s in ss] # flatten
    slots_end = [s + match_duration for s in slots_start]
    slots = [TimeSlot(court, start, end) for start, end in zip(slots_start, slots_end) for court in courts]
    return  slots
    

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

    