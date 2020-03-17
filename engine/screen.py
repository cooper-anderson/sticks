#!/usr/bin/env python
# -*- coding: utf8 -*-

import locale
import os
import termios
import sys
import time
from array import array
from fcntl import ioctl
from select import select
from signal import signal, SIGWINCH
from random import randint

if __name__ == "__main__":
	from color import Color, Colors
else:
	from . import color
	# from color im

locale.setlocale(locale.LC_ALL, '')
os.environ.setdefault("ESCDELAY", "25")
ESC = "\033["


class Size(object):
	width = 0
	height = 0


class Vector(object):
	x = 0
	y = 0

	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y


class Tile(object):
	def __init__(self, char="", fg=-1, bg=-1):
		self.char = char
		self.fg = fg
		self.bg = bg

	def __eq__(self, other):
		return self.char == other.char and self.fg == other.fg and self.bg == other.bg


class Screen(object):
	def __init__(self):
		print(ESC + "?1049h" + ESC + "?25l" + ESC + "2J", end="")
		self.size = Size()
		self._initial = termios.tcgetattr(1)
		t = termios.tcgetattr(1)
		t[3] &= ~(termios.ECHO | termios.ICANON)  # | termios.OPOST)
		termios.tcsetattr(1, termios.TCSANOW, t)
		self.paused = False
		self._resize()
		self.queue = ""
		self.map = {}
		self.changes = {}
		self.colorIndex = -1
		self.hasRGB = True
		signal(SIGWINCH, self._resize)

	def _resize(self, a=0, b=0):
		if not self.paused:
			buf = array('h', [0, 0])
			ioctl(1, termios.TIOCGWINSZ, buf, 1)
			self.size.width = buf.pop()
			self.size.height = buf.pop()
			self.width = self.size.width
			self.height = self.size.height
			self.clear()

	def clear(self):
		print(ESC + "2J", end="")

	def pause(self):
		self.paused = True
		self.close(False)

	def resume(self):
		self.paused = False
		print(ESC + "?1049h" + ESC + "?25l" + ESC + "2J", end="")
		self.size = Size()
		self._initial = termios.tcgetattr(1)
		t = termios.tcgetattr(1)
		t[3] &= ~(termios.ECHO | termios.ICANON)  # | termios.OPOST)
		termios.tcsetattr(1, termios.TCSANOW, t)
		self._resize()

	def close(self, verbose=True):
		termios.tcsetattr(1, termios.TCSANOW, self._initial)
		print("\033[?1049l", end="")
		print("\033[?25h", end="")
		termios.tcflush(sys.stdin, termios.TCIOFLUSH)
		if verbose:
			print("[Process closed]")

	def addstr(self, y=0, x=0, string="", fg=-1, bg=-1):
		if type(string) != str:
			string = str(string)
		colorFG = ("255;255;255" if fg == -1 else fg.getRGB()) if self.hasRGB else (255 if fg == -1 else fg.get256())
		colorBG = (-1 if bg == -1 else bg.getRGB()) if self.hasRGB else (-1 if bg == -1 else bg.get256())
		for i in range(len(string)):
			tile = Tile(string[i], colorFG, colorBG)
			self.changes[(x + i, y)] = tile

	def refresh(self, clear=True, char=' '):
		colorMap = {}
		new_map = {}
		# print(ESC + "0m")
		for pos in self.changes:
			tile = self.changes[pos]
			new_map[pos] = tile
			if (tile.fg, tile.bg) not in colorMap:
				colorMap[(tile.fg, tile.bg)] = {}
			colorMap[(tile.fg, tile.bg)][pos] = tile
			if pos in self.map:
				del self.map[pos]
		for c in colorMap:
			number = "2;" if self.hasRGB else "5;"
			if c[1] != -1:
				print(ESC + "38;" + number + str(c[0]) + 'm' + ESC + "48;" + number + str(c[1]) + 'm', end='\r')
			else:
				print(ESC + "0m" + ESC + "38;" + number + str(c[0]) + 'm', end='\r')
			for pos in colorMap[c]:
				tile = colorMap[c][pos]
				print(ESC + str(pos[1] + 1) + ';' + str(pos[0] + 1) + 'H' + tile.char, end='\r')
		if clear:
			print(ESC + "0m", end='\r')
			for pos in self.map:
				print(ESC + str(pos[1] + 1) + ';' + str(pos[0] + 1) + 'H' + char, end='\r')
		self.changes = {}
		self.map = new_map

	def getch(self, timeout=0, flush=True, refresh=True):
		if select([sys.stdin], [], [], timeout) == ([sys.stdin], [], []):
			s = ord(sys.stdin.read(1))
			self.flushinp()
			if refresh and s == 12:
				self.clear()
			return s
		else:
			return -1

	def flushinp(self):
		termios.tcflush(sys.stdin, termios.TCIFLUSH)

	def autoflushinp(self, flag=True):
		pass

	def inpdelay(self, flag):
		pass


if __name__ == "__main__":
	screen = Screen()
	guy = Vector(screen.size.width // 2, screen.size.height // 2)
	clear = True
	rand = False
	letter = 0
	sprites = ['o', 'O']
	sIndex = 0
	r = 5
	g = 5
	b = 5
	try:
		color2 = Color(r=0, g=255, b=0)
		count = 0
		char = ' '
		while True:
			# if clear:
			# 	screen.clear()
			if rand:
				for i in range(int(screen.size.width * screen.size.height * .0125)):
					x = randint(0, screen.size.width)
					y = randint(0, screen.size.height)
					screen.addstr(y, x, str(randint(0, 9)))
			c = screen.getch()
			if c != -1:
				letter = c
			if c == ord('w'):
				guy.y -= 1
			elif c == ord('s'):
				guy.y += 1
			elif c == ord('a'):
				guy.x -= 1
			elif c == ord('d'):
				guy.x += 1
			elif c == ord('m'):
				clear = not clear
			elif c == ord('r'):
				rand = not rand
			elif c == ord('u'):
				r = min(r+1, 5)
			elif c == ord('j'):
				r = max(r-1, 0)
			elif c == ord('i'):
				g = min(g+1, 5)
			elif c == ord('k'):
				g = max(g-1, 0)
			elif c == ord('o'):
				b = min(b+1, 5)
			elif c == ord('l'):
				b = max(b-1, 0)
			elif c == ord(':'):
				char = chr(screen.getch(5))
			if count % 30 == 0:
				sIndex = 1 - sIndex
			screen.addstr(guy.y, guy.x, sprites[sIndex], color2)
			color2.setHue(count)
			screen.addstr(1, 1, count, Colors.white)
			screen.addstr(2, 1, letter)
			screen.addstr(screen.height - 2, screen.width - 25, "Try resizing your window")
			screen.addstr(screen.height - 3, screen.width - 25, "Buttons: wasdrmuiojkl")
			count += 1
			screen.refresh(clear, char)
			time.sleep(1.0 / 60.0)
	except KeyboardInterrupt:
		pass
	finally:
		screen.close()

