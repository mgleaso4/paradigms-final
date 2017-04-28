#!/usr/bin/env python3
# Maddie Gleason and Ben Gunning
# PyGame + Twisted Final Project

import os, sys, pygame, math

class Player(pygame.sprite.Sprite):
	def __init__(self,gs):
		return
	def tick(self):
		return

class GameSpace:
	def main(self):
# Initialize Game State Environment
		pygame.init()
		self.size = self.width, self.height = 640,480
		self.black = (0,0,0)
		self.screen = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()

# We could use the following command if we want the user to hold down the key for the direction they want to move
# This probably isn't necessary if we just have the user press a key only to change direction
#		pygame.key.set_repeat(1,60)

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
					if event.key == pygame.ESCAPE:
						running = False
				elif event.type == pygame.QUIT:
					running = False

# Update Screen
			self.screen.fill(self.black)
			pygame.display.flip()
			pygame.display.update()

if __name__ == "__main__":
	gs = GameSpace()
	gs.main()
