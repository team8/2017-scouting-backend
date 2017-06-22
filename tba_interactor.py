import requests
import json
from collections import defaultdict
import collections
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_matches_with_teams(eventKey):
	"""
	Method that will return a list of TBAMatch 
	"""
	route = "/event/" + eventKey + "/matches"
	jsonvar = get_data(route)

	jsonvar = parse_unicode(jsonvar)

	return_val = []
	for i in jsonvar:
                #if i.get("match_number") <= 99:
                return_val.append(TBAMatch(i))

	return return_val

def get_teams(eventKey):
       	route = "/event/" + eventKey + "/teams"
        jsonvar = get_data(route)
        return_val = []
        for i in jsonvar:
                return_val.append(i["team_number"])
        
        return return_val

def get_match(matchKey):
        route = "/match/" + matchKey
        jsonvar = get_data(route)
        return jsonvar

def get_team_alliance(event, team, comp_level, match):
        match = get_match(str(event) + "_" + str(comp_level) + str(match))
        if match.get("alliances") is None:
                print match
                return None
        if "frc" + str(team) in match["alliances"]["red"]["teams"]:
                return "red"
        elif "frc" + str(team) in match["alliances"]["blue"]["teams"]:
                return "blue"
        else:
                return None

def get_rankings(eventKey):
        route = "/event/" + eventKey + "/rankings"
        jsonvar = get_data(route)

        return_val = {}
        for i in jsonvar:
                if i[0] != "Rank":
                        rp = i[2] * i[9]
                        return_val[i[1]] = {"ranking": i[0], "rankingInfo": "RP: " + str(int(round(rp))) + " | " + str(i[8]) + " (W-L-T) | Played: " + str(i[9])}
        
        return return_val

def get_fuel_in_match(eventKey, match_key, alliance, fuel_key):
	route = "/match/" + eventKey + "_" + match_key
	jsonvar = get_data(route)
	score_breakdown = jsonvar.get("score_breakdown")
	if (score_breakdown is not None):
		return score_breakdown[alliance][fuel_key]
	return 0

def get_defensible_score(eventKey, match_key, alliance):
	route = "/match/" + eventKey + "_" + match_key
	jsonvar = get_data(route)
	score_breakdown = jsonvar.get("score_breakdown")
	if (score_breakdown != None):
		return score_breakdown[alliance]["teleopPoints"] - score_breakdown[alliance]["teleopTakeoffPoints"] + score_breakdown[alliance]["foulPoints"]
	return None

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
		

		self.score_breakdown = match_dict.get("score_breakdown")
		self.has_played = self.score_breakdown != None
		self.has_team8 = "8" in self.blue_alliance.get_teams() or "8" in self.red_alliance.get_teams()
		self.alliance_with_team8 = "Blue" if "8" in self.blue_alliance.get_teams() else "Red"
    

	def summary_generator_match(self):
		return self.has8 and not self.has_been_played

	def get_team8_alliance(self):
		return self.alliance_with_team8

	def get_red(self):
		return self.red_alliance.get_teams()

	def get_blue(self):
		return self.blue_alliance.get_teams()

class TBAQualRanking(object):
	def __init__(self, qual_ranking_array):
		self.qual_ranking_array = qual_ranking_array
		self.data = defaultdict(dict)

		for team in qual_ranking_array[1:]:
			for position in range(len(team)):
				self.data[str(team[1])][qual_ranking_array[0][position]] = team[position]

		self.data = dict(self.data)

	def get_ranking(self, team):
		return self.data[team]["Rank"]

	def get_record(self, team):
		return self.data[team]["Record (W-L-T)"]

	def get_total_rp(self, team):
		return float(self.data[team]["Played"]) * float(self.data[team]["Ranking Score"])

	def get_num_matches(self, team):
		return float(self.data[team]["Played"])

def get_event_ranking(eventid):
	"""
	Method that will 
	return ranking data for an event
	"""
	route = "/event/" + eventid + "/rankings"
	data = get_data(route)

	return TBAQualRanking(data)

def parse_unicode(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(parse_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(parse_unicode, data))
    else:
        return data

def get_opr(eventid, team):
	route = "/event/" + eventid + "/stats"
	data = get_data(route)
	data = parse_unicode(data)


	return data["oprs"][team]
