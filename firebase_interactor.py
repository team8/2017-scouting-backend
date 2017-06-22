from __future__ import division
import firebase
import firebasecustomauth
import collections
import math_implementation as math
import time
import slack_interactor as slack


# Initialize Firebase
fb = None

def authenticate(fb_auth_token):
	authentication = firebase.FirebaseAuthentication(fb_auth_token, "scouting@palyrobotics.com", extra={"id": "server"})
	global fb
	fb = firebase.FirebaseApplication("https://scouting-2017.firebaseio.com/", authentication=authentication)
	
def put(url, key, value):
        fb.put(url, key, value)

def get(url, key):
        return fb.get(url, key)

def delete(url, key):
        fb.delete(url, key)

def get_teams(event):
        print "Getting teams for event " + str(event)
        dict = fb.get(str(event), "teams")
        return dict.keys()

def upload_timd_stat(event, team, comp_level, match_number, stats):
	print "Uploading TIMD stat: " + str(team) + " - " + str(stats) + " in " + str(comp_level) + str(match_number)
	fb.put(str(event) + "/teams/" + str(team) + "/timd/" + str(comp_level), str(match_number), stats)


def upload_pit_stat(event, team, stat, value):
	print "Uploading pit scouting stat: " + str(team) + " - " + str(stat) + ": " + str(value)
	fb.put(str(event) + "/teams/" + str(team) + "/pit", stat, value)

def get_timd_stat(event, team, comp_level, match_number, stat):
	print "Getting TIMD stat: " + str(team) + "'s " + str(stat) + " in " + str(comp_level) + str(match_number)
	return fb.get(str(event) + "/teams/" + str(team) + "/timd/" + str(comp_level) + "/" + str(match_number), stat)

def upload_team_stat(event, team, stat, value):
	print "Uploading team stat: " + str(team) + " - " + str(stat) + ": " + str(value)

	try:
		fb.put(str(event) + "/teams/" + str(team) + "/data/", stat, value)
	except Exception:
		try:
			# wait and try again
			time.sleep(1)
			fb.put(str(event) + "/teams/" + str(team) + "/data/", stat, value)
		except:
			# If it still fails, alert us on slack
			slack.send_message("Unable to upload to stat {}.  Value was {}".format(stat, value))

def get_team_stat(event, team, stat):
	print "Getting team stat: " + str(team) + "'s " + str(stat)
	return fb.get(str(event) + "/teams/" + str(team) + "/data/", stat)

def get_match_stats(event, comp_level, match_number):
	"""
	Returns a dictionary that maps team to data about the match they were in.  The second element is
	the number of teams that have data uploaded.
	"""
	print "Getting match stats for " + str(event) + "_" + str(comp_level) + str(match_number)

	match_stats = fb.get(str(event)+"/teams/", None)
	
	various_timd_map = {}
	match_stats = parse_firebase_unicode(match_stats)
	
	for team in match_stats.keys():
		if match_stats[team].has_key("timd"):
			if match_stats[team]["timd"].has_key(comp_level):
				if match_stats[team]["timd"][comp_level].has_key(match_number):
					various_timd_map[team] = match_stats[team]["timd"][comp_level][match_number]

	return various_timd_map, len(various_timd_map.keys())

def get_comments(event, team):
	match_stats = parse_firebase_unicode(fb.get(str(event) + "/teams/"+team +"/timd/qm" , None))
	lst = []
	for i in match_stats.keys():
		lst.append(i["End-Notes"])

	return lst

# Firebase basics
def get_team_matches(event, team, comp_level):
	print "Getting " + str(comp_level) + " match keys for " + str(team)
	matches = []
	matches_raw = fb.get(str(event) + "/teams/" + str(team)  + "/timd/" + comp_level, None)
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

	real_data = get_real_data(event, team, "qm")

	for i in ["Auto-Fuel-High-Cycles","Auto-Fuel-Low-Cycles","Auto-Gears","Auto-Gears-Intake-Ground","Auto-Robot-Broke-Down","Auto-Robot-No-Action","End-Defense","End-Defense-Rating","End-Fuel-Ground-Intake-Rating","End-Gear-Ground-Intake-Rating","End-Driver-Rating","End-No-Show","End-Takeoff-Speed","Tele-Fuel-High-Cycles","Tele-Fuel-Low-Cycles","Tele-Gears-Cycles","Tele-Gears-Dropped","Tele-Gears-Intake-Dropped","Tele-Gears-Intake-Ground","Tele-Gears-Intake-Loading-Station"]:
		upload_team_stat(event, team, i+"-Average", get_stat_average_per_match(event, team, i, real_data))
		upload_team_stat(event, team, i+"-Stdev", get_stat_std(event, team, i, real_data))

	for i in ["Tele-Fuel-High-Cycles-Times", "Tele-Fuel-Low-Cycles-Times", "Tele-Gears-Cycles-Times"]:
		upload_team_stat(event, team, i+"-Average", get_stat_average_cycle_time(event, team, i, real_data))

	for i in ["Tele-Gears-Cycles"]:
		upload_team_stat(event, team, i+"-Upper-Limit", get_stat_upper_limit(event, team, i, real_data))

	upload_team_stat(event, team, "End-Takeoff-Success-Rate", get_takeoff_success_rate(event, team, real_data))

	for i in ["End-Takeoff","Auto-Baseline","Auto-Gears"]:
		upload_team_stat(event, team, i+"-Achieve-Rate", get_stat_achieve_rate(event, team, i, real_data))

	for i in ["b", "m", "l"]:
		upload_team_stat(event, team, "Auto-Gears-"+i+"-Success-Rate", get_auto_gear_success_rate(event, team, i, real_data))

	for i in ["In-Key", "Out-Of-Key"]:
		upload_team_stat(event, team, "Tele-Fuel-High-"+i+"-Position-Prob", get_tele_fuel_high_position_prob(event, team, i, real_data))

	for i in ["Boiler", "Middle", "Loading"]:
		upload_team_stat(event, team, "Tele-Gears-"+i+"-Position-Prob", get_tele_gear_position_prob(event, team, i, real_data))

	for i in ["i", "o"]:
		upload_team_stat(event, team, "Auto-Fuel-High-"+i+"-Position-Prob", get_auto_fuel_high_position_prob(event, team, i, real_data))

	for i in ["b", "m", "l"]:
		upload_team_stat(event, team, "Auto-Gears-"+i+"-Position-Prob", get_auto_gear_position_prob(event, team, i, real_data))

	for i in ["Tele-Gears-Cycles","Tele-Fuel-High-Cycles","Tele-Fuel-Low-Cycles","End-Defense"]:
		upload_team_stat(event, team, "Strategy-Rate-"+i, get_strategy_rate(event, team, i, real_data))

	upload_team_stat(event, team, "Reliability", get_reliability(event, team, real_data))

	upload_team_stat(event, team, "Loading-Station-Reliability", get_loading_station_reliability(event, team, real_data
))

        upload_team_stat(event, team, "Auto-Gear-Counts", get_gear_counts(event, team, "Auto", real_data))
        upload_team_stat(event, team, "Tele-Gear-Counts", get_gear_counts(event, team, "Tele", real_data))


def get_real_data(event, team, comp_level):
	print "Getting real TIMD data for team " + str(team) + " in " + str(comp_level) + " matches at " + str(event)
	data = parse_firebase_unicode(fb.get(event + "/teams/" + str(team), None))
	real_data = data["timd"][comp_level]
        if real_data.get("test") is not None:
                del real_data["test"]
        return real_data

def get_stat_average_per_match(event, team, stat, real_data):

	total = 0
	num = 0

	for i in real_data.keys():

		if real_data[i][stat] == "" or real_data[i][stat] == "-1":
			continue

		total += float(real_data[i][stat])
		num += 1
                
	return float(total)/float(num) if num != 0 else 0

def get_stat_std(event, team, stat, real_data):
	data = []

	for i in real_data.keys():

		if real_data[i][stat] == "" or real_data[i][stat] == "-1":
			continue

		data.append(float(real_data[i][stat]))
    
	stddev = math.get_std_dev(data)
	if stddev != stddev:
		return 0 # NAN
	else:
		return stddev

def get_stat_average_cycle_time(event, team, stat, real_data):

	total = 0
	num = 0

	for i in real_data.keys():
		collected = [k for k in real_data[i][stat].split(";")[:-1] if k!= ""]
		total += sum([float(k) for k in collected])
		num+=len(collected)


	return float(total)/float(num) if num != 0 else 0

def get_stat_upper_limit(event, team, stat, real_data):

	max = 0

	for i in real_data.keys():
		if float(real_data[i][stat]) > float(max):
			max = float(real_data[i][stat])

	return max

def get_takeoff_success_rate(event, team, real_data):

	attempts = 0
	successes = 0

	for i in real_data.keys():
		if real_data[i]["End-Takeoff"] != "0":
			attempts += 1
			if real_data[i]["End-Takeoff"] == "2":
				successes += 1

        retval = str(round(float(successes)/float(attempts)*100, 2)) + "% (" + str(successes) + " of " + str(attempts) + " attempts)" if attempts != 0 else "0% (0 of 0 attempts)"

	return retval

def get_stat_achieve_rate(event, team, stat, real_data):

	matches = 0
	successes = 0

	for i in real_data.keys():
		matches += 1
		val = float(real_data[i][stat])
		if stat == "End-Takeoff":
			if val == 2:
				successes += 1
		else:
			successes += min(1, val)

        if stat == "End-Takeoff":
                retval = str(round(float(successes)/float(matches)*100, 2)) + "% (" + str(successes) + " of " + str(matches) + " matches)" if matches != 0 else "0% (0 of 0 matches)"
        else:
                retval = round(float(successes)/float(matches), 2) if matches != 0 else 0
                
	return retval

def get_auto_gear_success_rate(event, team, position, real_data):

	total = 0
	successes = 0

	for i in real_data.keys():
		for p in real_data[i]["Auto-Gears-Positions"].split(';'):
			if p == position:
				total += 1
				successes += 1
		for p in real_data[i]["Auto-Gears-Failed-Positions"].split(';'):
			if p == position:
				total += 1

	return float(successes)/float(total) if total != 0 else 0

def get_tele_fuel_high_position_prob(event, team, position, real_data):

	total = 0
	pos = 0

	for i in real_data.keys():
		pos += float(real_data[i]["Tele-Fuel-High-Cycles-" + str(position)])
		total += float(real_data[i]["Tele-Fuel-High-Cycles"])

	return float(pos)/float(total) if total != 0 else 0

def get_tele_gear_position_prob(event, team, position, real_data):

	total = 0
	pos = 0

	for i in real_data.keys():
		pos += float(real_data[i]["Tele-Gears-Position-" + str(position)])
		total += float(real_data[i]["Tele-Gears-Cycles"])

	return float(pos)/float(total) if total != 0 else 0

def get_auto_fuel_high_position_prob(event, team, position, real_data):

	total = 0
	pos = 0

	for i in real_data.keys():
		for p in real_data[i]["Auto-Fuel-High-Positions"].split(';'):
			if p == position:
				pos += 1
		total += float(real_data[i]["Auto-Fuel-High-Cycles"])

	return float(pos)/float(total) if total != 0 else 0

def get_auto_gear_position_prob(event, team, position, real_data):

	total = 0
	pos = 0

	for i in real_data.keys():
		for p in real_data[i]["Auto-Gears-Positions"].split(';'):
			if p == position:
				pos += 1
		total += float(real_data[i]["Auto-Gears"])

	return float(pos)/float(total) if total != 0 else 0

def get_strategy_rate(event, team, stat, real_data):

	matches = 0
	played = 0

	for i in real_data.keys():
		matches += 1
		val = float(real_data[i][stat])
		if val > 0:
			played += 1

	return float(played)/float(matches) if matches != 0 else 0

def get_reliability(event, team, real_data):

	matches = 0
	working = 0

	for i in real_data.keys():
		matches += 1
		if real_data[i]["Tele-Robot-No-Action"] == "0" and real_data[i]["Tele-Robot-Broke-Down"] == "0":
			working += 1

	return float(working)/float(matches) if matches != 0 else 0

def get_loading_station_reliability(event, team, real_data):

	total = 0
	intaken = 0

	for i in real_data.keys():
		intaken_raw = float(real_data[i]["Tele-Gears-Intake-Loading-Station"])
		dropped = float(real_data[i]["Tele-Gears-Intake-Dropped"])
		total += intaken_raw + dropped
		intaken += intaken_raw

	return float(intaken)/float(total) if total != 0 else 0

def get_gear_counts(event, team, period, real_data):

        retval = ""

        for i in real_data.keys():
                if retval != "":
                        retval += ","
                key = period + "-Gears"
                if period == "Tele":
                        key += "-Cycles"
                retval += real_data[i][key]

        return retval

