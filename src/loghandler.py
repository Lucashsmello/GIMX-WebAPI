import logging
import logging.handlers
import flask
from flask_restful import Resource
import os
import zipfile
from io import BytesIO

def zipdir(path, ziph):
	# ziph is zipfile handle
	for root, dirs, files in os.walk(path):
		for f in files:
			ziph.write(os.path.join(root, f),os.path.join('log',f))


class LogResource(Resource):
	def get(self):
		global LOG_FILE,INSTALL_LOG_FILE,LOG_DIR
		if('zipped' in flask.request.args):
			mem_zip = BytesIO()
			with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
				zipdir(LOG_DIR,zf)
			mem_zip.seek(0)
			R=flask.send_file(mem_zip, as_attachment=True, attachment_filename='gimxweb-log.zip',mimetype='application/zip',cache_timeout=4)
			R.direct_passthrough=False
			return R
		with open(LOG_FILE,'r') as f:
			d1=f.read()
		with open(INSTALL_LOG_FILE,'r') as f:
			d2=f.read()
		return {'web':d1, 'install':d2}


def configureLogger(log_dir,app):
	global LOG_FILE, INSTALL_LOG_FILE, LOGGER, INSTALL_LOGGER,LOG_DIR
	if(not os.path.isdir(log_dir)):
		os.mkdir(log_dir)
	LOG_DIR=log_dir
	LOG_FILE=os.path.join(log_dir,"gimx_webapi.log")
	INSTALL_LOG_FILE=os.path.join(log_dir,"gimx_webapi_install.log")
	app.logger.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', "%Y-%m-%d %H:%M:%S")
	# create logger
	LOGGER = logging.getLogger('gimx_webapi')
	LOGGER.setLevel(logging.DEBUG)
	h = logging.handlers.RotatingFileHandler(LOG_FILE,maxBytes=200000,backupCount=1)
	h.setLevel(logging.INFO)
	h.setFormatter(formatter)
	LOGGER.addHandler(h)

	app.logger.handlers=[h]

	h = logging.StreamHandler()
	h.setLevel(logging.INFO)
	h.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
	LOGGER.addHandler(h)


	INSTALL_LOGGER = logging.getLogger('gimx_webapi_install')
	INSTALL_LOGGER.setLevel(logging.DEBUG)
	h = logging.handlers.RotatingFileHandler(INSTALL_LOG_FILE,maxBytes=200000,backupCount=1)
	h.setLevel(logging.INFO)
	h.setFormatter(formatter)
	INSTALL_LOGGER.addHandler(h)
