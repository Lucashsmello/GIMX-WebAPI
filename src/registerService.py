import socket
from sys import argv
from time import sleep
from threading import Thread

DOLISTEN=True

def unregisterService():
	global DOLISTEN
	DOLISTEN=False

def listenBroadCast():
	global DOLISTEN
	DOLISTEN=True
	UDP_PORT=51915
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(("", UDP_PORT))
	while DOLISTEN:
		data, addr = client.recvfrom(1024)
		#print("received message from %s: %s" % (addr,data))
		if(data=="whoGIMXAPISERVICE"):
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("megimxservice", (addr[0], UDP_PORT))
	client.close()

def registerService():
	T = Thread(target=listenBroadCast)
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
    

