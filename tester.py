import requests
import json
from collections import defaultdict
import collections

def get_data(route):
	url = "https://www.thebluealliance.com/api/v2" + route
	request = requests.get(url, headers={'X-TBA-App_Id': 'frc8:scouting:pre-alpha'}, verify=False)
	jsonvar = request.json()

	return jsonvar

class Alliance:
	def __init__(self, team1, team2, team3):
		self.teams = [team1, team2, team3]
#		self.teams = [a.encode('ascii','ignore') for a in self.teams]

	def get_teams(self):
		return self.teams

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

class TBAMatch(object):

	def __init__(self, match_dict):
		self.comp_level = match_dict["comp_level"]
		self.match_number = match_dict["match_number"]
		self.key = match_dict["key"]
		self.blue_alliance = Alliance(int(match_dict["alliances"]["blue"]["teams"][0][3:]), 
									  int(match_dict["alliances"]["blue"]["teams"][1][3:]), 
									  int(match_dict["alliances"]["blue"]["teams"][2][3:]))
		self.red_alliance = Alliance(int(match_dict["alliances"]["red"]["teams"][0][3:]), 
									  int(match_dict["alliances"]["red"]["teams"][1][3:]), 
									  int(match_dict["alliances"]["red"]["teams"][2][3:]))
		
		self.has_been_played = False
		self.has_team8 = "8" in self.blue_alliance.get_teams() or "8" in self.red_alliance.get_teams()
		self.alliance_with_team8 = "Blue" if "8" in self.blue_alliance.get_teams() else "Red"
		print match_dict
    
        # self.score_breakdown = match_dict.get("score_breakdown")

	def summary_generator_match(self):
		return self.has8 and not self.has_been_played

	def get_team8_alliance(self):
		return self.alliance_with_team8

	def get_alliances(self):

