import firebase
import firebasecustomauth

# Initialize Firebase
fb = None

def authenticate(fb_auth_token):
	authentication = firebase.FirebaseAuthentication(fb_auth_token, "scouting@palyrobotics.com", extra={"id": "server"})
	fb = firebase.FirebaseApplication("https://scouting-2017.firebaseio.com/", authentication=authentication)

def fbtest():
	upload_timd_stat("2017cave" , "frc8", "qm", "1", "high_goals_scored", 100)
	upload_timd_stat("2017cave" , "frc8", "qm", "2", "high_goals_scored", 200)
	upload_timd_stat("2017cave" , "frc8", "qm", "3", "high_goals_scored", 300)
	upload_timd_stat("2017cave" , "frc8", "qm", "4", "high_goals_scored", 400)
	upload_team_stat("2017cave" , "frc8", "high_goals_scored_avg", calc_timd_average("2017cave" , "frc8", "high_goals_scored"))
	upload_team_stat("2017cave" , "frc8", "high_goals_scored_sd", calc_timd_stddev("2017cave" , "frc8", "high_goals_scored"))
	return str(calc_timd_average("2017cave", "frc8", "high_goals_scored")) + ", " + str(calc_timd_stddev("2017cave", "frc8", "high_goals_scored"))


def upload_timd_stat(event, team, comp_level, match_number, stat, value):
	print "Uploading TIMD stat: " + str(team) + " - " + str(stat) + ": " + str(value) + " in " + str(comp_level) + str(match_number)
	fb.put(str(event) + "/teams/" + str(team) + "/matches/" + str(comp_level) + "/" + str(match_number), stat, value)

def get_timd_stat(event, team, comp_level, match_number, stat):
	print "Getting TIMD stat: " + str(team) + "'s " + str(stat) + " in " + str(comp_level) + str(match_number)
	return fb.get(str(event) + "/teams/" + str(team) + "/matches/" + str(comp_level) + "/" + str(match_number), stat)

def upload_team_stat(event, team, stat, value):
	print "Uploading team stat: " + str(team) + " - " + str(stat) + ": " + str(value)
	fb.put(str(event) + "/teams/" + str(team) + "/stats/", stat, value)

def get_team_stat(event, team, stat):
	print "Getting team stat: " + str(team) + "'s " + str(stat)
	return fb.get(str(event) + "/teams/" + str(team) + "/stats/", stat)

# Firebase basics
def get_team_matches(event, team, comp_level):
	print "Getting " + str(comp_level) + " match keys for " + str(team)
	matches = []
	matches_raw = fb.get(str(event) + "/teams/" + str(team)  + "/matches/" + comp_level, None)
	if matches_raw != None:
		try:
			for match in matches_raw.keys():
				matches.append(match)
		except AttributeError:
			for i in range(0, len(matches_raw)):
				if matches_raw[i] != None:
					matches.append(i)
	else:
		return None
	return matches