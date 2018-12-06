import os
import psutil # pip install psutil
import subprocess

import time
#import uinput #pip install python-uinput; modprobe uinput
from evdev import uinput, ecodes as e
import evdev

GIMX_EXEC="gimx"
GIMX_PROC=None


class DeviceNotFound(Exception):
	pass

def isGimxRunning():
	checkDefunctProcess()
	for pid in psutil.pids():
		p = psutil.Process(pid)
		if p.name() == GIMX_EXEC:
			return True
	return False

def startGimx(opts):
	global GIMX_PROC
	#subprocess.call([GIMX_EXEC]+opts)
	GIMX_PROC = subprocess.Popen([GIMX_EXEC]+opts)
	for _ in range(4):
		time.sleep(0.5)
		if(isGimxRunning()):
			return True
	return False

def openKeyboardDevice(): #TODO: open all keyboard devices.
	devs=[evdev.InputDevice(fn) for fn in evdev.list_devices()]
	ret=None
	for d in devs:
		#print d.name
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

	"""
	from pynput.keyboard import Key, Controller # pip install pynput	
	keyboard = Controller()
	with keyboard.pressed(Key.shift):
		keyboard.press(Key.esc)
	"""
	time.sleep(1)
	return not isGimxRunning()

#print stopGimx()
#print startGimx("-p /dev/ttyUSB0 --config Overwatch_lmello.xml --force-updates --refresh 5 --curses --window-events".split())
