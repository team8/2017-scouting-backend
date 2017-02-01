# Scouting Backend

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
