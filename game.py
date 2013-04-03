#*-* coding: utf-8

import pygame
import world
import multipprocessing
import os

import configuration

from pygame.locals import *

class InvalidFileError(Exception):
	pass

class Game(multiprocessing.Process):

		def __init__(self, config):
			
			multiprocessing.Process.__init__(self)
			self.comfig = config
			self.working = True

			
			self.game = world.World(self)

		def run(self):
			self.screen = pygame.display.init((self.config["x"], self.config["y"]))
			while self.working:
				self.game.update()
				for event in pygame.event.get():
					if event.type == MOUSEBUTTONDOWN:
						if event.button == 4:
							self.game.scale(self.game.scale_factor + 0.1, event.pos)
						if event.button == 5:
							self.game.scale(self.game.scale_factor - 0.1, event.pos)
					elif event.type == QUIT: self.exit()

				keylist = pygame.key.get_pressed()
				if keylist[K_UP]:
				 	self.game.pos[1] += 10
				if keylist[K_DOWN]:
				 	self.game.pos[1] -= 10
				if keylist[K_LEFT]:
				 	self.game.pos[0] += 10
				if keylist[K_RIGHT]:
				 	self.game.pos[0] -= 10
				self.screen.fill((0,0,0))
				self.screen.blit(self.game.image, self.game.pos)
				pygame.display.update()

		def exit(self):
			self.working = False
			self.kill()
