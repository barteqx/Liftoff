#*-* coding: utf-8 *-*

import pygame
import os
import json
from game_object import Object

from pygame.locals import *
from math import *

def load():
	return Ship

class Ship(Object):

	def __init__(self, world, config):
		Object.__init__(self, world, config)
		self.img = pygame.image.load(os.path.join('objects', 'ship', 'images', 'ship.bmp'))
		self.img.set_colorkey(self.img.get_at((0,0)))
		if not "bomb" in self.config.keys():
			self["counters"]["bomb"] = 0
		
	def keys(self, keys):
		if keys[K_w]:
			self.engine_on()
		else:
			self.engine_off()
		if keys[K_a]:
			self.turn_left()
		if keys[K_d]:
			self.turn_right()
		if keys[K_SPACE]:
			self.bomb()

	def bomb(self):
		if len([x for x in self.world.objects if x["type"] == "bomb"]) == 0:
			cfgfile = open(os.path.join("objects", "ship", "bomb.cfg"), 'r')
			cfg = json.load(cfgfile)
			cfg["position"] = (int(self.x - 50*sin(radians(self["counters"]["angle"]))), int(self.y - 50*cos(radians(self["counters"]["angle"]))))
			cfg["counters"] = {}
			cfg["counters"]["angle"] = self["counters"]["angle"]
			cfg["counters"]["time"] = 10
			cfg["radius"] = 3
			cfg["velocity"] = self["velocity"]
			cfg["ident"] = "bomb%d" % self["counters"]["bomb"]
			self.world.objects.add(self.world.game.object_classes["bomb"](self.world, cfg))
			self.world["bomb%d" % self["counters"]["bomb"]].engine_on()
			self["counters"]["bomb"] += 1