import tba_interactor as tba
import firebase_interactor as fb
import sys

firebase_secret = open(sys.argv[1]).readlines()[1].strip()

def change_match(event, team, match1, match2):
    timd = fb.get(str(event) + "/teams/" + str(team) + "/timd/qm", str(match1))
    print(timd)
#    print(fb.get_timd_stat("2017inwla", 868, "qm", 5, "Auto-Baseline"))
    fb.put(str(event) + "/teams/" + str(team) + "/timd/qm", match2, timd)

def change_team(event, team1, team2, match):
    timd = fb.get(str(event) + "/teams/" + str(team1) + "/timd/qm", str(match))
    fb.put(str(event) + "/teams/" + str(team2) + "/timd/qm", match, timd)

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
        data = fb.get(str(event1) + "/teams/", str(team))
        pit = fb.parse_firebase_unicode(data).get("pit")
        fb.put(str(event2) + "/teams/" + str(team), "pit", pit)

fb.authenticate(firebase_secret)
change_team("2017cave", 6449, 4964, 49)
change_team("2017cave", 6449, 4964, 21)
change_team("2017cave", 9999, 3993, 51)
change_team("2017cave", 5896, 5869, 45)
change_team("2017cave", 2589, 4078, 36)
change_team("2017cave", 5665, 5869, 51)
change_team("2017cave", 3769, 3759, 36)
change_team("2017cave", 7442, 2443, 48)
change_team("2017cave", 689, 589, 44)
#change_match("2017cave", 981, 34, 35)
#change_team("2017cave", 1907, 1967, 33)
#change_match("2017cave", 3863, 8, 7)
#change_match("2017cave", 8, 7656755, 6)
#change_team("2017cave", 881, 981, 4)
#change_team("2017cave", 4954, 4964, 25)
#change_event_for_pit("2017cave_practice", "2017cave")
#for team in tba.get_teams("2017cave"):
#    if team != 114 and team != 1661 and team != 2489 and team != 3859 and team != 3863 and team != 3882 and team != 3965 and team != 4913 and team != 5477 and team != 5678 and team != 6764:
#        print team
#        if fb.get("2017cave/teams/" + str(team), "timd") == None:
#            print "hi"
#        fb.end_of_match("2017cave", team)
#test_calc("2017inwla")
#change_match("2017inwla", 4103, 10, 11)
#switch_team_match("2017inwla", 1018, "qm", 29)
#print(fb.get_timd_stat("2017inwla", 29, "qm", 1018, "Auto-Baseline"))
