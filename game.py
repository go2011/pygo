from abc import ABCMeta	# imports to add oop features
from constants import * # imports for all projects

class Game:
	'''
	size is 2 tuple (width, height), rules is aclass implementing the rules.py methods,
	and timer is a class implementing the game_timer.py methods
	'''
	def __init__(self, size, rules, timer):
		self._size = size
		self._rules = rules(self)
		self._timer = timer()

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



