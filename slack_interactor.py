import requests
import json

def send_message(data, channel="#scouting-app", icon=":exclamation:", name="Scouting Issue Bot"):
	payload = {"channel": channel, "username": name,"text": data, "icon_emoji": icon}
	results = requests.post("https://hooks.slack.com/services/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", json.dumps(payload), headers={'content-type': 'application/json'})

	return results.text
