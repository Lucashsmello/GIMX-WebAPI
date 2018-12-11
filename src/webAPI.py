import flask
from flask import Flask
import flask_restful #pip install flask-restful
from flask_restful import Resource
import gimxAPI
from gimxAPI import *
import os
import io

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

class GimxConfigFiles(Resource):
	def __init__(self):
		self.confdir=getGimxUserConfigFilesDir()

	def get(self, name=None):
		if(name is None):
			xmllist=[f for f in os.listdir(self.confdir) if f.endswith(".xml")]
			return {'conf_files':xmllist}
		with open(os.path.join(self.confdir,name),'rb') as f:
			data=io.BytesIO(f.read())
			return flask.send_file(data, attachment_filename=name)

def GimxAddResource(api,res,route1,route2=None):
	GIMX_API_VERSION=1
	R1='/gimx/api/v%d/%s' % (GIMX_API_VERSION, route1)
	if(route2 is None):
		api.add_resource(res,R1)
		return
	R2='/gimx/api/v%d/%s' % (GIMX_API_VERSION, route2)
	api.add_resource(res,R1,R2)

GimxAddResource(api,GimxStatus,'status')
GimxAddResource(api,GimxStart,'start')
GimxAddResource(api,GimxStop,'stop')
GimxAddResource(api,GimxConfigFiles,'configfile','configfile/<string:name>')

app.run(host='0.0.0.0', port=80, debug=True) 

