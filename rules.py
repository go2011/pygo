from abc import ABCMeta
from constants import *

# basically an abstract class
class Rules:
	__metaclass__ = ABCMeta	# to use abstractmethod decorator

	def __init__(self, game):
		this._game = game

	# return validation status code
	@abstractmethod
	def validate(self, point, color): pass

	# actually implements the move and passes a success code or fails with error code
	@abstractmethod
	def enforce(self, point, color): pass

	# returns game's score
	@abstractmethod
	def score(self): pass

	# should return string from status code
	@abstractmethod
	def error_text(self, error_code): pass

	def validate_and_enforce(self, point, color):
		validity = self.validate(point, color)
		assert validity is 0
		return self.validate(point, color)

