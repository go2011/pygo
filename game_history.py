from copy import copy as copy_board
from constants import *


# acts as a proxy between you and a specific game state
class GameFrame:

	'''
	Instances of this class act as proxies between users of the game states
	and the actual game state, this virtualization, allows for deffered processing
	and could significantly improve performance. This should only be used internally
	By the GameHistory instances.

	usage:

	# gets _GameFrame object for the board's 5th state (state after 4 moves)
	board_state_instance = game_history_instance.get_state(5)

	# indexes go up to 18 on 19x19 board
	x = 3
	y = 18

	point = x, y
	point_contents = board_state_instance[point]

	#	or

	point_contents = board_state_instance[x, y]
	'''

	def __init__(self, game_history, index):
		self._game_history = game_history
		self._index = index
		self._rendered = False
		self._state = None

	# gives tuple of the width, height, etc (if applicable)
	@property
	def dimensions(self):
		return self._game_history.dimensions

	# does not use matrix notation ( instance[y, x] with indexes starting at 1)
	# instead uses instance[x, y] with indexes starting at 0,
	def __getitem__(self, item):
		if type(item) == tuple:
			x, y = item

			if not self._rendered:
				self._state = self._game_history.get_state(self._index)
				self._rendered = True

			return self._state[x][y]
		else:
			raise IndexError("Invalid index for board position: %s" % item)



class GameHistory:

	'''
	Instances of GameHistory allow you to seamlessly browse through the game step by step
	without having the user having to compute the state of the game. The module introduces
	several optimizations to limit RAM and CPU cycles, but allows the user to access each
	sequencial state of the game similar to a list. Ultimately this class should be flexible
	enough to allow for any variation of the game which can be boiled down to 2d cartesian
	coordinates. A toroidal go board (no edges) can easily be achieved by changing the default
	GameFrame object, and overriding __getitem__ in the custom game frame class.

	usage:

	width = 19
	height = 19

	game_history_instance = GameHistory(width, height)

	# ...

	# putting stones on board
	point = (18, 18) # corner of board
	game_history_instance.put(  (point, BLACK)  )
	game_history_instance.put(  ((4, 5), WHITE),  ((4, 3), BLACK)  ) # takes unlimited arguments


	# clearing spaces
	point = (4, 5)

	# clears the last two stones put down on board
	game_history_instance.take(point, (4, 3)) # also takes unlmited arguments


	# ends recording of current turn, adds new frame
	game_history_instance.close()

	# do same types of steps as above for next move ...


	# to query:

	# gets game state as true list 5 states (4 moves) in to the game
	board_list_2d = game_history_instance.get_state(5)

	# returns a virtual list representation of same game state
	game_frame = game_history_instance[5]



	'''

	default_game_frame_class = GameFrame

	def __init__(self, width, height, game_frame_class=default_game_frame_class):
		# set class to instantiate all game frame objects from
		self._game_frame_class = game_frame_class


		# list tracking each change in the board contents
		self._changes = []

		# dimensions of each board
		self._width = width
		self._height = height

		# must call after setting _width, _height
		self._first = self._empty_board()
		self._last = self._empty_board()
		self._current = self._empty_board()

	def __getitem__(self, index):
		if type(index) == int:
			if index < 0:
				index += len(self)

			return self._game_frame_class(self, index)
		else:
			raise IndexError("Invalid move number: %s" % index)

	def __len__(self):
		# game will always a number of states 1 greater than the number of changes
		return len(self._changes) + 1

	@property
	def dimensions(self):
		return self._width, self._height

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
	def _difference(self, in_board, out_board):
		changes = {}
		for i in range(0, self._width):
			for j in range(0, self._height):
				
				original, new = in_board[i][j], out_board[i][j]
				if original == new:
					continue
				else:
					key = self._hash((i,j))

					# first digit represents color removed
					# second color added
					changes[key] = BASE * original + new

		return changes


	# calculates board state at out index based on input board state and its index
	def _compute_game_state(self, current_board, in_index, out_index):
		length = len(self._changes)
		board = copy_board(current_board)

		if in_index < out_index:
			for i in range(in_index, out_index):
				changes = self._changes[i]
				self._forward(board, changes)
		elif in_index > out_index:
			for i in range(in_index - 1, out_index - 1, -1):
				changes = self._changes[i]
				self._backward(board, changes)

		return board


	def close(self):
		diff = self._difference(self._last, self._current)

		self._last = self._current
		self._current = copy_board(self._last)
		self._changes.append(diff)


	# takes parameters of tuples (point, color)
	# where point is a tuple (x, y)
	# and adds them to current game state
	def put(self, *stones):
		for point, color in stones:
			x, y = point
			self._current[x][y] = color

	# sets given points to empty
	def take(self, *points):
		for x, y in points:
			self._current[x][y] = EMPTY

	# chooses optimal calculation function based on relative distance
	# feature not yet implemented
	def get_state(self, index):
		length = len(self)

		# if index is closer to left side
		if index < length - index:
			in_board = self._first
			out_board = self._compute_game_state(in_board, 0, index)
		else:
			in_board = self._last
			out_board = self._compute_game_state(in_board, length, index)
		
		return out_board



