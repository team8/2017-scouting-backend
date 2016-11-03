import requests
import json

def get_matches_with_teams(eventKey):
	"""
	Method that will return a list of TBAMatch 
	"""
	route = "/event/" + eventKey + "/matches"
	jsonvar = get_data(route)

	return_val = []
	for i in jsonvar:
		return_val.append(TBAMatch(i))

	return return_val

def get_data(route):
	url = "http://www.thebluealliance.com/api/v2" + route
	request = requests.get(url, headers={'X-TBA-App_Id': 'frc8:scouting:pre-alpha'})
	jsonvar = request.json()

	return jsonvar

class Alliance:
	def __init__(self, team1, team2, team3):
		self.teams = [team1, team2, team3]
		self.teams = [a.encode('ascii','ignore') for a in self.teams]

	def get_teams(self):
		return self.teams

class TBAMatch(object):

	def __init__(self, match_dict):
		self.comp_level = match_dict["comp_level"]
		self.match_number = match_dict["match_number"]
		self.key = match_dict["key"]
		self.blue_alliance = Alliance(match_dict["alliances"]["blue"]["teams"][0], 
									  match_dict["alliances"]["blue"]["teams"][1], 
									  match_dict["alliances"]["blue"]["teams"][2])
		self.red_alliance = Alliance(match_dict["alliances"]["red"]["teams"][0], 
									  match_dict["alliances"]["red"]["teams"][1], 
									  match_dict["alliances"]["red"]["teams"][2])