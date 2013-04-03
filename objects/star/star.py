#*-* coding: utf-8 *-*

from game_object import Object

from pygame.locals import *

def load():
	return Star

class Star(Object):
	
	def update(self):
		self.lastx, self.lasty = self.x, self.y = self["position"]