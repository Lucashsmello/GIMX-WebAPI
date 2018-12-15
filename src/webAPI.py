import flask
from flask import Flask
import flask_restful #pip install flask-restful
from flask_restful import Resource
import gimxAPI
from gimxAPI import *
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = flask_restful.Api(app)

APPDATA_DIR=os.path.expanduser('~')+"/.gimx-web"
LAST_OPTS_FILE=os.path.join(APPDATA_DIR,"last_opts")
#UPLOAD_FOLDER=os.path.join(APPDATA_DIR,"uploads")
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
		if 'get_output' in flask.request.args:
			if(flask.request.args['get_output'].lower()=='true'):
				(msg,err)=getGimxOutput()
				return {'status_code':status_code, 'messages':msg, 'error_messages':err}
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
	ALLOWED_EXTENSIONS = set(['xml'])
	def __init__(self):
		self.confdir=getGimxUserConfigFilesDir()

	def allowed_file(self,filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in GimxConfigFiles.ALLOWED_EXTENSIONS

	def get(self, name=None):
		if(name is None):
			xmllist=[f for f in os.listdir(self.confdir) if f.endswith(".xml")]
			return {'conf_files':xmllist}
		with open(os.path.join(self.confdir,name),'rb') as f:
			data=io.BytesIO(f.read())
			return flask.send_file(data, as_attachment=True, attachment_filename=name)

	def post(self):
		global app
		# check if the post request has the file part
		if 'file' not in flask.request.files:
		    return {'return_code':1, 'message':'No file uploaded'}
		if 'overwrite' in flask.request.form:
			overwrite_enabled = flask.request.form['overwrite'].lower()=='true'
		else:
			overwrite_enabled = False
		f = flask.request.files['file']
		if f.filename == '':
		    return {'return_code':1, 'message':'No file uploaded'}
		filename = secure_filename(f.filename)
		if f and not self.allowed_file(filename):
			return {'return_code':2, 'message':'File name "%s" not allowed' % filename}
		file_exists=os.path.isfile(os.path.join(self.confdir,f.filename))
		if(not overwrite_enabled):
			if file_exists:
				return {'return_code':3, 'message':'File already exists'}
			
		#f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		f.save(os.path.join(self.confdir,filename))
		return {'return_code':0}


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

