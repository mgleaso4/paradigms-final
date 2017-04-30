
#!/usr/bin/env python3
# Maddie Gleason and Ben Gunning
# PyGame + Twisted Final Project

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue

class GameConnection(Protocol):
	def __init__(self):
		self.queue = DeferredQueue()
	def startForward(self):
		self.queue.get().addCallback(self.forwardData)
	def connectionMade(self):
		return
	def dataReceived(self, data):
		return
	def forwardData(self, data):
		self.transport.write(data)
		self.queue.get().addCallback(self.forwardData)

class GameConnectionFactory(Factory):
	def __init__(self):
		self.gameconn = GameConnection()
	def buildProtocol(self, addr):
		return self.gameconn
