import socket
from sys import argv
from time import sleep
from threading import Thread

DOLISTEN=True
UDP_PORT=51915

def unregisterService():
	global DOLISTEN
	DOLISTEN=False

def sendHIMessage(address,responseMessage=None):
	global UDP_PORT
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	if(address=='<broadcast>'):
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	if(responseMessage is None):
		sock.sendto("megimxservice", (address, UDP_PORT))
	else:
		sock.sendto("megimxservice:%s" % str(responseMessage), (address, UDP_PORT))
	sock.close()

def listenBroadCast(responseMessage=None):
	global DOLISTEN,UDP_PORT
	DOLISTEN=True
	
	sendHIMessage('<broadcast>')
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(("", UDP_PORT))
	while DOLISTEN:
		data, addr = client.recvfrom(1024)
		#print("received message from %s: %s" % (addr,data))
		if(data=="whoGIMXAPISERVICE"):
			sendHIMessage(addr[0],responseMessage)
	client.close()

def registerService(responseMessage=None):
	T = Thread(target=listenBroadCast, args=(responseMessage,))
	T.daemon=True
	T.start()

if __name__=="__main__":
	listenBroadCast()

#try:
#    while True:
#        sleep(0.1)
#except KeyboardInterrupt:
#    pass
#finally:
    

