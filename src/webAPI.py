import flask
from flask import Flask
import flask_restful #pip install flask-restful
from flask_restful import Resource
import gimxAPI
from gimxAPI import isGimxInitialized, isGimxRunningOK, startGimx, stopGimx
import os

app = Flask(__name__)
api = flask_restful.Api(app)

APPDATA_DIR=os.path.expanduser('~')+"/.gimx-web/"
LAST_OPTS_FILE=APPDATA_DIR+"last_opts"

class GimxStatus(Resource):
	"""
	Gives info about gimx process status. 
	"""
	def get(self):
		status_code=0
		if(isGimxRunningOK()):
			status_code=1
		elif(isGimxInitialized()):
			status_code=2
		else:
			status_code=0
		return {'status_code':status_code}

def handleGimxStart(opts):
	global APPDATA_DIR,LAST_OPTS_FILE
	if(isGimxInitialized()):
		return 1
	if(startGimx(opts.split())==False):
		return 2
	if(not os.path.isdir(APPDATA_DIR)):
		os.mkdir(APPDATA_DIR)
	try:
		with open(LAST_OPTS_FILE,'w') as f:
			f.write(opts)
	except IOError:
		print 'could not write used options in a file!'
	return 0


class GimxStart(Resource):
	def post(self):
		opts=flask.request.form['options'] #TODO: Schema for options
		retcode=handleGimxStart(opts)
		msg=""
		if(retcode==2):
			msg="Unable to start GIMX!"
		elif(retcode==1):
			msg="GIMX is already initialized!"

		if(msg==""):
			return {'return_code':retcode}
		return {'return_code':retcode, 'message':msg}

class GimxStop(Resource):
	def get(self):
		self.post()

	def post(self):
		msg=""
		try:
			if(stopGimx()):
				retcode=0
			else:
				retcode=1
				msg="Unable to stop GIMX!"
		except gimxAPI.DeviceNotFound as ex:
			msg=str(ex)
			retcode=2
		return {'return_code':retcode, 'message':msg}


api.add_resource(GimxStatus,'/gimx/api/v1/status')
api.add_resource(GimxStart,'/gimx/api/v1/start')
api.add_resource(GimxStop,'/gimx/api/v1/stop')

app.run(host='0.0.0.0', port=80, debug=True) 

