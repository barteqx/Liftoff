#*-* coding: utf-8 *-*
import pygame

from game_object import Object

from pygame.locals import *

from math import *

def load():
	return Bomb

class Bomb(Object):
	def __init__(self, world, config):
		Object.__init__(self, world, config)
		self["collided"] = False
		self["counters"]["frame"] = self.world.game.fps
		self.rad = self["counters"]["frame"] * 3

	def collision(self, obj):
		if self["counters"]["time"] <= 0:
			if not self["collided"]:
				Object.collision(self, obj)
				self.explode()

	def explode(self):
		self["collided"] = True
		self.img = pygame.Surface((1,1))
		self.img.fill((255,255,255))

	def update(self):
		if not self["collided"]:
			Object.update(self)
			self["counters"]["time"] -= 1
			if self["counters"]["time"] < 0: self.engine_off()
		else:
			if self["counters"]["frame"] == 0:
				self.kill()
			else:
			
				self["counters"]["frame"] -= 1
				self.rad = (60 - self["counters"]["frame"])*3
				pygame.draw.circle(self.world.img, (255,255,255), (int(self.x), int(self.y)), int(self.rad))
				for obj in self.world.objects:
					if hypot(obj.x - self.x, obj.y - self.y) < self.rad and obj["ident"] != self["ident"]:
						obj["additional_force"][0] += 200 - (obj.x - self.x)
						obj["additional_force"][1] += 200 - (obj.y - self.y)
						if not "damage" in self.config.keys():
							obj["health"] -= 200 - self.rad
						else:
							obj["health"] -= self["damage"]

			