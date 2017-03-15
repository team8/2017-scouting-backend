from __future__ import division
import firebase
import firebasecustomauth
import collections


# Initialize Firebase
fb = None

def authenticate(fb_auth_token):
	authentication = firebase.FirebaseAuthentication(fb_auth_token, "scouting@palyrobotics.com", extra={"id": "server"})
	global fb
	fb = firebase.FirebaseApplication("https://scouting-2017.firebaseio.com/", authentication=authentication)
	

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

def get_match_stats(event, comp_level, match_number):
	"""
	Returns a dictionary that maps team to data about the match they were in.  The second element is
	the number of teams that have data uploaded.
	"""
	print "Getting match stat: " + str(event) + "/" + str(comp_level) + "/" + str(match_number)

	match_stats = fb.get(str(event)+"/teams/", None)
	
	various_timd_map = {}

	match_stats = parse_firebase_unicode(match_stats)
	
	for team in match_stats.keys():
		if match_stats[team].has_key("matches"):
			if match_stats[team]["matches"].has_key(comp_level):
				if match_stats[team]["matches"][comp_level].has_key(match_number):
					various_timd_map[team] = match_stats[team]["matches"][comp_level][match_number]

	return various_timd_map, len(various_timd_map.keys())



# Firebase basics
def get_team_matches(event, team, comp_level):
	# print "Getting " + str(comp_level) + " match keys for " + str(team)
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

def parse_firebase_unicode(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(parse_firebase_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(parse_firebase_unicode, data))
    else:
        return data

def end_of_match(event, team):

	data = parse_firebase_unicode(fb.get(event + "/teams/" + team, None))
	real_data = data["matches"]["qm"]

	for i in ["Auto-Baseline","Auto-Fuel-High-Cycles","Auto-Fuel-Intake-Hopper","Auto-Fuel-Low-Cycles","Auto-Gears","Auto-Gears-Dropped","Auto-Gears-Intake-Ground","Auto-Robot-Broke-Down","Auto-Robot-No-Action","End-Defense","End-Defense-Rating","End-Fuel-Ground-Intake","End-Fuel-Ground-Intake-Rating","End-Gear-Ground-Intake","End-Gear-Ground-Intake-Rating","End-No-Show","End-Takeoff","End-Takeoff-Speed","Tele-Fuel-High-Cycles","Tele-Fuel-High-Cycles-In-Key","Tele-Fuel-High-Cycles-Out-Of-Key","Tele-Fuel-Intake-Hopper","Tele-Fuel-Intake-Loading-Station","Tele-Fuel-Low-Cycles","Tele-Fuel-Low-Cycles-Times","Tele-Gears-Cycles","Tele-Gears-Dropped","Tele-Gears-Intake-Dropped","Tele-Gears-Intake-Ground","Tele-Gears-Intake-Loading-Station","Tele-Gears-Position-Boiler","Tele-Gears-Position-Loading","Tele-Gears-Position-Middle","Tele-Robot-Broke-Down","Tele-Robot-No-Action"]:
		upload_team_stat(event, team, i+"-Average", get_stat_average_per_match(event, team, i, real_data))

	for i in ["Tele-Fuel-High-Cycles-Times", "Tele-Gears-Cycles-Times"]:
		upload_team_stat(event, team, i+"-Average", get_stat_average_cycle_time(event, team, i, real_data))


def get_stat_average_per_match(event, team, stat, real_data):

	total = 0
	num = 0

	for i in real_data.keys():

		if real_data[i][stat] == "" or real_data[i][stat] == "-1":
			continue

		total += float(real_data[i][stat])
		num += 1

	return total/num if num != 0 else 0

def get_stat_average_cycle_time(event, team, stat, real_data):

	total = 0
	num = 0

	for i in real_data.keys():
		collected = [k for k in real_data[i][stat].split(";")[:-1] if k!= ""]
		total += sum([float(k) for k in collected])
		num+=len(collected)


	return total/num if num != 0 else 0
