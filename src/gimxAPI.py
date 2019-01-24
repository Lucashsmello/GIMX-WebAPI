import os
import psutil # pip install psutil
import subprocess
from subprocess import PIPE

import time
#import uinput #pip install python-uinput; modprobe uinput
from evdev import uinput, ecodes as e
import evdev
import socket

GIMX_EXEC="gimx"
GIMX_PROC=None
GIMX_EXIT_CODE=0

GIMX_STDERR_FILE="/tmp/gimx-stderr"
GIMX_STDOUT_FILE="/tmp/gimx-stdout"

class DeviceNotFound(Exception):
	pass


def getGimxStatus():
	status_code=0
	if(isGimxRunningOK()):
		status_code=2
	elif(isGimxInitialized()):
		status_code=1
	else:
		status_code=0
	return status_code

def getGimxUserDataDir():
	return os.path.expanduser('~')+"/.gimx"

def getGimxUserConfigFilesDir():
	return os.path.join(getGimxUserDataDir(),"config")

def isGimxInitialized():
	checkDefunctProcess()
	for proc in psutil.process_iter(attrs=['name']):
		if proc.info['name'] == GIMX_EXEC:
			return True
	return False

def isGimxRunningOK():
	global GIMX_STDERR_FILE
	if(isGimxInitialized()==False):
		return False
	if(GIMX_PROC is None):
		return False

	dest=("127.0.0.1", 51914)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	ba=bytearray()
	ba.append(0)
	#ba.append(0)
	sock.sendto(ba, dest)
	sock.settimeout(0.5)
	try:
		data, _ =sock.recvfrom(128)
		sock.close()
		return True
	except socket.timeout:
		sock.close()
	
	'''
	if(os.path.isfile(GIMX_STDERR_FILE)):
		with open(GIMX_STDERR_FILE,'r') as f:
			for line in f:
				if('error' in line.lower()):
					return False
	'''
	return False


def getGimxOutput():
	global GIMX_STDOUT_FILE,GIMX_STDERR_FILE
	out1=""
	outerror=""
	if(os.path.isfile(GIMX_STDOUT_FILE)):
		with open(GIMX_STDOUT_FILE,'r') as f: 
			out1=f.read()
	if(os.path.isfile(GIMX_STDERR_FILE)):
		with open(GIMX_STDERR_FILE,'r') as f: 
			outerror=f.read().replace("[01;31m","").replace("[0m","")
	spl=outerror.split('\n')
	outerror="\n".join([spl[0]]+[spl[i] for i in range(1,len(spl)) if spl[i]!=spl[i-1]])
	return (out1,outerror)	

def startGimx(opts,wait=2):
	global GIMX_PROC,GIMX_STDOUT_FILE,GIMX_STDERR_FILE
	opts+=["--src","127.0.0.1:51914"]
	print("Starting gimx with options: %s" % opts) 
	with open(GIMX_STDERR_FILE,'w') as ferror, open(GIMX_STDOUT_FILE,'w') as fout:
		#GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts,stderr=PIPE)
		GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts, stdout=fout, stderr=ferror)

	if(not(wait is None)):	
		if(wait>0):
			time.sleep(wait)
			return isGimxRunningOK()
	return isGimxInitialized()

def openKeyboardDevice(): #TODO: open all keyboard devices.
	devs=[evdev.InputDevice(fn) for fn in evdev.list_devices()]
	ret=None
	for d in devs:
		if(d.name.upper().find("KEYBOARD")>=0):
			if(ret is None):
				ret=d
			elif(int(ret.fn[-1])>int(d.fn[-1])):
				ret.close()
				ret=d
		else:
			d.close()
	#print(ret.fn, ret.name, ret.phys)
	return ret

def checkDefunctProcess():
	global GIMX_PROC,GIMX_STDERR_FILE
	if(GIMX_PROC is None):
		return
	if(GIMX_PROC.poll() is None):
		return
	print("GIMX terminated with return code: "+str(GIMX_PROC.returncode))
	
	GIMX_PROC=None

def stopGimx():
	#ui=evdev.InputDevice('/dev/input/event0')
	ui=openKeyboardDevice()
	if(ui is None):
		raise DeviceNotFound("Keyboard not found.")
	ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
	ui.write(e.EV_KEY, e.KEY_ESC, 1)
	ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
	ui.write(e.EV_KEY, e.KEY_ESC, 0)
	ui.write(e.EV_SYN, e.SYN_REPORT, 0)
	ui.close()

	for _ in range(4):
		time.sleep(0.25)
		if(not isGimxInitialized()):
			return True
	return False

#print stopGimx()
#print startGimx("-p /dev/ttyUSB0 --config Overwatch_lmello.xml --force-updates --refresh 5 --curses --window-events".split())
