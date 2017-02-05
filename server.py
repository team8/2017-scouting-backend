from flask import Flask, jsonify, request

import sys
import traceback
import json
import urllib2

import firebase_interactor as fb
import slack_interactor as slack
import tba_interactor as tba

from subprocess import call

"""
Used to catch Python exceptions.  This doesn't catch Flask exceptions because of
http://bugs.python.org/issue1230540.
"""
def exception_handling(exctype, val, data):
	# Log it
	print "Encountered a Python-Based (non-Flask) error {}.  Value: {}.  Full Traceback: {}".format(exctype, val, data)
	# Send us a slack notification
	slack.send_message("Encountered an exception of type `{}`.  The value printed was `{}`.  A full traceback is below. \n\n ```{}```".format(exctype, val, data))

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

	result = {'query' : {'success' : 'yes'}}
	teams = tba.get_teams(event)
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

@app.route('/<string:auth>/upload_data')
def upload_data(auth):
	data_elements = request.headers['data'] # Expects the header to be a JSON array
	data = json.loads(data_elements)

	try:
		event = data["event"]
		team = data["team"]
		comp_level = data["comp_level"]
		matchNumber = data["match_number"]
		for k,v in data:
			if k not in ["event", "team", "comp_leve", "match_number"]:
				fb.upload_timd_stat(event, team, comp_level, matchNumber, k, v)

		return jsonify({"status": "success"})
        except Exception:
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
