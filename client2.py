#!/usr/bin/env python3
# Maddie Gleason and Ben Gunning
# PyGame + Twisted Final Project

import os, sys, pygame, math, collections, random, queue, time
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
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

	# Used in client1 to check for collision between user and food 
	def tick(self):
		pass

class Player(pygame.sprite.Sprite):
	# Initialize Player with Starting Position
	def __init__(self,gs):
		self.gs = gs
		self.head_size = 7
		self.head = pygame.Surface((self.head_size,self.head_size))
		self.rect = self.head.get_rect()
		self.speed = 1
		self.alive = True
		self.collision = False
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
			self.gs.transport.write(data + '\r\n')

		# Check for Collision with Boundaries or Self
		if self.rect.centerx >= self.gs.width or self.rect.centerx <= 0 or self.rect.centery >= self.gs.height or self.rect.centery <= 0:
			self.alive = False
			if self.user:
				dead = {"dead": 2}
			else:
				dead = {"dead": 1}
			data = json.dumps(dead)
			self.gs.transport.write(data + '\r\n')

		for r in range(self.head_size*2,len(self.tail)):
			if self.rect.colliderect(self.tail[r]):
				self.alive = False
				if self.user:
					dead = {"dead": 2}
				else:
					dead = {"dead": 1}
				data = json.dumps(dead)
				self.gs.transport.write(data + '\r\n')

		# Check for Collision with Opponent (Passed as Argument)
		for r in opp:
			if self.rect.colliderect(r):
				self.collision = True
				if self.user:
					collision = {"collision": 2}
				else:
					collision = {"collision": 1}
				data = json.dumps(collision)
				self.gs.transport.write(data + '\r\n')

class Player1(Player):
	def __init__(self,gs):
		# Intitialize player 2's position and speed
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
		# Intitialize player 1's position and speed
		Player.__init__(self,gs)
		self.rect.centerx = 320
		self.rect.centery = 160
		self.red = (255,0,0)
		self.xvel = 0
		self.yvel = self.speed
		# player 2 is user in client2.py
		self.user = True

		self.tail.appendleft(self.rect.copy())
		for unit in range(1,self.tail_len):
			temp = self.rect.copy()
			temp.centery = self.rect.centery - self.yvel * unit
			self.tail.append(temp)

class GameSpace(LineReceiver):
	def __init__(self):
		# Initialize Game State Environment
		pygame.init()
		self.size = self.width, self.height = 640,480
		self.black = (0,0,0)
		self.screen = pygame.display.set_mode(self.size)

		# Load and Resize Game Over Images
		self.bluewins = pygame.image.load("bluewins.png")
		self.bluewins = pygame.transform.scale(self.bluewins, (640, 480))
		self.bluerect = self.bluewins.get_rect()
		self.redwins = pygame.image.load("redwins.png")
		self.redwins = pygame.transform.scale(self.redwins, (640, 480))
		self.redrect = self.redwins.get_rect()
		self.gameover = pygame.image.load("gameover.png")
		self.gameover = pygame.transform.scale(self.gameover , (640, 480))
		self.gamerect = self.gameover.get_rect()

		# Initialize Game Objects
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.fuel = Fuel(self)
		self.queue = DeferredQueue()
		self.queue.get().addCallback(self.update)

	def main(self): 
		# Read User Input and Handle Events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				# Quit on Escape Press
				if event.key == pygame.K_ESCAPE:
					os._exit(1)
				else:
					if self.playing:
						self.player2.move(event.key)
			elif event.type == pygame.QUIT:
				os._exit(1)

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

		# Check for collision between players, and display winner
		if self.player1.collision:
			if self.player2.collision:
				# Whoever is longer, wins; otherwise, tie
				if self.player1.tail_len > self.player2.tail_len:
					self.screen.blit(self.bluewins, self.bluerect)
				elif self.player2.tail_len > self.player1.tail_len: 
					self.screen.blit(self.redwins, self.redrect) 
				else:
					self.screen.blit(self.gameover, self.gamerect)
			else: 
				self.screen.blit(self.redwins, self.redrect) 
			pygame.display.flip()
			pygame.display.update()
			time.sleep(3)
			os._exit(1)
		elif self.player2.collision:
			self.screen.blit(self.bluewins, self.bluerect)
			pygame.display.flip()
			pygame.display.update()
			time.sleep(3)
			os._exit(1)

		# Check if player 1 has died and display red player wins
		if not self.player1.alive: 
			self.screen.blit(self.redwins, self.redrect) 
			pygame.display.flip()
			pygame.display.update()
			time.sleep(3)
			os._exit(1) 

		# Check if player 2 has died and display blue player wins
		if not self.player2.alive: 
			self.screen.blit(self.bluewins, self.bluerect)
			pygame.display.flip()
			pygame.display.update()
			time.sleep(3)
			os._exit(1)

	def connectionMade(self):
		pass

	def lineReceived(self, data):
		# Upon receiving initial go data start game loop
		if data == 'go':
			self.playing = True
			self.loop = LoopingCall(self.main)
			self.loop.start(1/60)
		else:
			self.queue.put(data)

	def update(self, data):
		pos = json.loads(data)
		# pass over new length if food consumed
		if 't1' in pos:
			self.fuel.rect.centerx = int(pos["x"])
			self.fuel.rect.centery = int(pos["y"])
			self.player1.tail_len = int(pos["t1"])
			self.player2.tail_len = int(pos["t2"])
		elif 'dead' in pos:
			if int(pos["dead"]) == 1:
				self.player1.alive = False
			else:
				self.player2.alive = False
		elif 'collision' in pos:
			if int(pos["collision"]) == 1:
				self.player1.collision = True
			else:
				self.player2.collision = True
		else:
			# update player 1 with new position
			self.player1.rect.centerx = int(pos["x"])
			self.player1.rect.centery = int(pos["y"])

			# update player 1's tail
			self.player1.tail.appendleft(self.player1.rect.copy())
			while len(self.player1.tail) > self.player1.tail_len:
				self.player1.tail.pop()
		self.queue.get().addCallback(self.update)

if __name__ == "__main__":
	log.startLogging(sys.stdout)
	gcf = GameConnectionFactory()
	reactor.connectTCP("localhost", 40139, gcf)
	reactor.run()

