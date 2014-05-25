from abc import ABCMeta
from constants import *

class GameTimer:
	__metaclass__ = ABCMeta
	# in ms
	PERIOD = 1000


	def __init__(self, interval=5):
		self.interval = interval
		self.timeout_listeners = []
		self.interval_listeners = []
		self.turn_change_listeners = []
		self.started = False
		self._turn = BLACK # set using .turn property  (instance.turn = WHITE)

	
	def unpause(self):
		self.started = True

	def pause(self):

	# best way to alternate turns
	def next(self):
		self.turn = opposite_color(self.turn)

	# in cases such as handicaps where white goes first, set turn to 0
	# syntax
	@property
	def turn(self):
	    return self._turn
	@turn.setter
	def turn(self, value):
		if value == self._turn:
			return
		else:
			self._turn = value
			self._on_turn_change(value)
			time
			for listener in self.turn_change_listeners:
				listener()
	
	@abstractmethod
	def _on_turn_change(self, color): pass

	# called every period
	@abstractmethod
	def tick(self): pass

	# gives time left
	@abstractmethod
	def time_left(self): pass