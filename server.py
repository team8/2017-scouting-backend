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

# Firebase calculations
def calc_timd_average(event, team, stat):
	print "Calculating TIMD average for " + str(team) + "'s " + str(stat)
	num_matches = 0
	stat_total = 0
	for comp_level in comp_levels:
		matches = get_team_matches(event, team, comp_level)
		if matches != None:
			for match in matches:
				timd_stat = get_timd_stat(event, team, comp_level, match, stat)
				if timd_stat != None:
					stat_total += timd_stat
				num_matches += 1
	if num_matches != 0:
		average = float(stat_total)/float(num_matches)
	else:
		average = 0
	return average

def calc_timd_stddev(event, team, stat):
	print "Calculating TIMD standard deviation for " + str(team) + "'s " + str(stat)
	average = calc_timd_average(event, team, stat)
	num_matches = 0
	stat_total = 0
	for comp_level in comp_levels:
		matches = get_team_matches(event, team, comp_level)
		if matches != None:
			matches = get_team_matches(event, team, comp_level)
			for match in matches:
				timd_stat = get_timd_stat(event, team, comp_level, match, stat)
				if timd_stat != None:
					stat_total += (timd_stat - average) ** 2
				num_matches += 1
	if num_matches != 0:
		stddev = (float(stat_total)/float(num_matches)) ** 0.5
	else:
		stddev = 0
	return stddev
		


# Start Flask
if __name__ == '__main__':
	fb.authenticate(firebase_secret)
	app.run(host='0.0.0.0', debug=True)