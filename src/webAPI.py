import flask
from flask import Flask, Response,request
import flask_restful #pip install flask-restful
from flask_restful import Resource
import gimxAPI
from gimxAPI import *
import os
import io
from werkzeug.utils import secure_filename
from registerService import registerService, unregisterService
from threading import Thread
from time import sleep
from sys import argv
import subprocess
import logging
import logging.handlers
from waitress import serve

app = Flask(__name__)
api = flask_restful.Api(app)

APPDATA_DIR=os.path.expanduser('~')+"/.gimx-web"
LAST_OPTS_FILE=os.path.join(APPDATA_DIR,"last_opts")
GIMX_API_VERSION=1
with open('../version.txt','r') as f:
	VERSION=f.read().strip('\n').strip()
REPOSITORY_NAME_W="Lucashsmello/GIMX-WebAPI"
REPOSITORY_NAME_GIMX="matlo/GIMX"
#UPLOAD_FOLDER=os.path.join(APPDATA_DIR,"uploads")
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def configureLogger():
	global LOGGER,app
	# create logger
	LOGGER = logging.getLogger('gimx_webapi')
	LOGGER.setLevel(logging.DEBUG)

	h = logging.handlers.RotatingFileHandler('../log/gimx_webapi.log',maxBytes=330000,backupCount=2)
	h.setLevel(logging.INFO)

	# create formatter
	formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', "%Y-%m-%d %H:%M:%S")
	h.setFormatter(formatter)
	LOGGER.addHandler(h)
	app.logger.setLevel(logging.INFO)
	app.logger.handlers=[h]

	h = logging.StreamHandler()
	h.setLevel(logging.DEBUG)
	h.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
	LOGGER.addHandler(h)

@app.before_request
def pre_request_logging():
	if(len(request.values)==0):
		#request.remote_addr
		msg=[request.method,request.url]
	else:
		vals=', '.join(['%s:%s' % (str(key),str(request.values[key])) for key in request.values])
		vals='{'+vals+'}'
		msg=[request.method,request.url,vals]
	app.logger.info('\t'.join(msg))
		#', '.join([': '.join(x) for x in request.headers])]))

@app.after_request
def after_request_logging(response):
	app.logger.info(('%s response: ' % str(request.url_rule)) + response.status + ', ' + response.data.decode('utf-8'))
	return response

def getLastUsedOptions():
	opts=None
	try:
		if(os.path.isfile(LAST_OPTS_FILE)):
			with open(LAST_OPTS_FILE) as f:
				opts=f.readline()
	except IOError:
		LOGGER.warning("getLastUsedOptions() failed!")
		return None
	return opts


def getVersion():
	global VERSION
	return {"gimxWebAPI-version":VERSION, "gimx-version":getGimxVersion()[0]}

def compareVersions(V1,V2):
	"""
	V1 and V2 types can be str and/or a list of integers. Ex: compareVersions("7.10",[7,9])
	
	returns positive integer if V1 is newer;
	returns 0 if V1 and V2 are equal;
	returns negative integer if V2 is newer.
	"""
	if(type(V1) is str):
		V1=[int(v) for v in V1.split('.')]
	if(type(V2) is str):
		V2=[int(v) for v in V2.split('.')]
	
	for l,r in zip(V1,V2):
		if(l>r):
			return 1
		if(r>l):
			return -1
	return 0


@app.route("/gimx/api/v%d/streamStatus" % GIMX_API_VERSION)
def observeStatus():
	def eventStream():
		last_status=-1
		while True:
			cur_status=getGimxStatus()
			if(cur_status!=last_status):
				yield ("data: %d\n\n" % cur_status)
			last_status=cur_status
			sleep(0.5)
	R=Response(eventStream(), mimetype="text/event-stream")
	R.headers["HTTP/1.1 200 OK"] = "HTTP/1.1 200 OK"
	R.headers['Content-Type'] = 'text/event-stream'
	return R

class GimxStatus(Resource):
	"""
	Gives info about gimx process status.
	"""
	def get(self):
		"""
		Response
			status_code (int):
				0: No gimx process exists;
				1: Gimx is initialized but not fully working yet.
				2: if is running and working normally;
			messages (string): GIMX stdout. (Exists only if parameter get_output="true")
			error_messages (string): GIMX stderr. (Exists only if parameter get_output="true")
		"""
		status_code=getGimxStatus()
		ret={'status_code':status_code}
#		if(status_code==0):
#			ret['gimx_error_code
		if 'get_output' in flask.request.args:
			if(flask.request.args['get_output'].lower()=='true'):
				(msg,err)=getGimxOutput()
				ret['messages']=msg
				ret['error_messages']=err
		return ret

def handleGimxStart(opts,wait_sec=None):
	global APPDATA_DIR,LAST_OPTS_FILE
	if(isGimxInitialized()):
		return 1
	if(startGimx(opts.split(),wait_sec)==False):
		return 2
	if(not os.path.isdir(APPDATA_DIR)):
		os.mkdir(APPDATA_DIR)
	try:
		with open(LAST_OPTS_FILE,'w') as f:
			f.write(opts)
	except IOError:
		LOGGER.warning('could not write used options in a file!')
	return 0


class GimxStart(Resource):
	"""
	Resource responsible for starting gimx process. 
	Starts/Initializes Gimx process by calling gimx command line binary using specified parameters.
	On normal execution, this changes the gimx state from 0 (OFF) to 1 (Initializing). If successfully initialized, then it changes to state 2 (Running).
	Note that normally, after making this request, gimx is not fully running yet.
	You should make polling /status requests until GIMX is fully running or completly goes OFF (an error occurs).
	"""

	def get(self):
		return self.gstart(getLastUsedOptions())

	def post(self):
		"""
		POST params
			options (string): the options used on the gimx command line binary (see [http://gimx.fr/wiki/index.php?title=Command_line]). Example: "options"="-c file_name -p /dev/ttyUSB0"
		
		POST Response
		    return_code (int): returns 0 on success, otherwise:
        		* 1: GIMX is already initialized!
        		* 2: Unable to start GIMX! (And we don't known why)
        		* 3: Missing parameter "options"
    		message (string): If an error occurs, an error message is given here. (Exists only if return_code is not 0).

		"""
		if(not ('options' in flask.request.form)):
			return {'return_code':3, 'message':'Missing parameter "options"'}
		opts=flask.request.form['options'] #TODO: Schema for options
		wait_sec=None
		if('wait_sec' in flask.request.form):
			try:
				wait_sec=int(flask.request.form['wait_sec']) #TODO: Schema for options
			except ValueError:
				return {'return_code':4, 'message':'Invalid value for parameter "wait"'}
		return self.gstart(opts,wait_sec)

	def gstart(self,opts,wait_sec=None):
		retcode=handleGimxStart(opts,wait_sec)
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
		return self.post()

	def post(self):
		"""
		Stops Gimx if it is running. Currently this works by simply making a shift+ESC event.
		
		Response:
    		return_code (int): returns 0 on success.
		"""

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
		"""
		Gets a list of all configuration files. Response have only one value:
		    conf_files (string-list): A list of strings (can be empty) with each xml configuration file.
		"""
		if(name is None):
			xmllist=[f for f in os.listdir(self.confdir) if f.endswith(".xml")]
			return {'conf_files':xmllist}
		with open(os.path.join(self.confdir,name),'rb') as f:
			data=io.BytesIO(f.read())
			return flask.send_file(data, as_attachment=True, attachment_filename=name)

	def post(self):
		"""
		Uploads a configuration file.
		POST Parameters
			file
			overwrite: {true,false} - if true, the file can overwrite an existing one
		"""
		global app
		# check if the post request has the file part
		if 'file' not in flask.request.files:
		    return {'return_code':1, 'message':'No file specified'}
		if 'overwrite' in flask.request.form:
			overwrite_enabled = flask.request.form['overwrite'].lower()=='true'
		else:
			overwrite_enabled = False
		f = flask.request.files['file']
		if f.filename == '':
		    return {'return_code':1, 'message':'No file specified'}
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

class CheckVersion(Resource):
	#SUPPORTED_GIMX_VERSION=[7,10]
	def get(self):
		"""
		Response
			gimxWebAPI-version (string): Version of the Web Server.
			gimx-version (string): GIMX version.
		"""
		global REPOSITORY_NAME_W,REPOSITORY_NAME_GIMX
		myV=getVersion()
		if('check' in flask.request.args):
			lastV=[subprocess.check_output(["../auto_updater/getLatestReleaseNumber.sh",r]).strip('\n').strip().strip('v') for r in (REPOSITORY_NAME_W,REPOSITORY_NAME_GIMX)]
			#needs_update=compareVersions(CheckVersion.SUPPORTED_GIMX_VERSION,lastV[1])==0 and myV["gimx-version"]!=lastV[1]
			myV['needs-update'] = myV["gimxWebAPI-version"]!=lastV[0]
		return myV

class Updater(Resource):
	"""
	Responsible for updating/installing/changing versions.
	"""
	def post(self):
		"""
		POST parameters
			file: must be a .tar.gz file that contains a 'install.sh' script.

		Response
			return_code (int): 0 if no error occurred.
		"""
		try:
			cmd=["./update.sh"]
			if 'file' in flask.request.files:
				f = flask.request.files['file']
				fname=f.filename.strip()
				if(".." in fname or len(fname)==0):
					return {'return_code':-1}
				fout_path='/tmp/%s' % fname
				f.save(fout_path)
				cmd.append(fout_path)
				
			subprocess.check_call(cmd+['../../'], cwd='../auto_updater/')
		except subprocess.CalledProcessError as e:
			LOGGER.error(str(e))
			return {'return_code':e.returncode}
		return {'return_code':0}


class Configurator(Resource):
	def get(self):
		config_params=GetConfigurationParameters()
		return config_params

	def post(self):
		sensibility=-1
		dzx=32767
		dzy=32767
		expx=-1
		expy=-1
		yxratio=-1
		save=False
		fform=flask.request.form
		if 'sensibility' in fform:
			sensibility = float(fform['sensibility'])
		if 'dzx' in fform:
			dzx = int(fform['dzx'])
		if 'dzy' in fform:
			dzy = int(fform['dzy'])
		if 'save' in fform:
			save = fform['save'].lower()=='true'
			if((not save) and fform['save'].lower()!='false'):
				LOGGER.warning('Configurator: invalid value for save "%s"' % fform['save'])
		if 'exp_x' in fform:
			expx = float(fform['exp_x'])
		if 'exp_y' in fform:
			expy = float(fform['exp_y'])
		if 'yx_ratio' in fform:
			yxratio = float(fform['yx_ratio'])

		SetConfigurationParameters(sensibility,dzx,dzy,expx,expy,yxratio)
		if(save):
			saveConfigurationParameters()
		return {'return_code':0}
		


def GimxAddResource(api,res,route1,route2=None):
	global GIMX_API_VERSION
	R1='/gimx/api/v%d/%s' % (GIMX_API_VERSION, route1)
	if(route2 is None):
		api.add_resource(res,R1)
		return
	R2='/gimx/api/v%d/%s' % (GIMX_API_VERSION, route2)
	api.add_resource(res,R1,R2)

if __name__=="__main__":
	configureLogger()
	LOGGER.info("version %s" % VERSION)
	port=80
	if('-p' in argv):
		port=int(argv[argv.index('-p')+1])
	GimxAddResource(api,GimxStatus,'status')
	GimxAddResource(api,GimxStart,'start')
	GimxAddResource(api,GimxStop,'stop')
	GimxAddResource(api,GimxConfigFiles,'configfile','configfile/<string:name>')
	GimxAddResource(api,CheckVersion,'version')
	GimxAddResource(api,Updater,'update')
	GimxAddResource(api,Configurator,'curconfig')
	
	#psutil.net_if_addrs()
	registerService(port)
	serve(app,host="0.0.0.0", port=port)
	#app.run(host="0.0.0.0", port=port, debug=False)  
	unregisterService()

