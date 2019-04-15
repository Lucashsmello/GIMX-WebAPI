import socket
from sys import argv
from time import sleep
from threading import Thread
import logging

LOGGER=logging.getLogger('gimx_webapi')
DOLISTEN=True
UDP_PORT=51915

def unregisterService():
	global DOLISTEN
	DOLISTEN=False

def sendHIMessage(address,responseMessage=None):
	global UDP_PORT
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	try:
		if(address=='<broadcast>'):
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			address='255.255.255.255' #'<broadcast>' is not translated properly sometimes. We should do it manually.
		if(responseMessage is None):
			sock.sendto(b"megimxservice", (address, UDP_PORT))
		else:
			msg="megimxservice:%s" % str(responseMessage)
			sock.sendto(msg.encode('utf-8'), (address, UDP_PORT))
	except Exception as e:
		LOGGER.error('sendHIMessage("%s","%s"): %s' % (str(address),str(responseMessage),str(e))) 
	sock.close()

def listenBroadCast(responseMessage=None):
	global DOLISTEN,UDP_PORT
	DOLISTEN=True

	sendHIMessage('<broadcast>',responseMessage)
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(("", UDP_PORT))
	while DOLISTEN:
		data, addr = client.recvfrom(1024)
		LOGGER.info("Received message from %s: %s" % (addr,data))
		if(data==b"whoGIMXAPISERVICE"):
			sendHIMessage(addr[0],responseMessage)
	client.close()

def registerService(responseMessage=None):
	T = Thread(target=listenBroadCast, args=(responseMessage,))
	T.daemon=True
	T.start()

if __name__=="__main__":
	listenBroadCast()

