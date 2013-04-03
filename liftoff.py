#!/bin/python
#*-* coding: utf-8 *-*

import pygame
import world
import multiprocessing
import os
import sys
import datetime
import importlib

import Tkinter

import configuration

from pygame.locals import *

class InvalidFileError(Exception):
	pass

class Game(multiprocessing.Process):

		def __init__(self, command):
			
			multiprocessing.Process.__init__(self)
			self.config = configuration.ConfigFile("config.cfg")
			self.config.loadFile()
			self.working = True
			self.paused = False
			self.tk = Tkinter.Tk()
			self.fps = self.config["fps"]
			self.x = self.config["x"]
			self.y = self.config["y"]
			self.screenx = self.tk.winfo_screenwidth()
			self.screeny = self.tk.winfo_screenheight()
			self.counter = 1
			pygame.init()
			self.clock = pygame.time.Clock()
			self.fullscreen = True

			i = 0
			for root, dirs, files in os.walk("objects"):
				objects = dirs
				i += 1
				if i > 0: break

			self.object_classes = {}
			for obj in objects:
				try:
					self.object_classes[obj] = importlib.import_module('objects.%s.%s' % (obj, obj)).load()
				except ImportError, e:
					pass

			i = 0
			for root, dirs, files in os.walk("levels"):
				levels = dirs
				i += 1
				if i > 0: break

			self.levels = {}
			for lvl in levels:
				try:
					self.levels[lvl] = importlib.import_module('levels.%s.level' % lvl).load()
				except ImportError:
					pass

			if command[0] == "-s":
				try:
					cfg = configuration.ConfigFile(command[1])
					cfg.loadFile()
					self.game = self.levels[cfg["name"]](self, cfg.configuration)
				except (KeyError, IndexError):
					print "Incorrect save file. Exiting..."
					exit()
			else:
				try:
					self.game = self.levels[command[0]](self)
				except (KeyError, IndexError):
					print "Incorrect level. Exiting..."
					exit()

		def run(self):
			if self.screenx * 2 > self.game.config["x"] or self.screeny * 2 > self.game.config["y"]:
				self.x = self.config["x"]
				self.y = self.config["y"]
				self.screen = pygame.display.set_mode((self.config["x"], self.config["y"]))
			else: 
				self.screen = pygame.display.set_mode((self.screenx, self.screeny), FULLSCREEN)
				self.x = self.screenx
				self.y = self.screeny

			while self.working:
				self.clock.tick(int(self.config["fps"]))
				self.game.update()
				for event in pygame.event.get():
					
					if event.type == MOUSEBUTTONDOWN:
						pos = [int(self.game.pos[0] + event.pos[0]*2/self.game.scale_factor), int(self.game.pos[1] + event.pos[1]*2/self.game.scale_factor)]
						if event.button == 4 and self.game.scale_factor < 3:
							self.game.scale(self.game.scale_factor + 0.4, pos)
						if event.button == 5 and self.game.scale_factor > 1:
							self.game.scale(self.game.scale_factor - 0.4, pos)
					elif event.type == MOUSEBUTTONUP:
						pos = [int(self.game.pos[0] + event.pos[0]*2/self.game.scale_factor), int(self.game.pos[1] + event.pos[1]*2/self.game.scale_factor)]
						if event.button == 1:
							self.game.select(pos)
					elif event.type == KEYDOWN:
						if event.key == 27:	
							self.exit()
						if event.key == 116:
							self.game.track()
					elif event.type == QUIT: self.exit()

				keylist = pygame.key.get_pressed()
				self.game.keys(keylist)
				if keylist[K_UP]:
				 	self.game.pos[1] -= 20
				if keylist[K_DOWN]:
				 	self.game.pos[1] += 20
				if keylist[K_LEFT]:
				 	self.game.pos[0] -= 20
				if keylist[K_RIGHT]:
				 	self.game.pos[0] += 20
				self.screen.fill((0,0,0))
				self.screen.blit(self.game.image, (0,0))
				pygame.display.update()
				if self.counter == 0:
					x = self.game.check_level()
					if x == 1:
						print "You won!"
						self.exit(False)
					elif x == -1:
						print "You lost!"
						self.exit(False)
				self.counter = (self.counter + 1) % 60

		def exit(self, saving = True):
			if saving:
				now = datetime.datetime.now()
				name = "%d_%d_%d-%d_%d_%d.sav" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
				save = configuration.ConfigFile(name, "saves")
				save.configuration = self.game.get_state()
				save.saveFile()
			self.working = False
			exit()

if __name__ == "__main__":
	try:
		b = Game(sys.argv[1:])
		b.run()

	except IndexError:
		print "Specify the level or save path"
