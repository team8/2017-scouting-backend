import tba_interactor as tba
import firebase_interactor as fb
import TBAconnection
import scipy as sp
from scipy import linalg
import math
from pprint import pprint

def calculate_goals(event, period_key, goal_key):
    # period_key: "Auto" or "Tele"
    # goal_key: "Fuel-High" or "Fuel-Low"

    stat = period_key + "-" + goal_key + "-Cycles"
    tbaperiod = ""
    if period_key == "Tele":
        tbaperiod = "Teleop"
    else:
        tbaperiod = period_key
    tbastat = tbaperiod.lower() + goal_key.split('-')[0] + goal_key.split('-')[1]
    teams = []
    
    for team in fb.get_teams(event):
        real_data = fb.get_real_data(event, team, "qm")
        if fb.get_stat_upper_limit(event, team, stat, real_data) > 0:
            teams.append(team)

    print teams

    A = sp.zeros((len(teams), len(teams)), dtype=float)
    B = sp.zeros((len(teams), 1), dtype=int)

    for team1 in teams:
        total_fuel = 0
        matches = fb.get_team_matches(event, team1, "qm")
        for team2 in teams:
            total_cycles = 0
            for match in matches:
                if tba.get_team_alliance(event, team1, "qm", match) == tba.get_team_alliance(event, team2, "qm", match) and tba.get_team_alliance(event, team1, "qm", match) is not None:
                    match_stats = fb.get_match_stats(event, "qm", match)[0]
                    total_cycles += float(match_stats[team1][stat])
                    total_fuel += tba.get_fuel_in_match(event, "qm" + match, tba.get_team_alliance(event, team1, "qm", match), tbastat)
            A[teams.index(team2)][teams.index(team1)] = total_cycles
        B[teams.index(team1)][0] = total_fuel
    pprint(A)
    pprint(B)

    print "Solving for matrix X..."

    X = sp.linalg.solve(A, B, overwrite_b=True)

    pprint(X)

    print "Calculated " + period_key + "-" + goal_key + " contributions:"
    for team in teams:
        print str(team) + ": " + str(X[teams.index(team)][0])
        
    
#def calculate_defensible_oprs(event):


#def calculate_adjusted_dprs(event):
	
