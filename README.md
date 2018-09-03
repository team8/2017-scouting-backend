# Scouting Backend

Team 8's 2017 Scouting System consists of three parts:
* Viewer App - iPhone app that allows viewing of raw and calculated pit and match scouting data pulled from Firebase, as well as match and ranking data pulled from The Blue Alliance for easy formulating of match strategies and picklists. Also includes QR code scanning for uploading raw match data to the server.
* Collection App - iPad app used by scouters in the stands to collect raw match data and submit it to the server via QR code scanning/uploading.
* Backend Server - Python program constantly running on a private server that receives match data, performs calculations on it, and submits it to Firebase and the viewer app.

# Running the server

Start the server by running

```
python server.py <AUTH-FILE>
```

where `<AUTH-FILE>` is a file with the authentication password on the first line and the Firebase API Key (Secret) on the second line.

# Dependencies

In order to run the server, you need to install the following pip dependencies:

```
pip install flask
pip install python-firebase
```
# Python 2.7.9+

You will need Python 2.7.9+ for `requests` to run properly. The Team 8 dev server runs Ubuntu 14.04, which does not support Python 2.7.7+. Use the link [here](http://mbless.de/blog/2016/01/09/upgrade-to-python-2711-on-ubuntu-1404-lts.html) to set up a virtual environment for running Python 2.7.11 on the dev server.

Create a folder "venv" with Python 2.7.11:
```
virtualenv \
   --python=/usr/local/lib/python2.7.11/bin/python \
   --system-site-packages
   venv
```

Start the virtual environment:
`source venv/bin/activate`
