#import tba_interactor as tba
import firebase_interactor as fb
import sys
# import cc
import threading

firebase_secret = open(sys.argv[1]).readlines()[1].strip()

def change_match(event, team, match1, match2):
    timd = fb.get(str(event) + "/teams/" + str(team) + "/timd/qm", str(match1))
    print(timd)
#    print(fb.get_timd_stat("2017inwla", 868, "qm", 5, "Auto-Baseline"))
    fb.put(str(event) + "/teams/" + str(team) + "/timd/qm", match2, timd)

def change_team(event, team1, team2, match):
    timd = fb.get(str(event) + "/teams/" + str(team1) + "/timd/qm", str(match))
    fb.put(str(event) + "/teams/" + str(team2) + "/timd/qm", match, timd)

def change_team_for_pit(event, team1, team2):
    data = fb.get(str(event) + "/teams/", str(team1))
    if data is not None:
        pit = fb.parse_firebase_unicode(data).get("pit")
        fb.put(str(event) + "/teams/" + str(team2), "pit", pit)

def switch_team_match(event, team, comp_level, match):
    timd = fb.get(str(event) + "/teams/" + str(match) + "/timd/" + str(comp_level), str(team))
    print(timd)
    fb.put(str(event) + "/teams/" + str(team) + "/timd/" + str(comp_level), str(match), timd)

def test_calc(event):
    teams = fb.get(str(event), "teams")
    for (key) in teams:
        fb.end_of_match(event, key)

def change_event_for_pit(event1, event2):
    teams = fb.get(str(event1), "teams")
    for (team) in teams:
        if fb.get(str(event2) + "/teams", str(team)) is not None and fb.get(str(event2) + "/teams/" + str(team), "pit") is None:
            print team
            data = fb.get(str(event1) + "/teams/", str(team))
            if data is not None:
                pit = fb.parse_firebase_unicode(data).get("pit")
                fb.put(str(event2) + "/teams/" + str(team), "pit", pit)

def import_skyes():
    f = open("sykes-svrweek3.csv", "r")
    data = [[j.replace("\n", "").replace("\r", "") for j in i.split(",")] for i in f.readlines()]

    print data
    raw_input()

    for i in data[1:]:
        for j in range(2,len(i)):
            print "Uploading For Team #{}.  Stat {} Value {}".format(i[0], data[0][j], i[j])
            fb.upload_team_stat("2017roe", i[0], data[0][j], i[j])

def find_no_pit(event):
    teams = fb.get(str(event), "teams")
    for (team) in teams:
        if fb.get(str(event) + "/teams/" + str(team), "pit") is None:
            print team

def find_no_auto_notes(event):
    teams = fb.get(str(event), "teams")
    for (team) in teams:
        if fb.get(str(event) + "/teams/" + str(team) + "/pit/", "Auto-Notes") is None:
            print team

def find_wrong_data(event):
    matches = tba.get_matches_with_teams(event)
    teams = fb.get(str(event), "teams")
    for (team) in teams:
        timds = fb.get(str(event) + "/teams/" + str(team) + "/timd", "qm")
        for (timd) in timds:
            valid = False
            for (match) in matches:
                if str(match.match_number) == str(timd) and (int(team) in match.blue_alliance.teams or int(team) in match.red_alliance.teams):
                    valid = True
            if valid == False:
                print "Bad data for team " + str(team) + " in match " + str(timd)

def change_list(event):
    teams = fb.get(str(event), "teams")
    for (team) in teams:
        l = fb.get(str(event) + "/teams/" + str(team) + "/timd", "qm")
#        if l is not None:
#            if l.get("test") is not None:
#                print team
#                fb.delete(str(event) + "/teams/" + str(team) + "/timd/qm", "test")
        if isinstance(l, list):
            print team
            fb.put(str(event) + "/teams/" + str(team) + "/timd/qm", "test", "test")
            """
            timd = l[1]
            d = {"1": timd}
            print d
            fb.put(str(event) + "/teams/" + str(team) + "/timd", "qm", d)
            """

fb.authenticate(firebase_secret)
fb.end_of_match("2017roe", 4276)
"""
teams = fb.get("2017roe", "teams")
for (team) in teams:
    if fb.get("2017roe/teams/" + str(team) + "/timd/qm", 1) is not None:
        print team
        fb.end_of_match("2017roe", team)
"""
#change_list("2017roe")
#change_event_for_pit("2017casj", "2017roe")
#change_team_for_pit("2017roe", 314014, 3140)
#change_team_for_pit("2017roe", 3616, 3316)
#for i in fb.get_teams("2017cave"):
#    newEndOfmatchThread = threading.Thread(target=fb.end_of_match, args=("2017cave", i))
#        newEndOfmatchThread.start()
#fb.end_of_match("2017casj", 8)
#change_match("2017casj", 4904, 4904, 82)
#change_team("2017casj", 799, 766, 71)
#change_team("2017casj", 4158, 4159, 70)
#change_match("2017casj", 971, 66, 67)
#change_team("2017casj", 1357, 1351, 85)
#change_match("2017casj", 100, 92, 82)
#change_team("2017casj", 6415, 6418, 79)
#change_team("2017casj", 952, 852, 86)
#change_team("2017casj", 2145, 2135, 1)
#change_match("2017casj", 6410, 14, 15)
#change_match("2017casj", 971, 33, 34)
#change_match("2017casj", 254, 25 ,26)
#change_match("2017casj", 5728, 43, 44)
#change_match("2017casj", 5728, 29, 30)
#change_match("2017casj", 4159, 57, 56)
#change_match("2017casj", 4159, 45, 46)
# find_wrong_data("2017casj")

#import_skyes()
# for i in fb.get_teams("2017casj"):
#     newEndOfmatchThread = threading.Thread(target=fb.end_of_match, args=("2017casj", i))
#     newEndOfmatchThread.start()
#change_team("2017casj", 2474, 2473, 30)
#change_team("2017casj", 3382, 3482, 26)
#switch_team_match("2017casj", 2643, "qm", 50)
#change_match("2017casj", 581, 38753, 14)
#change_match("2017casj", 846, 28548, 13)
#find_no_auto_notes("2017casj")
#change_event_for_pit("2017casj_practice", "2017casj")
#find_no_pit("2017roe")
#change_team("2017casj", 2613, 2813, 12694501)
#change_team("2017casj", 5739, 5737, 111111111)
#cc.calculate_adjusted_dprs("2017casj")
#dict = cc.calculate_adjusted_dprs("2017casj")
#for key in dict.keys():
#    print dict[key]
#    fb.put("2017casj/teams/" + str(key) + "/data", "Cc-Adjusted-DPR", dict[key])
#cc.calculate_goals("2017casj", "Auto", "Fuel-Low")
#cc.calculate_defensible_oprs("2017cave")
#import_skyes()
# cc.calculate_goals("2017cave", "Auto", "Fuel-Low")
#change_team("2017cave", 2448, 2443, 54)
#change_team("2017cave", 6449, 4964, 49)
#change_team("2017cave", 6449, 4964, 21)
#change_team("2017cave", 9999, 3993, 51)
#change_team("2017cave", 5896, 5869, 45)
#change_team("2017cave", 2589, 4078, 36)
#change_team("2017cave", 5665, 5869, 51)
#change_team("2017cave", 3769, 3759, 36)
#change_team("2017cave", 7442, 2443, 48)
#change_team("2017cave", 689, 589, 44)
#change_match("2017cave", 981, 34, 35)
#change_team("2017cave", 1907, 1967, 33)
#change_match("2017cave", 3863, 8, 7)
#change_match("2017cave", 8, 7656755, 6)
#change_team("2017cave", 881, 981, 4)
#change_team("2017cave", 4954, 4964, 25)
#change_event_for_pit("2017cave", "2017casj")
#for team in tba.get_teams("2017casj"):
#        print team
#        if fb.get("2017casj/teams/" + str(team), "timd") == None:
#            print "hi"
#        fb.end_of_match("2017casj", team)
#test_calc("2017inwla")
#change_match("2017inwla", 4103, 10, 11)
#switch_team_match("2017casj", 100, "qm", 8)
#switch_team_match("2017casj", 668, "qm", 8)
#switch_team_match("2017casj", 852, "qm", 8)
#switch_team_match("2017casj", 4158, "qm", 8)
#switch_team_match("2017casj", 5737, "qm", 8)
#switch_team_match("2017casj", 5924, "qm", 8)
#switch_team_match("2017casj", 6039, "qm", 8)
#print(fb.get_timd_stat("2017inwla", 29, "qm", 1018, "Auto-Baseline"))
