from flask import Flask, jsonify, request

import sys
import json
import urllib2

import firebase_interactor as fb
import slack_interactor as slack
import tba_interactor as tba

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
	result['query']['matches'] = {i.key : {"blue" : i.blue_alliance.teams, "red" : i.red_alliance.teams} for i in matches}
	return jsonify(result)


@app.route('/<string:auth>/error')
def error(auth):
	issue = request.headers['issue']

	status = slack.send_message("*ISSUE REPORTED*: " + issue)

	if status == "ok":
		return jsonify({"report": "success"})
	else:
		return jsonify({"report": "failed"})

@app.route('/<string:auth>/upload_data'):
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

# Start Flask
if __name__ == '__main__':
	fb.authenticate(firebase_secret)
	app.run(host='0.0.0.0', debug=True)
