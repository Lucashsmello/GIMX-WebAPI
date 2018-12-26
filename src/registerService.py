import socket
from sys import argv
from time import sleep


def listenBroadcast():
	UDP_PORT=51915
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(("", UDP_PORT))
	print("Listening...")
	while True:
		data, addr = client.recvfrom(1024)
		print("received message from %s: %s" % (addr,data))
		if(data=="whoGIMXAPISERVICE"):
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("megimxservice", (addr[0], UDP_PORT))
		sleep(0.5)


if __name__=="__main__":
	listenBroadcast()

#try:
#    while True:
#        sleep(0.1)
#except KeyboardInterrupt:
#    pass
#finally:
    

