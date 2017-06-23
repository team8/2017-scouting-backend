import requests
import json

def send_message(data, channel="#scouting-app-bot", icon=":exclamation:", name="Scouting Issue Bot"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon}
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})

	return results.text

def send_test_results1(data, channel="#communication", icon=":scouting_app:", name="Automatic Test Grader"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon}
#	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})

	return results.text

def send_test_results2(data, channel="#communication", icon=":scouting_app:", name="Automatic Test Grader"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon}
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})
#	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})
	return results.text
