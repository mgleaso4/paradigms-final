#!/usr/bin/env python3
# Maddie Gleason and Ben Gunning
# PyGame + Twisted Final Project

import os, sys, pygame, math, collections

class Player(pygame.sprite.Sprite):
# Initialize Player with Starting Position
	def __init__(self,gs):
		self.gs = gs
		self.head_size = 5
		self.head = pygame.Surface((self.head_size,self.head_size))
		self.rect = self.head.get_rect()
		self.rect.centerx = 320
		self.rect.centery = 240
		self.blue = (0,0,255)
		self.xvel = 0
		self.yvel = -1
		self.alive = True

# Create Tail to Store Previous Rectangles
		self.tail_len = 50
		self.tail = collections.deque()
		self.tail.appendleft(self.rect.copy())

# Change the Direction of the Player
	def move(self,key):
		if key == pygame.K_UP and self.yvel <= 0:
			self.xvel = 0
			self.yvel = -1
		if key == pygame.K_DOWN and self.yvel >= 0:
			self.xvel = 0
			self.yvel = 1
		if key == pygame.K_LEFT and self.xvel <= 0:
			self.xvel = -1
			self.yvel = 0
		if key == pygame.K_RIGHT and self.xvel >= 0:
			self.xvel = 1
			self.yvel = 0

	def tick(self):
		if self.alive:
# Update the Player Position
			self.rect.centerx += self.xvel
			self.rect.centery += self.yvel

# Add the New Rectangle to the Left of the Tail and Pop the Rightmost Rectangle
			self.tail.appendleft(self.rect.copy())
			while len(self.tail) > self.tail_len:
				self.tail.pop()

# Check for Collision with Boundaries or Self
			if self.rect.centerx >= self.gs.width or self.rect.centerx <= 0 or self.rect.centery >= self.gs.height or self.rect.centery <= 0:
				self.alive = False
			for r in range(self.head_size*2,len(self.tail)):
				if self.rect.colliderect(self.tail[r]):
					self.alive = False

class GameSpace:
	def main(self):
# Initialize Game State Environment
		pygame.init()
		self.size = self.width, self.height = 640,480
		self.black = (0,0,0)
		self.screen = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()

# Initialize Game Objects
		self.player = Player(self)

# Start Game Loop
		running = True
		while running:
			self.clock.tick(60)

# Read User Input and Handle Events
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
# Quit on Escape Press
					if event.key == pygame.K_ESCAPE:
						running = False
					else:
						self.player.move(event.key)
				elif event.type == pygame.QUIT:
					running = False

# Call Tick Functions
			self.player.tick()

# Update Screen
			self.screen.fill(self.black)
			for rectangle in self.player.tail:
				self.screen.blit(self.player.head,rectangle)
			self.player.head.fill(self.player.blue)
			pygame.display.flip()
			pygame.display.update()

if __name__ == "__main__":
	gs = GameSpace()
	gs.main()
