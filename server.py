import requests as pyReq

from flask import Flask, jsonify

import flask

import sys
import TBAconnection
import firebase
import json
import firebasecustomauth
import urllib2



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
	matches = TBAconnection.get_matches_with_teams(event)
	result['query']['matches'] = {i.key : {"blue" : i.blue_alliance.teams, "red" : i.red_alliance.teams} for i in matches}
	return jsonify(result)


@app.route('/<string:auth>/error')
def error(auth):
	issue = flask.request.headers['issue']

	payload = {"channel":"#scouting-app","username":"Scouting Issue Bot","text":"*ISSUE REPORTED*: " + issue,"icon_emoji":":exclamation:"}
	results = pyReq.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})

	print results.url
	print results

	print results.text

	if results.text == "ok":
		return jsonify({"report": "success"})
	else:
		return jsonify({"report": "failed"})

# Initialize Firebase
authentication = firebase.FirebaseAuthentication(firebase_secret, "scouting@palyrobotics.com", extra={"id": "server"})
firebase = firebase.FirebaseApplication("https://scouting-2017.firebaseio.com/", authentication=authentication)

# Firebase basics
def get_team_matches(event, team, comp_level):
	print "Getting " + str(comp_level) + " match keys for " + str(team)
	matches = []
	matches_raw = firebase.get(str(event) + "/teams/" + str(team)  + "/matches/" + comp_level, None)
	if matches_raw != None:
		try:
			for match in matches_raw.keys():
				matches.append(match)
		except AttributeError:
			for i in range(0, len(matches_raw)):
				if matches_raw[i] != None:
					matches.append(i)
	else:
		return None
	return matches

def upload_timd_stat(event, team, comp_level, match_number, stat, value):
	print "Uploading TIMD stat: " + str(team) + " - " + str(stat) + ": " + str(value) + " in " + str(comp_level) + str(match_number)
	firebase.put(str(event) + "/teams/" + str(team) + "/matches/" + str(comp_level) + "/" + str(match_number), stat, value)

def get_timd_stat(event, team, comp_level, match_number, stat):
	print "Getting TIMD stat: " + str(team) + "'s " + str(stat) + " in " + str(comp_level) + str(match_number)
	return firebase.get(str(event) + "/teams/" + str(team) + "/matches/" + str(comp_level) + "/" + str(match_number), stat)

def upload_team_stat(event, team, stat, value):
	print "Uploading team stat: " + str(team) + " - " + str(stat) + ": " + str(value)
	firebase.put(str(event) + "/teams/" + str(team) + "/stats/", stat, value)

def get_team_stat(event, team, stat):
	print "Getting team stat: " + str(team) + "'s " + str(stat)
	return firebase.get(str(event) + "/teams/" + str(team) + "/stats/", stat)

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
		

# Firebase test
@app.route('/<string:auth>/fbtest/', methods=['GET'])
def fbtest(auth):
	from datetime import datetime
	start = datetime.now()
	upload_timd_stat("2017cave" , "frc8", "qm", "1", "high_goals_scored", 100)
	upload_timd_stat("2017cave" , "frc8", "qm", "2", "high_goals_scored", 200)
	upload_timd_stat("2017cave" , "frc8", "qm", "3", "high_goals_scored", 300)
	upload_timd_stat("2017cave" , "frc8", "qm", "4", "high_goals_scored", 400)
	upload_team_stat("2017cave" , "frc8", "high_goals_scored_avg", calc_timd_average("2017cave" , "frc8", "high_goals_scored"))
	upload_team_stat("2017cave" , "frc8", "high_goals_scored_sd", calc_timd_stddev("2017cave" , "frc8", "high_goals_scored"))
	retval = str(calc_timd_average("2017cave", "frc8", "high_goals_scored")) + ", " + str(calc_timd_stddev("2017cave", "frc8", "high_goals_scored"))
	print (datetime.now() - start)
	return retval

# Start Flask
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)