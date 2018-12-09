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

class DeviceNotFound(Exception):
	pass

def isGimxInitialized():
	checkDefunctProcess()
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == GIMX_EXEC:
			return True
	return False

def isGimxRunningOK():
	if(isGimxInitialized()==False):
		return False
	if(GIMX_PROC is None):
		return False

	#FIXME
	if(os.path.isfile("/tmp/gimx-output")):
		with open("/tmp/gimx-output",'r') as f:
			for line in f:
				if('error' in line.lower()):
					return False

	return True

def startGimx(opts):
	global GIMX_PROC,GIMX_STARTED_OK
	#subprocess.call([GIMX_EXEC]+opts)
	GIMX_STARTED_OK=False
	#GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts,stderr=PIPE)
	with open("/tmp/gimx-output",'w') as outfile:
		GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts, stderr=outfile)
	
	time.sleep(2)
	return isGimxRunningOK()

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
	global GIMX_PROC
	if(GIMX_PROC is None):
		return
	if(GIMX_PROC.poll() is None):
		return
	print "GIMX terminated with return code: "+str(GIMX_PROC.returncode)
	open("/tmp/gimx-output",'w').close()
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
