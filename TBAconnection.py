import urllib2
import json

def get_matches_with_teams(eventKey):
	"""
	Method that will return a list of TBAMatch 
	"""
	url = "http://www.thebluealliance.com/api/v2/event/" + eventKey + "/matches" + '?X-TBA-App-Id=frc8%3Ascouting%3Apre-alpha'
	request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'})
	data = urllib2.urlopen(request).read().decode('utf-8')
	jsonvar = json.loads(data)

	retern_val = []
	for i in jsonvar:
		return_val.append(TBAMatch(i))

	return return_val


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