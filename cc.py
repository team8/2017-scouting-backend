import tba_interactor as tba
import firebase_interactor as fb
# import TBAconnection
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
    retval = {}
    for team in teams:
        print str(team) + ": " + str(X[teams.index(team)][0])
        retval[team] = X[teams.index(team)][0]
    return retval
                         
def calculate_defensible_oprs(event):

    teams = tba.get_teams(event)

    A = sp.zeros((len(teams), len(teams)), dtype=int)
    B = sp.zeros((len(teams), 1), dtype=int)

    matches = tba.get_matches_with_teams(event)

    for match in matches:
        if match.score_breakdown is not None:
            blue_teams = match.blue_alliance.teams
            red_teams = match.red_alliance.teams
            for i in range(3):
                for j in range(3):
                    A[teams.index(blue_teams[i])][teams.index(blue_teams[j])] += 1
                    A[teams.index(red_teams[i])][teams.index(red_teams[j])] += 1
            for i in range(3):
                B[teams.index(blue_teams[i])][0] += match.score_breakdown["blue"]["teleopPoints"] + match.score_breakdown["blue"]["foulPoints"]
                B[teams.index(red_teams[i])][0] += match.score_breakdown["red"]["teleopPoints"] + match.score_breakdown["red"]["foulPoints"]

    # Removes teams that did not play to keep matrix Hermitian
    # TODO(Jonathan): Fill the matrix dynamically?
    #index = 0
    #while index < len(A):
    #    if A[index][index] == 0:
    #        A = sp.delete(A, index, 0)
    #        A = sp.delete(A, index, 1)
    #        B = sp.delete(B, index, 0)
    #        team_to_delete = teams[index]
    #        teams = sp.delete(teams, index, 0)
    #    else:
    #        index += 1

    print teams
    pprint(A)
    pprint(B)

    # Cholesky decomposition
    # cond = sp.linalg.expm_cond(A)
    L = sp.linalg.cholesky(A, lower=True, overwrite_a=True)
    sp.savetxt("Pairings.csv", sp.asarray(L), delimiter=",")


    # Forward substitution
    Z = sp.linalg.solve_triangular(L, B, lower=True, trans=0, overwrite_b=True)


    # Backward substitution
    Lt = sp.transpose(L)
    X = sp.linalg.solve_triangular(Lt, Z, lower=False, trans=0, overwrite_b=True)

    pprint(X)
    print "Calculated Defensible OPRs:"
    retval = {}
    for team in teams:
        print str(team) + ": " + str(X[teams.index(team)][0])
        retval[team] = X[teams.index(team)][0]

    return retval


def calculate_adjusted_dprs(event):
	
    teams = []
    
    for team in fb.get_teams(event):
        real_data = fb.get_real_data(event, team, "qm")
        if fb.get_stat_upper_limit(event, team, "End-Defense", real_data) > 0 and len(teams) < 8:
            teams.append(int(team))

    A = sp.zeros((len(teams), len(teams)), dtype=int)
    B = sp.zeros((len(teams), 1), dtype=int)

    matches = tba.get_matches_with_teams(event)

    for match in matches:
        if match.score_breakdown is not None and match.comp_level == "qm":
            blue_teams = match.blue_alliance.teams
            red_teams = match.red_alliance.teams
            for i in range(3):
                for j in range(3):
                    if blue_teams[i] in teams and blue_teams[j] in teams:
                        if fb.get_timd_stat(event, blue_teams[j], "qm", match.match_number, "End-Defense") == "1":
                            A[teams.index(blue_teams[i])][teams.index(blue_teams[j])] += 1
                    if red_teams[i] in teams and red_teams[j] in teams:
                        if fb.get_timd_stat(event, red_teams[j], "qm", match.match_number, "End-Defense") == "1":
                            A[teams.index(red_teams[i])][teams.index(red_teams[j])] += 1
            for i in range(3):
                if blue_teams[i] in teams:
                    if fb.get_timd_stat(event, blue_teams[i], "qm", match.match_number, "End-Defense") == "1":
                        dopr_sums = 0
                        for team in red_teams:
                            dopr = fb.get_team_stat(event, team, "Cc-Defensible-OPR")
                            if dopr is not None:
                                dopr_sums += dopr
                        print dopr_sums
                        B[teams.index(blue_teams[i])][0] += dopr_sums - (match.score_breakdown["red"]["teleopPoints"] + match.score_breakdown["red"]["foulPoints"])
                if red_teams[i] in teams:
                    if fb.get_timd_stat(event, red_teams[i], "qm", match.match_number, "End-Defense") == "1":
                        dopr_sums = 0
                        for team in blue_teams:
                            dopr = fb.get_team_stat(event, team, "Cc-Defensible-OPR")
                            if dopr is not None:
                                dopr_sums += dopr
                        print dopr_sums
                        B[teams.index(red_teams[i])][0] += dopr_sums - (match.score_breakdown["blue"]["teleopPoints"] + match.score_breakdown["blue"]["foulPoints"])


    # Removes teams that did not play to keep matrix Hermitian
    # TODO(Jonathan): Fill the matrix dynamically?
    #index = 0
    #while index < len(A):
    #    if A[index][index] == 0:
    #        A = sp.delete(A, index, 0)
    #        A = sp.delete(A, index, 1)
    #        B = sp.delete(B, index, 0)
    #        team_to_delete = teams[index]
    #        teams = sp.delete(teams, index, 0)
    #    else:
    #        index += 1

    print teams
    pprint(A)
    pprint(B)

    X = sp.linalg.solve(A, B, overwrite_b=True)

    
    pprint(X)
    print "Calculated Adjusted DPRs:"
    retval = {}
    for team in teams:
        print str(team) + ": " + str(X[teams.index(team)][0])
        retval[team] = X[teams.index(team)][0]

    return retval
