from copy import copy as copy_board
from constants import *

class GameHistory:

	def __init__(self, width, height):
		# list tracking each change in the board contents
		self._changes = []

		# dimensions of each board
		self._width = width
		self._height = height

		# must call after setting _width, _height
		self._last = self._empty_board()
		self._current = self._empty_board()

	def __getitem__(self, index):
		if type(index) == int:
			return GameFrame(self, index)
		else:
			raise IndexError("Invalid move number: %s" % index)

	def _empty_board(self):
		return [x[:] for x in [[EMPTY] * self._width] * self._height]

	# condenses point tuple down to unique keyable integer
	def _hash(self, point):
		x, y = point
		return self._width * y + x

	# returns integer back to point tuple
	def _unhash(self, integer):
		x = integer % self._width
		y = integer // self._width
		return x, y

	def _forward(self, current, changes, copy=True):
		if copy:
			future = copy_board(current)
		else:
			future = current

		for key in changes:
			change = changes[key]

			# extract removed and added colors from 2 digit number
			remove = change // BASE
			add = change % BASE

			x, y = self._unhash(key)
			future[x][y] = add

		return future

	def _backward(self, current, changes, copy=True):
		if copy:
			future = copy_board(current)
		else:
			future = current
		for key in changes:
			change = changes[key]

			# reverse order
			add = change // BASE
			remove = change % BASE

			x, y = self._unhash(key)
			future[x][y] = add

		return future

	# returns difffernce between the two boards
	def _diff(self, in_board, out_board):
		changes = {}
		for i in range(0, self._width):
			for j in range(0, self._height):
				
				original, new = inb[i][j], outb[i][j]
				if original == new:
					continue
				else:
					key = self._hash((i,j))

					# first digit represents color removed
					# second color added
					changes[key] = BASE * original + new

		return changes

	# get state at index starting from left
	def _get_state_left(self, index):
		board = self._empty_board()
		for i in range(0, index):
			self._forward(board, self._changes[i], copy=False)




	def close(self):
		diff = self._diff(self._last, self._current)

		self._last = self._current
		self._current = copy_board(self._last)
		self._changes.append(diff)


	# takes parameters of tuples (point, color)
	# where point is a tuple (x, y)
	def put(self, *stones):
		for point, color in stones:
			x, y = point
			self._current[x][y] = color

	def take(self, *points):
		for x, y in points:
			self._current[x][y] = EMPTY

	# chooses optimal calculation function based on relative distance
	# feature not yet implemented
	def get_state(self, index):
		return self._get_state_left(index)
		



# acts as a proxy between you and a specific game state
class GameFrame:
	def __init__(self, game_history, index):
		this._game_history = game_history
		this._index = index
		this._rendered = False
		this._state = None

	def __getitem__(self, item):
		if type(item) == tuple:
			x, y = item

			if not this._rendered:
				this._state = this._game_history.get_state(this._index)
				this._rendered = True

			return this._state[x][y]
		else:
			raise IndexError("Invalid index for board position: %s" % item)




