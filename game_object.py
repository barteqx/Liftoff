#*-* coding: utf-8 *-*

import pygame
import math
import os
import random

from pygame.locals import *

#Abstract class - every object in game inherits from this class
class Object(pygame.sprite.Sprite):

	#constructor of every subclass should call this function firstly.
	def __init__(self, world, config):
		pygame.sprite.Sprite.__init__(self)
		self.world = world
		self.config = config
		self.type =  self.config["type"]
		self.ident = self.config["ident"]
		self.img = pygame.Surface((self['radius']*2, self["radius"]*2))
		pygame.draw.circle(self.img, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), (self['radius'], self["radius"]),self["radius"])
		self.img.set_colorkey((0,0,0))
		self.image = self.img
		self.dying = False

		if not "counters" in self.config.keys():
			self["counters"] = {"angle":0, 'reset': 0}
		if not "collision_list" in self.config.keys():
			self["collision_list"] = []
		if not "health" in self.config.keys():
			self["health"] = self["mass"]
		if not "additional_force" in self.config.keys():
			self["additional_force"] = [0,0]
		self.radius = self.config["radius"]*math.sqrt(2)
		self.thrust = 0
		self.rect = self.image.get_rect()
		self.x, self.y = self.rect.centerx, self.rect.centery = self.config["position"]
		if "velocity" in self.config.keys():
			self.vx, self.vy = self["velocity"]
		else:
			self.vx = self.vy = 0
		self.additional_force = (0,0)
		self.G = 6.6738481*10**(-11)
		self.initialized = False


	def __getitem__(self, key):
		return self.config[key]

	def __setitem__(self, key, value):
		self.config[key] = value
			
	def update(self):
		
		if self["health"] <= 0:
			self.kill()
		self.lastx = self.x
		self.lasty = self.y

		self.rotate()
		self.move()
		self.rect.centerx, self.rect.centery = [int(self.x), int(self.y)]
		self["velocity"] = (self.vx, self.vy)

	def rotate(self):
		self.image = pygame.transform.rotate(self.img, self["counters"]["angle"])
		self.rect = self.image.get_rect()

	def move(self):
	
		Fx = []
		Fy = []
	
		for obj in self.world.objects:

			if obj["ident"] != self["ident"] and not obj["ident"] in self["collision_list"]:
				dx = obj.x - self.x
				dy = obj.y - self.y

				dist = math.hypot(dx, dy)
				angle = math.atan2(dy, dx)
				
				F = self.G * obj.config["mass"] * self.config["mass"]/(dist**2)
				
				Fx.append(F*math.cos(angle))
				Fy.append(F*math.sin(angle))
		
		Fx = sum(Fx) - self.thrust*math.sin(math.radians(self["counters"]["angle"])) + self["additional_force"][0]
		Fy = sum(Fy) - self.thrust*math.cos(math.radians(self["counters"]["angle"])) + self["additional_force"][1]

		self.vx += Fx*(1.0/self.world.fps)/self.config["mass"] 
		self.vy += Fy*(1.0/self.world.fps)/self.config["mass"]
	
		self["collision_list"] = []

		self.x = (self.x + self.vx) % self.world.x
		self.y = (self.y + self.vy) % self.world.y
		self["position"] = (self.x, self.y)
		self["velocity"] = (self.vx, self.vy)


	def collision(self, obj):
		self["collision_list"].append(obj["ident"])

	def turn_left(self):
		self["counters"]["angle"] = (self["counters"]["angle"] + 5) % 360

	def turn_right(self):
		self["counters"]["angle"] = (self["counters"]["angle"] - 5) % 360

	def engine_on(self):
		self.thrust = self.config["thrust"]

	def engine_off(self):
		self.thrust = 0

	def keys(self, keys):
		pass

	def set_velocity(self, vx = None, vy = None):
		if not self['ident'] == 'central_object':
			if vx: self.vx = vx
			if vy: self.vy = vy

	def set_pos(self, pos):
		self.x = pos[0]
		self.rect.centerx = int(self.x) % self.world.x
		self.y = pos[1]
		self.rect.centery = int(self.y) % self.world.y

	def initial_velocity(self):
		if not self.initialized:
			self.initialized = True
			if self.config["orbit"] == None:
				self.vx = 0
				self.vy = 0
			else:
				obj = self.world[self.config["orbit"]]
				obj.initial_velocity()
				dx = obj.x - self.x
				dy = obj.y - self.y
				length = math.hypot(dx, dy)
				a = math.atan2(dx, dy)
				orbit_v = math.sqrt(self.G*obj.config["mass"]/length)/8
				directions = {"R" : 180, "L": 0}
				self.vx = obj.vx + math.cos(a + math.radians(directions[self.config["direction"]])) * orbit_v
				self.vy = obj.vy + math.sin(a + math.radians(directions[self.config["direction"]])) * orbit_v

