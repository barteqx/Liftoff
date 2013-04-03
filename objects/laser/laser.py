#*-* coding: utf-8 *-*

from game_object import Object

from pygame.locals import *
from math import *

import pygame

def load():
	return Laser

class Laser(Object):
	
	def update(self):
		self.x += self.vx
		self.y += self.vy

	def collision(obj):
		Object.__init__(obj)

		self.kill()