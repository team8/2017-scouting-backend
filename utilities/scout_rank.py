import urllib2
import json
import math

def get_matches_with_teams():
	"""
	Method that will return a list of TBAMatch
	"""
	f = open("raw_tba.json")
	jsonvar = json.loads(f.read())

	return_val = []
	for i in jsonvar:
		# print i
		if "score_breakdown" in i and i["score_breakdown"] != None:
			return_val.append(FullTBAMatch(i))

	return return_val

			
class Alliance:
	def __init__(self, team1, team2, team3):
		self.teams = [team1, team2, team3]
		self.teams = [a.encode('ascii','ignore') for a in self.teams]

	def get_teams(self):
		return self.teams

	def as_string(self):
		return " ".join(self.teams)

	def as_csv_string(self):
		return ",".join(self.teams)
	
class FullTBAMatch(object):
	def __init__(self, match_dict):
		self.real_data = match_dict
		self.key = match_dict["key"].encode('ascii', 'ignore')
		self.level = match_dict["comp_level"]
		self.match_num = match_dict["match_number"]
		
		self.blue_alliance_performance = match_dict["score_breakdown"]["blue"]
		self.red_alliance_performance = match_dict["score_breakdown"]["red"]
		self.red = Alliance(match_dict["alliances"]["red"]["teams"][0],
							match_dict["alliances"]["red"]["teams"][1],
							match_dict["alliances"]["red"]["teams"][2])

		self.blue = Alliance(match_dict["alliances"]["blue"]["teams"][0],
							match_dict["alliances"]["blue"]["teams"][1],
							match_dict["alliances"]["blue"]["teams"][2])

		self.blue_rotors = match_dict["score_breakdown"]["blue"]["rotor1Engaged"] + match_dict["score_breakdown"]["blue"]["rotor2Engaged"] + match_dict["score_breakdown"]["blue"]["rotor3Engaged"] + match_dict["score_breakdown"]["blue"]["rotor4Engaged"]
		self.red_rotors = match_dict["score_breakdown"]["red"]["rotor1Engaged"] + match_dict["score_breakdown"]["red"]["rotor2Engaged"] + match_dict["score_breakdown"]["red"]["rotor3Engaged"] + match_dict["score_breakdown"]["red"]["rotor4Engaged"]

		self.blue_climbs = match_dict["score_breakdown"]["blue"]["touchpadFar"] + match_dict["score_breakdown"]["blue"]["touchpadMiddle"] + match_dict["score_breakdown"]["blue"]["touchpadNear"]
		self.red_climbs = match_dict["score_breakdown"]["red"]["touchpadFar"] + match_dict["score_breakdown"]["red"]["touchpadMiddle"] + match_dict["score_breakdown"]["red"]["touchpadNear"] 
		self.blue_climbs = self.blue_climbs.count("Ready")
		self.red_climbs = self.red_climbs.count("Ready")

	def get_blue_rotors(self):
		return self.blue_rotors

	def get_red_rotors(self):
		return self.red_rotors

	def get_red_climbs(self):
		return self.red_climbs

	def get_blue_climbs(self):
		return self.blue_climbs

	def get_key(self):
		return self.key

	def get_level(self):
		return self.level

	def get_key_as_displayable(self):
		display = self.key.split("_")[1]

		if display[0:2] == "qm":
			return display.split("qm")[1]
		else:
			return display

	def get_red_alliance(self):
		return self.red

	def get_blue_alliance(self):
		return self.blue

	def get_winner(self):
		if self.blue_alliance_performance["totalPoints"] > self.red_alliance_performance["totalPoints"]:
			return "blue"
		if self.blue_alliance_performance["totalPoints"] < self.red_alliance_performance["totalPoints"]:
			return "red"
		return "tie"

	def get_blue_total(self):
		return self.blue_alliance_performance["totalPoints"]

	def get_red_total(self):
		return self.red_alliance_performance["totalPoints"]

	def get_blue_teleop_points(self):
		return self.blue_alliance_performance["teleopPoints"]

	def get_red_teleop_points(self):
		return self.red_alliance_performance["teleopPoints"]

	def get_blue_auto_points(self):
		return self.blue_alliance_performance["autoPoints"]

	def get_red_auto_points(self):
		return self.red_alliance_performance["autoPoints"]

	def get_blue_winning_margin(self):
		return self.blue_alliance_performance["totalPoints"] - self.red_alliance_performance["totalPoints"]

	def get_red_winning_margin(self):
		return self.red_alliance_performance["totalPoints"] - self.blue_alliance_performance["totalPoints"]

def gears_to_rotors(gears):
	retVal = 1
	if gears >= 1:
		retVal = 1
	if gears >= 3:
		retVal = 2
	if gears >= 6:
		retVal = 3
	if gears >= 12:
		retVal = 4

	return retVal

firebase_data = json.loads(open("svr-data.json").read())


print len(get_matches_with_teams())

for match in get_matches_with_teams():

	should_be_red = match.get_red_rotors()
	should_be_blue = match.get_blue_rotors()

	actual_gears_red = 0
	actual_gears_blue = 0

	name_string_red = ""
	name_string_blue = ""

	for i in match.get_red_alliance().get_teams():

		if match.get_key_as_displayable() in firebase_data["teams"][i[3:]]["timd"]["qm"]:
			actual_gears_red += int(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Tele-Gears-Cycles"])
			actual_gears_red += int(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Auto-Gears"])
			# actual_gears_red += 1
			name_string_red += str(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Name"] + ",")
		else:
			actual_gears_red = - (1 << 10)

	for i in match.get_blue_alliance().get_teams():

		if match.get_key_as_displayable() in firebase_data["teams"][i[3:]]["timd"]["qm"]:
			actual_gears_blue += int(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Tele-Gears-Cycles"])
			actual_gears_blue += int(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Auto-Gears"])
			# actual_gears_blue += 1
			name_string_blue += str(firebase_data["teams"][i[3:]]["timd"]["qm"][match.get_key_as_displayable()]["Name"] + ",")
		else:
			actual_gears_blue = - (1 << 10)

	if actual_gears_red < 0:
		print "Could not check QM #{0} RED.  Data Incomplete".format(match.get_key_as_displayable())
	else:

		if gears_to_rotors(actual_gears_red) != should_be_red:
			print "Incorrect Data for QM #{0}.  Red Alliance had {1} in reality, but it was scouted as {2}.  Scouters: {3}".format(match.get_key_as_displayable(), should_be_red, gears_to_rotors((actual_gears_red)), name_string_red )
		else:
			print "Correct Data for QM #{0}".format(match.get_key_as_displayable())

	if actual_gears_blue < 0:
		print "Could not check QM #{0} BLUE.  Data Incomplete".format(match.get_key_as_displayable())
	else:

		if gears_to_rotors(actual_gears_blue) != should_be_blue:
			print "Incorrect Data for QM #{0}.  Blue Alliance had {1} in reality, but it was scouted as {2}. Scouters: {3}".format(match.get_key_as_displayable(), should_be_blue, gears_to_rotors((actual_gears_blue)), name_string_blue)
		else:
			print "Correct Data for QM #{0}".format(match.get_key_as_displayable())