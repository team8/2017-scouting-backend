from flask import Flask, jsonify, request

import sys
import traceback
import json
import urllib2
import threading

import firebase_interactor as fb
import slack_interactor as slack
import tba_interactor as tba
import summary_generator as summary

from subprocess import call

"""
Used to catch Python exceptions.  This doesn't catch Flask exceptions because of
http://bugs.python.org/issue1230540.
"""
def exception_handling(exctype, val, data):
	# Log it
	print "Encountered a Python-Based (non-Flask) error {}.  Value: {}.  Full Traceback: {}".format(exctype, val, data.format_exc())
	# Send us a slack notification
	slack.send_message("Encountered an exception of type `{}`.  The value printed was `{}`.  A full traceback is below. \n\n ```{}```".format(exctype, val, data.format_exc()))

	call(["python"] + sys.argv) # restart

# This is used to catch Python system based exceptions (not involving Flask).
sys.excepthook = exception_handling

# Constants
comp_levels = ["f", "sf", "qf", "qm"]

# Initialize Flask
app = Flask(__name__)

# Pass the auth file in as an argument
auth_code = open(sys.argv[1]).readlines()[0].strip()
firebase_secret = open(sys.argv[1]).readlines()[1].strip()

# App routes
@app.route('/<string:auth>/test/', methods=['GET'])
def test(auth):
	if auth == auth_code:
		return jsonify({'connection':'success'})
	else:
		return jsonify({'connection':'failed'})

@app.route('/<string:auth>/match/<string:event>')
def match(auth, event):
	if auth != auth_code:
		return jsonify({'query':{'success' : 'no'}})

	result = {'query' : {'success' : 'yes'}}
	matches = tba.get_matches_with_teams(event)
	result['query']['matches'] = {i.key : {"blue" : i.blue_alliance.teams, "red" : i.red_alliance.teams, "score_breakdown" : i.score_breakdown} for i in matches}
	return jsonify(result)

@app.route('/<string:auth>/teams/<string:event>')
def teams(auth, event):
	if auth != auth_code:
		return jsonify({'query':{'success' : 'no'}})

	result = {'query' : {'success' : 'yes', 'teams': {}}}
	teams = tba.get_teams(event)
        rankings = tba.get_rankings(event)
        if rankings != {}:
                for i in teams:
                        if rankings.get(i) != None:
                                result['query']['teams'][i] = {"team_number" : i, "ranking": rankings.get(i)["ranking"], "rankingInfo": rankings.get(i)["rankingInfo"]}
                        else:
                                result['query']['teams'][i] = {"team_number" : i}
        else:
                result['query']['teams'] = {i : {"team_number" : i} for i in teams}
        return jsonify(result)

@app.route('/<string:auth>/error')
def error(auth):
	issue = request.headers['issue']
	status = slack.send_message("*ISSUE REPORTED*: " + issue)

	if status == "ok":
		return jsonify({"report": "success"})
	else:
		return jsonify({"report": "failed"})

@app.route('/prematch/', methods=["POST", "GET"])
def prematch():
	data = dict(request.form)
	url = data['response_url'][0].encode('ascii','ignore')

	summ = summary.construct_message()
	payload = {"channel": "#driveteam-steamworks",
				"username": "Pre-Match Bot", "text": summ,
				"icon_emoji": ":kenny:", "response_type":
				"in_channel","link_names": 1}

	return jsonify(payload)

@app.route('/<string:auth>/upload_data')
def upload_data(auth):
	data_elements = request.headers # Expects the header to be a JSON arrays
	data = data_elements.to_list()

	data = {i[0]:i[1] for i in data}
	print data

	try:
		#event = data["Event"]
                event = "testing"
		team = data["Team-Number"]
                #comp_level = data["Comp-Level"]
                #matchNumber = data["Match-Number"]
                comp_level = "pr"
                matchNumber = 0
                if data["Comp-Level"] == "sf":
                        matchNumber = 5
                elif data["Comp-Level"] == "qf":
                        matchNumber = 2
                else:
                        matchNumber = {
                                "22": 1,
                                "64": 3,
                                "15": 4
                        }.get(data["Match-Number"])
                if matchNumber == None:
                        matchNumber = data["Match-Number"]
                matchIn = data["Match-In"]

		uploadable = {}

		for k in data.keys():
			if k not in ["Event", "Team-Number", "Comp-Level", "Match-Number", "Match-In", "Accept-Encoding", "User-Agent", "Accept", "Accept-Language", "Connection", "Content-Length", "Content-Type", "Host"]:
				uploadable[k] = data[k]

                #if int(uploadable["Auto-Gears"]) > 0:
                #        uploadable["Auto-Baseline"] = "1"

                scouterteam = 0
                for t in ["8", "1339", "4561", "5472", "5499", "6560"]:
                        if t in uploadable["Name"]:
                                scouterteam = t
                if scouterteam == 0:
                        scouterteam = 8
                message = ""
                test_passed = True
                answerkey = fb.get("testing/teams/" + str(team) + "/timd/" + comp_level, matchNumber)
                #print answerkey
                if answerkey is None:
                        message = "Error: No answer key for this match-team pair (Team " + str(team) + " in Match " + str(matchNumber) + ")"
                        slack.send_test_results1(message, channel="#squadron-" + str(scouterteam))
                        slack.send_test_results2(message, channel="#scouting-cmp2017")
                        return jsonify({"status": "success"})
                for k in uploadable.keys():
                        if k not in ["End-Notes", "End-Defense-Rating", "End-Fuel-Ground-Intake-Rating", "End-Gear-Ground-Intake-Rating", "Name", "Tele-Fuel-High-Cycles-Times", "Tele-Gears-Cycles-Times", "Tele-Fuel-Low-Cycles-Times", "End-Driver-Rating", "End-Takeoff-Speed", "End-Defense"]:
                                if uploadable[k] != answerkey[k]:
                                        test_passed = False
                                        if k in ["Auto-Gears", "Auto-Baseline", "End-Takeoff"]:
                                                message += "\n*" + k + " - Answered: " + uploadable[k] + ", Correct: " + answerkey[k] + "*"
                                        else:
                                                message += "\n" + k + " - Answered: " + uploadable[k] + ", Correct: " + answerkey[k]
                if test_passed == True:
                        message = uploadable["Name"] + " (Team " + str(scouterteam) + ") has passed match " + str(matchNumber) + " (Team " + str(team) + ") of the practical test! Congratulations!"
                else:
                        message = uploadable["Name"] + " (Team " + str(scouterteam) + ") has failed match " + str(matchNumber) + " (Team " + str(team) + ") of the practical test. Incorrect reponses:" + message
                slack.send_test_results1(message, channel="#squadron-" + str(scouterteam))
                slack.send_test_results2(message, channel="#scouting-cmp2017")
                #fb.upload_timd_stat(event, team, comp_level, matchNumber, uploadable)
		print "Uploaded"

		#newEndOfmatchThread = threading.Thread(target=fb.end_of_match, args=(event, team))
		#newEndOfmatchThread.start()

		return jsonify({"status": "success"})
	except Exception, e:
		raise e
		return jsonify({"status": "errored"})

@app.route('/<string:auth>/upload_pit_data')
def upload_pit_data(auth):
	data_elements = request.headers # Expects the header to be a JSON arrays
	data = data_elements.to_list()

	data = {i[0]:i[1] for i in data}
	print data
	try:
		event = data["Event"]
		#event = "2017cave"
		team = data["Team-Number"]
		#comp_level = data["Comp-Level"]
		#matchNumber = data["Match-Number"]
                #matchIn = data["Match-In"]
		for k in data.keys():
			if k not in ["Event", "Team-Number", "Accept-Encoding", "User-Agent", "Accept", "Accept-Language", "Connection", "Content-Length", "Content-Type", "Host"]:
				print k
				fb.upload_pit_stat(event, team, k, data[k])

		return jsonify({"status": "success"})
	except Exception, e:
		raise e
		return jsonify({"status": "errored"})


@app.errorhandler(Exception)
def handle_error(e):
	data = traceback.format_exc()
	print "Encountered a Flask-Based error {}.  Value: {}.  Full Traceback: {}".format(type(e).__name__, str(e), data)

	slack.send_message("Encountered a flask exception of type `{}`.  The value printed was `{}`.  A full traceback is below. \n\n ```{}```".format(type(e).__name__, str(e), data))

	return jsonify({"status": "error"})

# Start Flask
if __name__ == '__main__':
	fb.authenticate(firebase_secret)
	app.run(host='0.0.0.0', debug=True)
