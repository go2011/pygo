from abc import ABCMeta	# imports to add oop features
from constants import * # imports for all projects

class Game:
	__metaclass__ = ABCMeta

	'''
	size is 2 tuple (width, height), rules is aclass implementing the rules.py methods,
	and timer is a class implementing the game_timer.py methods
	'''

	def __init__(self, size, rules, timer, onmove, onend):
		self._size = size
		self._rules = rules(self)
		self._timer = timer()

		# event handlers
		self._onmove = onplay
		self._onend = onend

	# pretty self explanatory
	def play_move(self, point, color):
		valid = self._rules.validate(point, color)
		assert valid is 0
		reasurance = self._rules.enforce(point, color)
		return valid

	# note pass is reserved word in python
	def pass_move(self, color):
		# not sure whether responsibility should be delegated to rules object
		pass

	def resign(self, color):
		pass




