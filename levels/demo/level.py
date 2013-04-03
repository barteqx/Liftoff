#*-* coding: utf-8 *-*

import pygame
import os
from math import *

from world import World
from configuration import ConfigFile

def load():
	return Level

class Level(World):

	def __init__(self, game, config = None):
		self.configfile = os.path.join("levels", "demo", "demo.lvl")
		World.__init__(self, game, config)

	def check_level(self):
		if [x for x in self.objects if x["ident"] == 'b'] == []: return 1
		if [x for x in self.objects if x["ident"] == 'ship'] == [] or [x for x in self.objects if x["ident"] == 'a'] == []: return -1
