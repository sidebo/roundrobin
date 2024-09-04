"""
Make a round-robin schedule.

Usage:

python main.py player1 player2 player3
"""

import argparse
import random
from typing import Tuple, Union
import sys
from collections import namedtuple
from itertools import combinations, product
from pprint import pprint
import pandas as pd
from datetime import time as timeofday
from dataclasses import dataclass
from enum import Enum

DEBUG = False

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

    @property
    def players(self):
        return [self]


class Team(Competitor):
    def __init__(self, player1, player2):
        if not all(isinstance(player, Player) for player in (player1, player2)):
            raise ValueError("Both team members must be Player instances")
        self.player1 = player1
        self.player2 = player2
        super().__init__(str(self))

    def __str__(self):
        return f"{str(self.player1)} + {str(self.player2)}"
    
    @property
    def players(self):
        return [self.player1, self.player2]


TimeSlot = namedtuple("TimeSlot", "court_nr start_time end_time")

@dataclass
class Match:
    competitor1: Competitor
    competitor2: Competitor
    group: str
    time: TimeSlot = None

    @property
    def players(self):
        return self.competitor1.players + self.competitor2.players
        


def round_robin(competitors, group):
    return [Match(*c, group=group) for c in combinations(competitors, 2)]
    
def time_slots():
    dates = ["2024-09-07", "2024-09-28", "2024-10-12", "2024-11-02", "2024-11-16", "2024-12-07"]
    def start_times(day, match_duration):
        start = pd.Timestamp.fromisoformat(day + " 11:00:00")
        end = pd.Timestamp.fromisoformat(day + " 13:00:00")
        return pd.date_range(start, end, freq=match_duration, inclusive="left")

    match_duration = pd.Timedelta("30min")
    courts = [10, 11, 12]
    slots_start = [start_times(day, match_duration) for day in dates]
    slots_start = [s for ss in slots_start for s in ss] # flatten
    slots_end = [s + match_duration for s in slots_start]
    slots = [TimeSlot(court, start, end) for start, end in zip(slots_start, slots_end) for court in courts]
    return  slots
    
# TODO: create all players as global variables. 
# .     now, without it, names must equals between singles and doubles
PETER_J = Player("Peter J")
EDWIN_D = Player("Edwin Dabbaghyan")
DAVID = Player("David Öreby")
EDVIN_S = Player("Edvin S")
KRISTUPAS = Player("Kristupas")
TIAN = Player("Tianhao Liu")
PATRIK = Player("Patrik Blix")
DUSHYANTAN = Player("Dushyanthan")
DENNIS = Player("Dennis")
TOMAS = Player("Tomas")
SISIR = Player("Sisir")
GUNNAR = Player("Gunnar")


GROUPS = {
    "Group1 Singles": [
        Player("Lukas L"),
        Player("Robert W"),
        Player("Oskar S"),
        EDWIN_D,
        Player("Jian Zhang"),
    ],
    "Group2 Singles": [
        TOMAS,
        GUNNAR,
        Player("Saby"),
        DAVID,
        EDVIN_S
    ],
    "Group3 Singles": [
        Player("Alex Chiang"),
        PETER_J,
        KRISTUPAS,
        TIAN,
        PATRIK
    ],
    "Group4 Singles": [
        DUSHYANTAN,
        Player("Kotryna"),
        Player("Ronnie"),
        SISIR,
        DENNIS
        
    ],
    "Group1 Doubles": [
        Team(player1=Player("Filippo"), player2=Player("Yang")),
        Team(player1=TOMAS, player2=Player("Josef")),
        Team(player1=Player("Peter A"), player2=Player("Kristoffer")),
        Team(player1=Player("Nhan"), player2=EDWIN_D),
        Team(player1=Player("Pierre"), player2=Player("Paulina")),
        Team(player1=Player("Danne"), player2=Player("Elodie")),
        
    ],
    "Group2 Doubles": [
        Team(player1=PATRIK, player2=Player("Stefan Winge")),
        Team(player1=DENNIS, player2=TIAN),
        Team(player1=DAVID, player2=Player("John")),
        Team(player1=KRISTUPAS, player2=DUSHYANTAN),
        Team(player1=SISIR, player2=PETER_J),
        Team(player1=EDVIN_S, player2=GUNNAR)
    ]
}

class Infeasible(Exception):
    pass

def assign_times(matches):
    times = time_slots()
    if len(matches) > len(times):
        raise Infeasible(f"Nr of matches {len(matches)} > nr of time time slots {len(times)}")
    while len(times) > len(matches):
        # Remove superfluous time slots
        times = times[:len(matches)]

    random.shuffle(times)
    unassigned = matches.copy()
    assigned = []
    for t in times:
        simultaneous_matches = [m for m in assigned if m.time.start_time == t.start_time]
        players_in_simultaneous_matches = [m.players for m in simultaneous_matches]
        while True:
            candidate = unassigned.pop()

            if DEBUG and simultaneous_matches:
                print('time ', t)
                print('candidate match = ', candidate)
                print('Checking if no conflicts')
                print('simultaneous matches:')
                pprint(simultaneous_matches)
                print(players_in_simultaneous_matches)
            
            if any(p in players_in_simultaneous_matches for p in candidate.players):
                if DEBUG:
                    print("\n**** CONFLICT: try a different candidate match\n\n\n")
                unassigned = [candidate] + unassigned
                continue
            candidate.time = t
            assigned.append(candidate)
            break
    assert len(assigned) == len(matches), "Not all matches were assigned! Could be a bug, but try running again."

def print_group_schedule(matches):
    group = matches[0].group
    print(f"*** SCHEDULE {group}. Copy below, paste into Google Sheets, click 'Data -> Split text to columns'")
    print("Date,Time,Court,Competitor 1,Competitor 2,Set1,Set2,Set3")
    matches = sorted(matches, key=lambda m: (m.time.start_time, m.time.court_nr))
    for m in matches:
        court = m.time.court_nr
        start_time = m.time.start_time
        end_time = m.time.end_time
        # Randomize order of competitors so that 1st can be considered responsible
        c1, c2 = random.sample([m.competitor1, m.competitor2], 2)
        print(f"{start_time.date().strftime('%b %d')},{start_time.time().isoformat('minutes')}-{end_time.time().isoformat('minutes')},{court},{c1.name},{c2.name},,,")
    print("")


def main(args):
    matches = [round_robin(competitors, group) for group, competitors in GROUPS.items()]
    matches = [m for mm in matches for m in mm] # flatten
    assign_times(matches)
    for group in GROUPS:
        matches_group = [m for m in matches if m.group == group]
        print_group_schedule(matches_group)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='',
                    description='Round-Robin schedule maker',
                    epilog='',
                    #usage='python main.py player1 player2 ...')
                    )
    #parser.add_argument('players', type=str, nargs='+',
    #                help='Players in the round-robin')
    args = parser.parse_args()      
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
    main(args)

    