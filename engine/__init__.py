#!/usr/bin/env python3
# -*- coding: utf8 -*-

import asyncio
from time import time
from uuid import uuid4 as UUID

from . import screen


class Renderer(object):
	def __init__(self, gameObject):
		self.gameObject = gameObject
		self.layer = 0


class GameObject(object):
	def __init__(self, game):
		self.game = game
		self.uuid = UUID().hex
		self.game.gameObjects[self.uuid] = self
		self.start()

	def __del__(self):
		if self.uuid is not None:
			del self.game.gameObjects[self.uuid]
			self.uuid = None

	def __repr__(self):
		return self.__class__.__name__

	def destroy(self):
		self.__del__()

	def start(self):
		pass

	def update(self):
		pass

	def late_update(self):
		pass

	def fixed_update(self):
		pass

	def render(self):
		pass


class DebugLog(GameObject):
	def start(self):
		self.enabled = False
		self.log = []

	def update(self):
		c = self.game.getKeyRaw()
		if c == 96:
			self.enabled = not self.enabled
		if self.enabled:
			for index, message in enumerate(self.log):
				self.game.screen.addstr(0 + index, 0, message)


class Game(object):
	def __init__(self):
		self.screen = screen.Screen()
		self.screen.inpdelay(False)
		self.screen.autoflushinp(True)
		self.delta_time = 1.0 / 60.0
		self.fixed_delta_time = 1.0 / 20.0
		self.gameObjects = {}
		self.start_time = time()
		self.__last_time = self.start_time
		self.__last_fixed_time = self.start_time
		self.__running = True
		self.__char = -1
		self.__logger = None

		try:
			self.start()
			self.loop = asyncio.new_event_loop()
			asyncio.set_event_loop(self.loop)
			# loop = asyncio.get_event_loop()
			tasks = [asyncio.ensure_future(self.__update__()), asyncio.ensure_future(self.__fixed_update__())]
			self.loop.run_until_complete(asyncio.wait(tasks))
		except KeyboardInterrupt:
			pass
		finally:
			self.close()
			pending = asyncio.Task.all_tasks()
			self.loop.run_until_complete(asyncio.gather(*pending))
			self.loop.stop()
			self.loop.close()

	async def __update__(self):
		try:
			while self.__running:
				t = time()
				self.delta_time = t - self.__last_time
				self.__last_time = t
				self.__char = self.screen.getch()
				self.update()
				UUIDs = self.gameObjects.copy().values()
				for gameObject in UUIDs:
					gameObject.update()
				for gameObject in UUIDs:
					gameObject.late_update()
				self.late_update()
				await asyncio.sleep(1.0 / 30.0)
		except Exception as e:
			self.close()
			raise e

	async def __fixed_update__(self):
		try:
			while self.__running:
				t = time()
				self.fixed_delta_time = t - self.__last_fixed_time
				self.__last_fixed_time = t
				self.fixed_update()
				for gameObject in self.gameObjects.copy().values():
					gameObject.fixed_update()
				await asyncio.sleep(1.0 / 20.0)
		except Exception as e:
			self.close()
			raise e

	def instantiate(self, gameObject=GameObject):
		return gameObject(self)

	def getKeyRaw(self):
		return self.__char

	def getKey(self, key):
		return key == self.__char

	def triggerKey(self, key):
		self.__char = key

	def close(self):
		if self.__running:
			self.__running = False
			self.screen.close(False)

	def start(self):
		pass

	def update(self):
		pass

	def late_update(self):
		pass

	def fixed_update(self):
		pass

	def log(self, message):
		if self.__logger is None:
			self.__logger = self.instantiate(DebugLog)
		if len(self.__logger.log) == 5:
			self.__logger.log = self.__logger.log[1:]
		self.__logger.log.append(message)


__all__ = ["GameObject", "Game"]

