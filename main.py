#!/usr/bin/env python

import sys 
import socket 
import time 

#Own Libraries
from lib import *

server = None 

print("MissionControl Server (MIDaC V1)\n") 

log = Logger("eventlog.log") 
conf = ConfigHandler("config.conf", log) 

log.logAndPrintMessage("Setting up server") 

#Create Socket
try:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	server.bind((conf.HOST, conf.PORT)) 
	server.listen(conf.BACKLOG) 
except socket.error:
	if server:
		server.close() 
	log.logAndPrintError("Could not open socket: "+`sys.exc_info()[1]`) 
	sys.exit() 

#Create RSAL object, launch RSAL as subprocess and connect
rsal = RS(conf, log)
rsal.connect()

log.logAndPrintSuccess("RSAL Connected!") 
log.logAndPrintSuccess("Server running!") 

#Create client manager
clients = ClientManager(server, log, conf, rsal.LAO) 
log.logAndPrintSuccess("Client Manager started!") 

running = True 
#main loop
while running:
	try:
		#run select on all clients
		clients.update() 
		#perform handshake operations with clients that are in handshake
		clients.handleHandshake() 
		
		#receive input from connnected clients and send it to rsal
		control = clients.handleInput() 
		if control != None:
			rsal.handleOutput(control) 

		#receive input from rsal and send it to all ready connected clients
		data = rsal.handleInput() 
		if data != None:
			clients.handleOutput(data) 

		#wait for steprate time
		time.sleep(conf.SAMPLERATE) 
	except KeyboardInterrupt:
		server.close() 
		rsal.rsalProcss.terminate() 
		log.logAndPrintWarning("Server manually stopped") 
		sys.exit() 
	except:
		server.close() 
		rsal.rsalProcss.terminate() 
		log.logAndPrintError("Unexpected Exception. Server stopped") 
		sys.exit() 

