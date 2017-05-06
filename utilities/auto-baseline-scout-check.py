import json

firebase_data = json.loads(open("svr-data.json").read())

mistakes = {}

for i in firebase_data["teams"].keys():

	specific_data = firebase_data["teams"][i]["timd"]["qm"]

	for k in specific_data.keys():
		timd = firebase_data["teams"][i]["timd"]["qm"][k]

		if int(firebase_data["teams"][i]["timd"]["qm"][k]["Auto-Gears"]) + int(firebase_data["teams"][i]["timd"]["qm"][k]["Auto-Gears-Failed"]) > 0 and int(firebase_data["teams"][i]["timd"]["qm"][k]["Auto-Baseline"]) == 0:
			messed_up_person = firebase_data["teams"][i]["timd"]["qm"][k]["Name"]
			print "AUTO BASELINE MESSED UP IN QM #{} TEAM #{} BY {}.".format(k, i,firebase_data["teams"][i]["timd"]["qm"][k]["Name"])
			if messed_up_person in mistakes:
				mistakes[messed_up_person] += 1
			else:
				mistakes[messed_up_person] = 1

for i in mistakes.keys():
	print str(i) + " MESSED UP " + str(mistakes[i]) + " TIMES "
