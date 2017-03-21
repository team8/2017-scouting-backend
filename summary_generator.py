from __future__ import division
import requests
import json

import tba_interactor as tba
import firebase_interactor as fb

import math

fb.authenticate("vOeDTTJx9eX6S8G29bgq3BJPvogEdmW6KbMDssPK")

EVENT = "2017cave"

sentence = """*In the upcoming match, Paly Robotics is on the {0} alliance.*"""

team_sentence = """{0} is currently ranked #{1} with {2} *RP*, and they are focused on {3}.  
The team scores {4} gears and {5} *fuel per match*.  They have climbed in {6} out of {7} matches and their overall OPR is {8}. 
""".replace("{", "*{").replace("}", "}*").replace("\n", "") + "\n\n"


data_about_us = """
\nOur team is composed of team {0}, team {1}, and team {2}.  
"""

match_suggestions = """Here are the ( :world_class_team: ) match suggestions:
We expect that our alliance will be scoring approximately {0} rotors.  Along with this, there will probably be {1} climb(s) based off of previous performances.  This combines for an expected score, discluding auto, of {2}.  As for the other alliance, 
they would be classified as a statistically {3} alliance. To counter them, we {4} have a robot playing defense {5}.  Due to the
drivetrain types, the teams that will be easy to defend are {6}.  You should be defending the robot with the fastest cycle time primarily, which 
is team #{7}.
""".replace("{", "*{").replace("}", "}*")


tags_at_the_end = """\n Tags: <@rselwyn>, <@atarng>, <@atong>\n"""

def send_message(data, channel="#match-bot-dev", icon=":chart_with_upwards_trend:", name="Pre-Match Scouting"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon, }
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})
	print (payload)
	return results.text

def format_team(team_number):
	team_text = "Team " + str(team_number)
	try:
		overall_rank = tba.get_event_ranking(EVENT).get_ranking(team_number)
		rps = int(tba.get_event_ranking(EVENT).get_total_rp(team_number))
	except:
		overall_rank = 0
		rps = 0

	try:
		opr = tba.get_opr(EVENT, team_number)
		total_plays = tba.get_event_ranking(EVENT).get_num_matches(team_number)
	except:
		opr = 0
		total_plays = 0

	average_scales = int(float(fb.get_team_stat(EVENT, team_number, "End-Takeoff-Average").encode('ascii','ignore')) * total_plays)

	average_gears = float(fb.get_team_stat(EVENT, team_number, "Tele-Gears-Cycles-Average"))

	average_shooting = 0

	strategy = ""
	if average_shooting>10: # More than only shooting in auto
		strategy += "shooting"

		if average_gears > 2.5: # Score at least 2 to 3 gears per match
			strategy += "+gearing"
	else:

		if average_gears > 2.5:
			strategy += "gearing"
		else:
			strategy += "not clear"

	return team_sentence.format(team_text, overall_rank, rps, strategy, average_gears, average_shooting, average_scales, total_plays, opr)

def decide_our_strategy(opponents, our_team):

	gearing_scores = [float(fb.get_team_stat(EVENT, i, "Tele-Gears-Cycles-Average")) for i in opponents]

	total_gears = sum(gearing_scores)
	rotors, extras, percent_dist_to_next_gear = calc_prospective_rotors(total_gears)

	should_play_defense = 0

	# TODO: Use stddev to further determine if they will score the gears
	if percent_dist_to_next_gear > .7:
		should_play_defense += 5 * percent_dist_to_next_gear

	if extras == 1:
		should_play_defense += 10


	return "No Strategy For Now"



def calc_prospective_rotors(gears):
	gears += 1 # Reserve gears

	left_over_gears = 0
	gears_to_next_rotor = 1
	max_ = 0
	
	if gears == 1:
		left_over_gears = 0
		max_ = 1
	if gears >= 3:
		left_over_gears = gears - 3
		gears_to_next_rotor = 6 - gears
		max_ = 2
	if gears >= 6:
		left_over_gears = gears - 6
		gears_to_next_rotor = 10 - gears
		max_ = 3
	if gears >= 10:
		left_over_gears = gears - 10
		gears_to_next_rotor = 100 # Hacky, but will work for now.  This will make the code think that there is no chance the team will get another gear, which is true
		max_ = 4

	return max_, left_over_gears, left_over_gears/(left_over_gears + gears_to_next_rotor)

def get_match():
	matches = tba.get_matches_with_teams(EVENT)

	for i in matches:
		if i.summary_generator_match():
			return i.get_red(), i.get_blue(), i.get_team8_alliance()

def construct_message():

	our_color = ""

	match = get_match()

	our_color = match[2]

	if our_color == "Blue":
		our_alliance = match[1]
		their_alliance = match[0]
	else:
		our_alliance = match[0]
		their_alliance = match[1]

	# our_color = "Blue"
	# our_alliance = ["8", "589","981"]
	# their_alliance = ["1138", "1515", "5818"]


	message = sentence.format(our_color)

	if our_color == "Blue":
		message = ":large_blue_circle: :large_blue_circle: :large_blue_circle: " + message + " :large_blue_circle: :large_blue_circle: :large_blue_circle:\n\n  The :red_circle: :red_circle: :red_circle: alliance is as follows. \n"
	else:
		message = ":red_circle: :red_circle: :red_circle: " + message + " :red_circle: :red_circle: :red_circle:\n\n  The :large_blue_circle: :large_blue_circle: :large_blue_circle: is as follows. \n "



	for i in their_alliance:
		message += format_team(i)

	message += data_about_us.format(our_alliance[0], our_alliance[1], our_alliance[2])
	
	for i in our_alliance:
		message += format_team(i)

	message += decide_our_strategy(their_alliance, our_alliance)
	message += tags_at_the_end
	# send_message(message)
	slack.send_message(message)
	return message
