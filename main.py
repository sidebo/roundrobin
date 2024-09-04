"""
Make a round-robin schedule.

Usage:

python main.py player1 player2 player3
"""

import argparse
from typing import Tuple, Union
import sys
from collections import namedtuple
from itertools import combinations, product
from pprint import pprint
import pandas as pd
from datetime import time as timeofday
from dataclasses import dataclass
from enum import Enum

class Sex(str, Enum):
    male = "male"
    female = "female"


@dataclass
class Player:
    name: str
    sex: Sex = None

    def __str__(self):
        return self.name

@dataclass
class Team:
    player1: Player
    player2: Player

    def __str__(self):
        return f"{str(self.player1)} + {str(self.player2)}"

@dataclass
class Competitor:
    name: str
#
#    def __init__(self, player_or_team: Union[str, Player, Tuple[Player]]):
#        if isinstance(player_or_team, str):
#            self = Player(player_or_team)
#        elif isinstance(player_or_team, Player):
#            self = player_or_team
#        elif isinstance(player_or_team, list):
#            self = Team(*player_or_team)


class Player(Competitor):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return f"{self.name}" #, Position: {self.position}"


class Team(Competitor):
    def __init__(self, player1, player2):
        if not all(isinstance(player, Player) for player in (player1, player2)):
            raise ValueError("Both team members must be Player instances")
        self.player1 = player1
        self.player2 = player2
        super().__init__(str(self))

    def __str__(self):
        return f"{str(self.player1)} + {str(self.player2)}"
    
    def players(self):
        return self.player1, self.player2


TimeSlot = namedtuple("TimeSlot", "court_nr start_time end_time")

@dataclass
class Match:
    competitor1: Competitor
    competitor2: Competitor
    group: str
    time: TimeSlot = None


def round_robin(competitors, group):
    return [Match(*c, group=group) for c in combinations(competitors, 2)]
    
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
    
GROUPS = {
    "Group1 Singles": [
        Player("Lukas L"),
        Player("Robert W"),
        Player("Oskar S"),
        Player("Edwin Dabbaghyan"),
        Player("Jian Zhang"),
    ],
    "Group2 Singles": [
        Player("Tomas A"),
        Player("David Öreby"),
        Player("Gunnar"),
        Player("Saby"),
        Player("Edvin S"),
    ]
}

class Infeasible(Exception):
    pass

def assign_times(matches):
    times = time_slots()
    if len(matches) > len(times):
        raise Infeasible(f"Nr of matches {len(matches)} > nr of time time slots {len(times)}")
    for m in matches:
        m.time = times.pop()


def main(args):
    matches = [round_robin(competitors, group) for group, competitors in GROUPS.items()]
    matches = [m for mm in matches for m in mm] # flatten
    assign_times(matches)
    pprint(matches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='',
                    description='Round-Robin schedule maker',
                    epilog='',
                    #usage='python main.py player1 player2 ...')
                    )
    #parser.add_argument('players', type=str, nargs='+',
    #                help='Players in the round-robin')
    #args = parser.parse_args()      
    #players = args.players
    #if len(players) == 1:
    #    print(f"Nr of players passed is only 1! Pass at least 2.")
    #    sys.exit(1)
    #players_unique = set(players)
    
    #if len(players_unique) < len(players):
    #    print(f"At least one player name was passed multiple time! Give only unique names.")
    #    sys.exit(1)

    #players = [Player(name=player) for player in players_unique]

    #pprint(round_robin(players))
    main(None)

    