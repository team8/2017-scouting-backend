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

@app.route('/teamdata/', methods=["POST", "GET"])
def teamdata():
	data = dict(request.form)
	# url = data['response_url'][0].encode('ascii','ignore')
	team = str(data["text"]).strip("[").strip("]").strip("\'")[2:]
	print len(team)
	message = fb.get("/2017cave/teams/" + team, None)

	print team

	payload = {"channel": "#match-bot-dev",
				"username": "Pre-Match Bot", "text": message,
				"icon_emoji": ":kenny:", "response_type":
				"in_channel","link_names": 1}

	print payload
	slack.send_message(message, channel="#match-bot-dev")

	return jsonify(payload)

@app.route('/<string:auth>/upload_data')
def upload_data(auth):
	if auth != auth_code:
		return jsonify({'query':{'success' : 'no'}})

	data_elements = request.headers # Expects the header to be a JSON arrays
	data = data_elements.to_list()

	data = {i[0]:i[1] for i in data}
	print data

	try:
		event = data["Event"]
		team = data["Team-Number"]
		comp_level = data["Comp-Level"]
		matchNumber = data["Match-Number"]
		matchIn = data["Match-In"]

		uploadable = {}

		for k in data.keys():
			if k not in ["Event", "Team-Number", "Comp-Level", "Match-Number", "Match-In", "Accept-Encoding", "User-Agent", "Accept", "Accept-Language", "Connection", "Content-Length", "Content-Type", "Host"]:
				uploadable[k] = data[k]

                if int(uploadable["Auto-Gears"]) > 0:
                        uploadable["Auto-Baseline"] = "1"
                        
		fb.upload_timd_stat(event, team, comp_level, matchNumber, uploadable)
        
		fb.upload_timd_stat(event, team, comp_level, "test", "test") # weird error causing the first match to not be interpreted as a dictionary

		print "Uploaded"
		print event
                
		newEndOfmatchThread = threading.Thread(target=fb.end_of_match, args=(event, team))
		newEndOfmatchThread.start() # start the calculations in a new thread so that the user doesn't wait

		return jsonify({"status": "success"})
	except Exception, e:
		raise e
		return jsonify({"status": "errored"})

@app.route('/<string:auth>/upload_pit_data')
def upload_pit_data(auth):
	if auth != auth_code:
		return jsonify({'query':{'success' : 'no'}})

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
