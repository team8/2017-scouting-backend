from flask import Flask, jsonify
import sys

app = Flask(__name__)
# Pass the auth file in as an argument
auth_code = open(sys.argv[1]).readlines()[0].strip()

@app.route('/test/<string:auth>', methods=['GET'])
def index(auth):
    if auth == auth_code:
    	return jsonify({'connection':'success'})
    else:
    	return jsonify({'connection':'failed'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)