from zeroconf import ServiceInfo, Zeroconf
import socket
from time import sleep
from sys import argv

zeroconf = Zeroconf()
ZINFO = ServiceInfo("_http._tcp.local.",
	               "GIMX API SERVICE._http._tcp.local.",
	               socket.inet_aton("127.0.0.1"), 80, 0, 0,
	               {'path': '/gimx/api/v1/'})

def registerService():
	global zeroconf, ZINFO
	zeroconf.register_service(ZINFO)

def unregisterService():
	global zeroconf, ZINFO
	print("Unregistering...")
	zeroconf.unregister_service(ZINFO)
	zeroconf.close()

if __name__=="__main__":
	if(argv[-1]=='--unregister'):
		unregisterService()
	elif(argv[-1]=='--register'):
		registerService()
	else:
		print("Must specify --register or --unregister")

#try:
#    while True:
#        sleep(0.1)
#except KeyboardInterrupt:
#    pass
#finally:
    

