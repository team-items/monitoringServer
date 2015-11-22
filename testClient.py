#First Party Libraries
import sys
import socket
import json
import time


CONFIG = '{"ConnREQ" : {"HardwareType" : "Smartphone","SupportedCrypto" : ["AES128", "RSA512"],"PreferredCrypto" : "None","SupportedDT" : ["Bool", "String", "Integer", "Slider", "Button"]}}'

def multiReceive(client):
	finished = False;
	jsonMsg = None;
	msg = client.recv(2048).decode("utf-8");

	if not msg:
		return False;
	while not finished:
		try:
			jsonMsg = json.loads(msg);

			finished = True;
		except ValueError:
			msg = msg+client.recv(2048).decode("utf-8");

			if not msg:
				return False;
	return jsonMsg;

def testClient():


	host = 'localhost'
	port = 62626
	size = 2048
	s = None
	crypto = None

	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		s.connect((host, port)) 
	except socket.error: 
		
		if s: 
		    s.close() 
		    print("Could not open socket: ", sys.exc_info()[1])
		    sys.exit(1)


	handshakeSucceeded = False
	s.send(CONFIG.encode())
	
	time.sleep(0.005)

	respStream = s.recv(2048)

	if respStream:
		print(respStream.decode("utf8"))
		response = json.loads(respStream.decode('utf8'))
		
		if ("ConnACK" in response.keys()):
			print("ConnACK message")
			ack = response["ConnACK"]

			if ("ChosenCrypto" in ack.keys()):
				crypto = ack["ChosenCrypto"]
			else:
				print("Missing ChosenCrypto in ConnACK using default: none")

			time.sleep(0.005)
			respStream = multiReceive(s)

			if respStream:
				lao = respStream
				print("LAO Received")
				handshakeSucceeded = True

				s.send('{ "ConnSTT" : "" }'.encode('utf8'));
				print("ConnSTT sent")
				while True:
					print("receiving")
					data = s.recv(2048);
					print("received")
					print(data.decode('utf8'));
					time.sleep(0.005);
			else:
				print("No answer from server");

		elif ("ConnREJ" in response.keys()):
			rej = response["ConnREJ"]

			if ("Error" in rej.keys()):
				print(rej["Error"]);
			else:
				print("Missing Error in ConnREJ")

		else:
			print("No response from the server")

	else:
		print("No answer from the server")
		
	if (handshakeSucceeded):
		print("Handshake succeeded");
		print(host)
		print(port)
		print(size)
		print(crypto)

	s.close()

testClient()
