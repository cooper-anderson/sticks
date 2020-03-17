#!/usr/bin/env python
# -*- coding: utf8 -*-

from engine import Game, GameObject
from engine.color import Colors
import math
# from random import randint


class Hand(object):
	symbols = ['0', '1', '2', '3', '4']
	def __init__(self, index=0, name=""):
		self.index = index
		self.name = ("Player #" + str(index)) if name == "" else name
		self.left = 1
		self.right = 1
	
	def __repr__(self):
		return '[' + Hand.symbols[self.left] + "] [" + Hand.symbols[self.right] + ']'


class Sticks(Game):
	def start(self):
		self.reset()

	def update(self):
		self.draw_players()
		self.screen.refresh()

	def reset(self):
		self.count = len(names)
		self.hands = [Hand(i, names[i]) for i in range(self.count)]

	def draw_players(self):
		width = self.screen.width
		height = self.screen.height
		radius = int(min(width / 2, height) * 1 / 2)
		for index, hand in enumerate(self.hands):
			theta = index * 2.0 * math.pi / self.count
			x = int(width / 2 + radius * math.sin(theta))
			y = int(height / 2 - radius * math.cos(theta) / 2)
			self.screen.addstr(y, x - len(hand.name) // 2, hand.name)
			self.screen.addstr(y + 1, x - 3, hand)


if __name__ == "__main__":
	count = "asdf"
	while not count.isdigit():
		count = input("How many players?: ")
		if count == "":
			count = '0'
	if count != '0':
		names = [input("Enter [Player #" + str(i) + "]'s name: ") for i in range(int(count))]
	else:
		count = 2
		names = ["", ""]
	sticks = Sticks()

