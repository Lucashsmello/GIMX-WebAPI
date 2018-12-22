import os
import psutil # pip install psutil
import subprocess
from subprocess import PIPE

import time
#import uinput #pip install python-uinput; modprobe uinput
from evdev import uinput, ecodes as e
import evdev
#from threading import Thread

GIMX_EXEC="gimx"
GIMX_PROC=None

GIMX_STDERR_FILE="/tmp/gimx-stderr"
GIMX_STDOUT_FILE="/tmp/gimx-stdout"

class DeviceNotFound(Exception):
	pass


def getGimxUserDataDir():
	return os.path.expanduser('~')+"/.gimx"

def getGimxUserConfigFilesDir():
	return os.path.join(getGimxUserDataDir(),"config")

def isGimxInitialized():
	checkDefunctProcess()
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == GIMX_EXEC:
			return True
	return False



def isGimxRunningOK():
	global GIMX_STDERR_FILE
	if(isGimxInitialized()==False):
		return False
	if(GIMX_PROC is None):
		return False

	#FIXME: make error verification better.
	if(os.path.isfile(GIMX_STDERR_FILE)):
		with open(GIMX_STDERR_FILE,'r') as f:
			for line in f:
				if('error' in line.lower()):
					return False

	return True


def getGimxOutput():
	global GIMX_STDOUT_FILE,GIMX_STDERR_FILE
	out1=""
	outerror=""
	if(os.path.isfile(GIMX_STDOUT_FILE)):
		with open(GIMX_STDOUT_FILE,'r') as f: 
			out1=f.read()
	if(os.path.isfile(GIMX_STDERR_FILE)):
		with open(GIMX_STDERR_FILE,'r') as f: 
			outerror=f.read()

	return (out1,outerror)	

def startGimx(opts,wait=2):
	global GIMX_PROC,GIMX_STARTED_OK,GIMX_STDOUT_FILE,GIMX_STDERR_FILE
	#subprocess.call([GIMX_EXEC]+opts)
	GIMX_STARTED_OK=False
	#GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts,stderr=PIPE)
	with open(GIMX_STDERR_FILE,'w') as ferror, open(GIMX_STDOUT_FILE,'w') as fout:
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
