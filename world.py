#*-* coding: utf-8 *-*

import pygame
from math import *

from configuration import ConfigFile

class World(object):

	#do not create instances of this class, only inherit
	def __init__(self, game, config = None):
		self.game = game
		self.config = ConfigFile(self.configfile)
		if not config:
			self.config.loadFile()
		else: self.config.configuration = config
		self.fps = float(self.game.config["fps"])
		self.x = self.config["x"]
		self.y = self.config["y"]
		self.img = pygame.Surface((self.x, self.y))
		self.image = self.img
		self.pos = list(self.config["position"])
		if "scale_factor" in self.config.keys():
			self.scale_factor = self.config["scale_factor"]
		else:
			self.scale_factor = 1.0

		self.objects = pygame.sprite.Group([self.game.object_classes[obj["type"]](self, obj) for obj in self.config["objects"]])
		self.player_objects = pygame.sprite.Group([obj for obj in self.objects if obj.config["player"]])
		
		if not config:
			for obj in self.objects: obj.initial_velocity()

		self.scale_list = []
		self.position_list = []
		self.selected = None
		if not "counters" in self.config.keys():
			self.counters = {"draw_selected":0}
		else:
			self.counters = self.config.configuration["counters"]
		self.tracking = False

	def __getitem__(self, key):

		for item in self.objects:
			if item.ident == key:
					return item

	def transform(self):
		self.image = pygame.transform.smoothscale(self.img.subsurface((self.pos[0], self.pos[1], self.game.x*2/self.scale_factor, self.game.y*2/self.scale_factor)), (self.game.x, self.game.y))

	def scale(self, dest_factor, position):
		f = lambda x: -2*x**3 + 3*x**2
		self.scale_list = [self.scale_factor + f(x/(self.fps/2))*(dest_factor-self.scale_factor) for x in range(int(self.fps/2) + 1)]
		l = self.scale_list
		self.position_list = [[int(position[0] - (position [0] - self.pos[0])/(x/l[0])), int(position[1] - (position[1] - self.pos[1])/(x/l[0]))] for x in l]

	def collision(self, obj1, obj2):
		ax = obj1.rect.x
		ay = obj1.rect.y
		bx = obj2.rect.x
		by = obj2.rect.y
		dx = (bx - ax)
		dy = (by - ay)
		D = obj1.radius + obj2.radius - hypot(dx, dy)
		angle = atan2(dy, dx)
		mtx = D*cos(angle)
		mty = D*sin(angle)
		m1 = obj2["mass"]/float(obj1["mass"]+obj2["mass"])
		m2 = obj1["mass"]/float(obj1["mass"]+obj2["mass"])
		if obj1["ident"] == "central_object":
		 	m1 = 0
		 	m2 = 1
		elif obj2["ident"] == 'central_object':
		 	m1 = 1
		 	m2 = 0
		obj1.set_pos((obj1.x + mtx*m1, obj1.y + mty*m1))
		obj2.set_pos((obj2.x - mtx*m2, obj2.y - mty*m2))
		v1 = hypot(obj1.vx, obj1.vy)
		v2 = hypot(obj2.vx, obj2.vy)
		try:
			sin_alfa = (bx-ax)/hypot((bx-ax),(by-ay))
			cos_alfa = (by-ay)/hypot((bx-ax),(by-ay))
		except ZeroDivisionError:
			print hypot((bx-ax),(by-ay))
		m = obj1["mass"]/obj2["mass"]
		k = obj1["energy_loss"]*obj2["energy_loss"]
		v1r = obj1.vy*cos_alfa - obj1.vx*sin_alfa
		v2r = obj2.vy*cos_alfa - obj2.vx*sin_alfa
		v1p = obj1.vx*cos_alfa + obj1.vy*sin_alfa
		v2p = obj2.vx*cos_alfa + obj2.vy*sin_alfa
		alfa = atan2((by - ay),(bx - ax)) - degrees(90)
		beta1 = atan2(obj1.vy, obj1.vx)
		beta2 = atan2(obj2.vy, obj2.vx)
		w1p = v1*cos(beta1 - alfa)
		w1r = v1*(m-k)*sin(beta1 - alfa)/(m+1) + v2*(k+1)*sin(beta2 - alfa)/(m+1)
		w2p = v2*cos(beta2 - alfa)
		w2r = v1*m*(k+1)*sin(beta1 - alfa)/(m+1) + v2*(1-k*m)*sin(beta2 - alfa)/(m+1)
		w1x = (w1p*cos(alfa) - w1r*sin(alfa))
		w1y = (w1p*sin(alfa) + w1r*cos(alfa))
		w2x = (w2p*cos(alfa) - w2r*sin(alfa))
		w2y = (w2p*sin(alfa) + w2r*cos(alfa))
		obj1.set_velocity(w1x, w1y)
		obj2.set_velocity(w2x, w2y)

		
	def keys(self, keylist):
		for obj in self.player_objects: 
			obj.keys(keylist)

	def select(self, pos):
		self.selected = None
		self.tracking = False
		for obj in self.objects:
			if hypot(obj.x - pos[0], obj.y - pos[1]) <= obj.radius:
				self.selected = obj

	def track(self):
		if self.tracking and self.selected:
			self.tracking = False
		else:
			self.tracking = True
		

	def draw_selected(self):
		if self.selected:
			pygame.draw.circle(self.img, (0,0,255), (self.selected.rect.centerx, self.selected.rect.centery), int(self.selected.radius + 20 + sin(self.counters["draw_selected"])*15), 6)
			self.counters["draw_selected"] += pi*2/(self.game.fps)
			self.counters["draw_selected"] = self.counters["draw_selected"] % (pi*2)

	def update(self):
		if not self.game.paused:
			self.img.fill((0,0,0))
			self.objects.update()
			for obj1 in self.objects:
				for obj2 in self.objects:
					if obj1 != obj2 and pygame.sprite.collide_circle(obj1, obj2):
						self.collision(obj1, obj2)
						obj1.collision(obj2)
						obj2.collision(obj1)
			
			
			self.objects.draw(self.img)
			if self.scale_list and self.position_list and 1 <= self.scale_factor <= 3:
				self.scale_factor = self.scale_list.pop(0)
				self.pos = self.position_list.pop(0)
			if 1 > self.scale_factor: self.scale_factor = 1
			if 3 < self.scale_factor: self.scale_factor = 3
			
			if self.tracking and self.selected:
				self.pos[0] = int(self.selected.x - self.game.x/self.scale_factor)
				self.pos[1] = int(self.selected.y - self.game.y/self.scale_factor)

			if self.pos[0] >= self.config["x"] - self.game.x*2/self.scale_factor - 1:
			 	self.pos[0] = self.config["x"] - self.game.x*2/self.scale_factor - 1
			if self.pos[1] >= self.config["y"] - self.game.y*2/self.scale_factor - 1:
			 	self.pos[1] = self.config["y"] - self.game.y*2/self.scale_factor - 1
			if self.pos[0] < 0: self.pos[0] = 0
			if self.pos[1] < 0: self.pos[1] = 0

			self.draw_selected()
			self.transform()

	def get_state(self):

		self.config["objects"] = [obj.config for obj in self.objects]
		self.config["scale_factor"] = self.scale_factor
		self.config["position"] = self.pos
		return self.config.configuration