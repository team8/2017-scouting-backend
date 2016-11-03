from flask import Flask, jsonify
import sys
import TBAconnection

app = Flask(__name__)
# Pass the auth file in as an argument
auth_code = open(sys.argv[1]).readlines()[0].strip()

@app.route('/test/<string:auth>', methods=['GET'])
def test(auth):
    if auth == auth_code:
    	return jsonify({'connection':'success'})
    else:
    	return jsonify({'connection':'failed'})

@app.route('/match/<string:auth>/<string:event>')
def match(auth, event):
	if auth != auth_code:
		return jsonify({'query':{'success' : 'no'}})

	result = {'query' : {'success' : 'yes'}}
	matches = TBAconnection.get_matches_with_teams(event)
	result['query']['matches'] = {i.comp_level + str(i.match_number) : {"blue" : i.blue_alliance.teams, "red" : i.red_alliance.teams} for i in matches}
	return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)