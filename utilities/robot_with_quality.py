from __future__ import division
import threading
import json

firebase_data = json.loads(open("roe-export-2.json").read())

teams = [3824,4265,2905,624,2655,2478,115,1482,5472,5499,6144,175,6705,6388,3653,4060,2881,973,6304,2485,955,6325,4723,4592,4590,2403,5803,8,6361,365,1011,3991,3834,585,1339,4276,3826,4219,441,2468,4371,4191,2183,4561,3402,488,3158,5515,3316,3140,5970,3229,6508,418,6409,6560,5614,2642,5026,1477,435,1414,1002,5816,1574]

def gearspm(k):
	data = []
	for i in firebase_data["teams"][k]["timd"]["qm"]:
		if firebase_data["teams"][k]["timd"]["qm"][i] == "test":
			continue
		data.append(int(firebase_data["teams"][k]["timd"]["qm"][i]["Tele-Gears-Cycles"]) + int(firebase_data["teams"][k]["timd"]["qm"][i]["Auto-Gears"]))
	return sum(data)/10

def auto_side_peg(k):
	data = []
	for i in firebase_data["teams"][k]["timd"]["qm"]:
		if firebase_data["teams"][k]["timd"]["qm"][i] == "test":
			continue
		data.append("l" in str(firebase_data["teams"][k]["timd"]["qm"][i]["Auto-Gears-Positions"]) or "b" in str(firebase_data["teams"][k]["timd"]["qm"][i]["Auto-Gears-Positions"]))
	return len(filter(lambda i: i, data)) >= 3

def grounde(k):
	data = []
	for i in firebase_data["teams"][k]["timd"]["qm"]:
		if firebase_data["teams"][k]["timd"]["qm"][i] == "test":
			continue
		data.append(int(firebase_data["teams"][k]["timd"]["qm"][i]["Tele-Gears-Intake-Ground"]))
	return sum(data)/len(data) >= 3

def climbe(k):
	data = []
	for i in firebase_data["teams"][k]["timd"]["qm"]:
		if firebase_data["teams"][k]["timd"]["qm"][i] == "test":
			continue
		data.append(int(firebase_data["teams"][k]["timd"]["qm"][i]["End-Takeoff"]))
	return len(filter(lambda i: i == 2, data)) >= 7

print gearspm("8")
print climbe("8")
print auto_side_peg("8")

def generate_list(auto_side, ground, climb):
	results = []

	for i in teams:
		i = str(i)
		can_add = True

		if (ground and ground != grounde(i)):
			# print "CANT ADD {} because ground".format(i)
			can_add = False

		if (auto_side and auto_side != auto_side_peg(i)):
			# print "CANT ADD {} because auto".format(i)
			can_add = False

		if (climb and climb != climbe(i)):
			# print "CANT ADD {} because climb".format(i)
			can_add = False


		if can_add:
			results.append([i, gearspm(i)])

	results.sort(key=lambda i: i[1], reverse=True)

	return results

ground = False
i = "8"
# print not (ground and ground == grounde(i))
print generate_list(False, False, True)


