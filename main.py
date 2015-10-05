#First Party Libraries
import json
import sys
import select
import socket
import base64

#Own Libraries
import Logging
from TurboConf import Config

class MissionControl:
	def __init__(self):
		self.config_path = "config.conf"
		# Config parsing
		config = Config(warnings=True)
		config.add_option("port", default_value=62626)
		config.add_option("samplerate", default_value=0.01)
		config.add_option("host", default_value="")
		config.add_option("backlog", default_value=10)
		try:
			cfg = config.read_config(open(self.config_path, "r").read())
		except IOError:
			raw_config = config.get_config()
			open(self.config_path, "w").write(config.get_config())
			cfg = config.read_config(raw_config)
		self.port = cfg["port"]
		self.samplerate = cfg["samplerate"]
		self.host = cfg["host"]
		self.backlog = cfg["backlog"]
		print(self)
		self.create_server()
	
	def __repr__(self):
		return "Config used: %s\n Port used: %s\n Samplerate used: %s" % (self.config_path, self.port, self.samplerate)


	def create_server(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			server.bind((self.host, self.port))
			server.listen(self.backlog)
			Logging.success("Socket set up")
		except socket.error:
			server.close()
			Logging.error("Could not open socket: %s" % sys.exc_info[1])

		self.input = [server]
		self.output = []

		Logging.success("Finished setting up Server")


	def run(self):
		Logging.success("Server up and running")

		while 1:
			inputready, outputready, exceptready = select.select(self.input, self.output, [])



mc = MissionControl()
mc.run()