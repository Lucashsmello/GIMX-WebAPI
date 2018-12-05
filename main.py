import flask
from flask import Flask, render_template, request, Response, send_from_directory, flash, url_for # pip install flask
from gimxAPI import isGimxRunning, startGimx, stopGimx
import gimxAPI
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dasdinboma'

@app.route("/")
@app.route("/index")
def index():
	if(isGimxRunning()):
		gimxstatus="GIMX is ON"
	else:
		gimxstatus="GIMX is OFF"
	return render_template('control-gimx.html', gimxstatus=gimxstatus)

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
#	return "<link rel=\"shortcut icon\" href=\"{{ url_for('static', filename='favicon.ico') }}\">"

def handleGimxStart(opts):
	if(isGimxRunning()):
		return "GIMX is already running!"
	if(startGimx(opts.split())==False):
		return "Unable to start GIMX!"
	return "GIMX has started!"

@app.route('/start', methods=['GET', 'PUT', 'POST'])
def start():
	msg=""
	if request.method == 'POST':
		opts=request.form['options']
		msg=handleGimxStart(opts)

	if request.method == 'PUT':
		opts=request.args.get('options','')
		msg=handleGimxStart(opts)

	if(not msg): #not empty
		flash(msg)
	return flask.redirect(url_for("/index"))

@app.route('/stop')
def stop():
	msg=""
	try:
		if(stopGimx()):
			msg="GIMX stopped."
		else:
			msg="Unable to stop GIMX!"
	except gimxAPI.DeviceNotFound as ex:
		msg=str(ex)
	flash(msg)
	return flask.redirect(url_for("/index"))

app.run(host='0.0.0.0', port=80) 
