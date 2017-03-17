import firebase_interactor as fb
import sys

firebase_secret = open(sys.argv[1]).readlines()[1].strip()

def change_match(event, team, match1, match2):
    timd = fb.get(str(event) + "/teams/" + str(team) + "/timd/qm", str(match1))
    print(timd)
#    print(fb.get_timd_stat("2017inwla", 868, "qm", 5, "Auto-Baseline"))
    fb.put(str(event) + "/teams/" + str(team) + "/timd/qm", match2, timd)

def switch_team_match(event, team, comp_level, match):
    timd = fb.get(str(event) + "/teams/" + str(match) + "/timd/" + str(comp_level), str(team))
    print(timd)
    fb.put(str(event) + "/teams/" + str(team) + "/timd/" + str(comp_level), str(match), timd)

def test_calc(event):
    teams = fb.get(str(event), "teams")
    for (key) in teams:
        fb.end_of_match(event, key)

fb.authenticate(firebase_secret)
fb.end_of_match("2017cave", 8)
#test_calc("2017inwla")
#change_match("2017inwla", 4103, 10, 11)
#switch_team_match("2017inwla", 1018, "qm", 29)
#print(fb.get_timd_stat("2017inwla", 29, "qm", 1018, "Auto-Baseline"))
