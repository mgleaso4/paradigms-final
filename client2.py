#!/usr/bin/env python3
# Maddie Gleason and Ben Gunning
# PyGame + Twisted Final Project

import os, sys, pygame, math, collections, random, queue
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.defer import DeferredQueue
from twisted.python import log
import json

class GameConnectionFactory(ClientFactory):
	def __init__(self):
		self.gameconnection = GameSpace()

	def buildProtocol(self, addr):
		return self.gameconnection

class Fuel(pygame.sprite.Sprite):
	# Initialize Fuel object with Starting Position
	def __init__(self, gs):
		self.gs = gs
		self.food_size = 7
		self.food = pygame.Surface((self.food_size, self.food_size))
		self.rect = self.food.get_rect()
		self.rect.centerx = 320
		self.rect.centery = 240
		self.white = (255,255,255)
		self.extend = 10

	def tick(self):
		# Check for collision between food and snake
		if self.gs.player1.rect.colliderect(self.rect):
			self.gs.player1.tail_len += self.extend
			self.rect.centerx = random.randint(4, 636)
			self.rect.centery = random.randint(4, 476)
		elif self.gs.player2.rect.colliderect(self.rect):
			self.gs.player2.tail_len += self.extend
			self.rect.centerx = random.randint(4, 636)
			self.rect.centery = random.randint(4, 476)

class Player(pygame.sprite.Sprite):
	# Initialize Player with Starting Position
	def __init__(self,gs):
		self.gs = gs
		self.head_size = 7
		self.head = pygame.Surface((self.head_size,self.head_size))
		self.rect = self.head.get_rect()
		self.speed = 2
		self.alive = True
		self.user = True

		# Create Tail to Store Previous Rectangles
		self.tail_len = 25
		self.tail = collections.deque()

	# Change the Direction of the Player
	def move(self,key):
		if key == pygame.K_UP and self.yvel <= 0:
			self.xvel = 0
			self.yvel = -1 * self.speed
		if key == pygame.K_DOWN and self.yvel >= 0:
			self.xvel = 0
			self.yvel = self.speed
		if key == pygame.K_LEFT and self.xvel <= 0:
			self.xvel = -1 * self.speed
			self.yvel = 0
		if key == pygame.K_RIGHT and self.xvel >= 0:
			self.xvel = self.speed
			self.yvel = 0

	def tick(self, opp):
		if self.alive:
		# Update the Player Position
			if self.user:
				self.rect.centerx += self.xvel
				self.rect.centery += self.yvel

				# Add the New Rectangle to the Left of the Tail and Pop the Rightmost Rectangle
				self.tail.appendleft(self.rect.copy())
				while len(self.tail) > self.tail_len:
					self.tail.pop()

				# Send the New Head to the Other Client
				pos = {"x": self.rect.centerx, "y": self.rect.centery}
				data = json.dumps(pos)
				#print (data)
				self.gs.transport.write(data)

			# Check for Collision with Boundaries or Self
			if self.rect.centerx >= self.gs.width or self.rect.centerx <= 0 or self.rect.centery >= self.gs.height or self.rect.centery <= 0:
				self.alive = False
			for r in range(self.head_size*2,len(self.tail)):
				if self.rect.colliderect(self.tail[r]):
					self.alive = False

			# Check for Collision with Opponent (Passed as Argument)
			for r in opp:
				if self.rect.colliderect(r):
					self.alive = False

class Player1(Player):
	def __init__(self,gs):
		Player.__init__(self,gs)
		self.rect.centerx = 320
		self.rect.centery = 320
		self.blue = (0,0,255)
		self.xvel = 0
		self.yvel = -1 * self.speed
		self.user = False

		self.tail.appendleft(self.rect.copy())
		for unit in range(1,self.tail_len):
			temp = self.rect.copy()
			temp.centery = self.rect.centery - self.yvel * unit
			self.tail.append(temp)

class Player2(Player):
	def __init__(self,gs):
		Player.__init__(self,gs)
		self.rect.centerx = 320
		self.rect.centery = 160
		self.red = (255,0,0)
		self.xvel = 0
		self.yvel = self.speed
		self.user = True

		self.tail.appendleft(self.rect.copy())
		for unit in range(1,self.tail_len):
			temp = self.rect.copy()
			temp.centery = self.rect.centery - self.yvel * unit
			self.tail.append(temp)

class GameSpace(Protocol):
	def __init__(self):
		# Initialize Game State Environment
		pygame.init()
		self.size = self.width, self.height = 640,480
		self.black = (0,0,0)
		self.screen = pygame.display.set_mode(self.size)

		# Initialize Game Objects
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.fuel = Fuel(self)
		self.queue = DeferredQueue()

	def main(self):
		# Read User Input and Handle Events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				# Quit on Escape Press
				if event.key == pygame.K_ESCAPE:
					self.loop.stop()
				else:
					if self.playing:
						self.player2.move(event.key)
			elif event.type == pygame.QUIT:
				self.loop.stop()

		# Call Tick Functions
		if self.playing:
			self.player1.tick(self.player2.tail)
			self.player2.tick(self.player1.tail)
			self.fuel.tick()

		# Update Screen
		self.screen.fill(self.black)
		self.screen.blit(self.fuel.food, self.fuel.rect)
		if self.playing:
			self.fuel.food.fill(self.fuel.white)
			for rectangle in self.player1.tail:
				self.screen.blit(self.player1.head,rectangle)
			for rectangle in self.player2.tail:
				self.screen.blit(self.player2.head,rectangle)
			self.player1.head.fill(self.player1.blue)
			self.player2.head.fill(self.player2.red)
		pygame.display.flip()
		pygame.display.update()

	def connectionMade(self):
		self.playing = True
		self.loop = LoopingCall(self.main)
		self.loop.start(1/60)

	def dataReceived(self, data):
		self.queue.put(data)
		self.queue.get().addCallback(self.update)

	def update(self, data):
		print(data)
		pos = json.loads(data)
		self.player1.rect.centerx = int(pos["x"])  
		self.player1.rect.centery = int(pos["y"])

		self.player1.tail.appendleft(self.player1.rect.copy()) 
		while len(self.player1.tail) > self.player1.tail_len:
			self.player1.tail.pop()  
		
if __name__ == "__main__":
	log.startLogging(sys.stdout)
	gcf = GameConnectionFactory()
	reactor.connectTCP("localhost", 40139, gcf)
	reactor.run()

