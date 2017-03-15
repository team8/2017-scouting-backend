import requests
import json

import tba_interactor as tba
import firebase_interactor as fb

if __name__ == '__main__':
	fb.authenticate("vOeDTTJx9eX6S8G29bgq3BJPvogEdmW6KbMDssPK")

EVENT = "2017ctwat"

sentence = """*In the upcoming match, Paly Robotics is playing the {0} alliance that is made up of {1}, {2}, and {3}.*\n"""

team_sentence = """{0} is a currently ranked #{1} with {2} *RP*, and they are focused on {3}.  
The team scores {4} gears and {5} *fuel per match*.  They have climbed in {6} out of {7} matches and their overall OPR is {8}.
""".replace("{", "*{").replace("}", "}*").replace("\n", "") + "\n\n"

match_suggestions = """Here are the ( :world_class_team: ) match suggestions:

We expect that our alliance will be scoring approximately {0} rotors.  Along with this, there will probably be {1} climb(s) based off of previous performances.  This combines for an expected score, discluding auto, of {2}.  As for the other alliance, they would be classified as a statistically {3} alliance.
To counter them, we  {4} have a robot playing defense.  {5}.
""".replace("{", "*{").replace("}", "}*")

tags_at_the_end = """\n Tags: @rselwyn, @atarng, @atong, @driveteam"""

def send_message(data, channel="#match-bot-dev", icon=":chart_with_upwards_trend:", name="Pre-Match Scouting"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon, "link_names": 1}
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})
	print (payload)
	return results.text

def format_team(team_number):
	team_text = "Team " + str(team_number)
	overall_rank = tba.get_event_ranking(EVENT).get_ranking(team_number)
	rps = int(tba.get_event_ranking(EVENT).get_total_rp(team_number))

	total_plays = tba.get_event_ranking(EVENT).get_num_matches(team_number)
	average_scales = int(fb.get_team_stat(EVENT, team_number, "End-Takeoff-Average") * total_plays)

	average_gears = float(fb.get_team_stat(EVENT, team_number, "Tele-Gears-Cycles-Average"))

	average_shooting = "Alex Calculate This"

	opr = tba.get_opr(EVENT, team_number)

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

def construct_message():
	message = sentence.format("red","254","971","1678") 
	message += format_team("558")
	# message += team_sentence.format("Team 254", "1", "12", "gears+shooting", "100", "12", "175", "6","7")
	message += team_sentence.format("Team 971", "2", "11", "gears+shooting", "99", "11", "174", "6","7")
	message += team_sentence.format("Team 1678", "3", "10", "gears+shooting", "98", "10", "173", "6","7")
	message += match_suggestions.format("3", "3", "some number", "strong", "should", "That should be team 8.")
	message += tags_at_the_end
	send_message(message)

	

construct_message()