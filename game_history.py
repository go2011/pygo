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

	def __init__(self, game_history, index, state=None):
		self._game_history = game_history
		self._index = index
		self._state = state

		if state is None:
			self._rendered = False
		else:
			self._rendered = True

	# does not use matrix notation ( instance[y, x] with indexes starting at 1)
	# instead uses instance[x, y] with indexes starting at 0,
	def __getitem__(self, item):

		if type(item) == tuple:

			if not self._rendered:
				self.render()
			return self._game_history.get(self._state, item)
		else:
			raise IndexError("Invalid index for board position: %s" % item)

	def __iter__(self):
		return self.points()


	# mainly for debugging
	def __str__(self):

		if not self.exists:
			return "Deleted or never existed"

		col_joiner = "\n"
		col_list = []
		row_joiner = " "
		row_list = []

		for x, y in self.points(order=(Y,X)):
			row_list.append(str(self[x, y]))

			if x >= self.size[X] - 1:
				string = row_joiner.join(row_list)
				col_list.append(string)
				row_list = []

		return col_joiner.join(col_list)

	# gives tuple of the width, height, etc (if applicable)
	@property
	def size(self):
		return self._game_history.size

	@property
	def exists(self):
		return 0 <= self._index < len(self._game_history)

	# gives whether the frame is rendered
	@property
	def rendered(self):
		return self._rendered

	def render(self):
		self._state = self._game_history.get_state(self._index)
		self._rendered = True

	def points(self, order=(Y, X)):
		d1, d2 = order
		a = [None,None]
		for i1 in range(0, self.size[d1]):
			a[d1] = i1 
			for i2 in range(0, self.size[d2]):
				a[d2] = i2
				yield a[X], a[Y]




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

	# class variables
	_allowable_colors = set([WHITE, BLACK])
	default_game_frame_class = GameFrame
	default_cache_frequency = 5

	def __init__(self, width, height, game_frame_class=default_game_frame_class):
		# set class to instantiate all game frame objects from
		self._game_frame_class = game_frame_class


		# list tracking each change in the board contents
		self._changes = []

		# stores a number of exact game states at certain points, for quicker access
		self._cache = {}

		# size of each board
		self._width = width
		self._height = height

		# must call after setting _width, _height
		self._first = self._empty_board()
		self._last = self._first
		self._current = self._empty_board()

		self._cache_frequency = self.default_cache_frequency
		self._store(0, self._first)

	def __getitem__(self, index):
		if type(index) == int:
			if index < 0:
				index += len(self)

			return self._game_frame(index, None)
		else:
			raise IndexError("Invalid move number: %s" % index)

	def __len__(self):
		# game will always a number of states 1 greater than the number of changes
		return len(self._changes) + 1

	@property
	def size(self):
		return self._width, self._height


	@property
	def cache_frequency(self):
		return self._cache_frequency

	# set cache frequency in real time (to optimize resource use)
	@cache_frequency.setter
	def cache_frequency(self, value):
		board = self.get_state(0)
		length = len(self)
		for i in range(0, length):
			if i % value == 0:
				self._cache[i] = board
			else:
				if i in self._cache:
					del self._cache[i]

			if i == length - 1:
				break

			changes = self._changes[i]
			board = self._forward(board, changes)

		self._cache_frequency = value

	def _game_frame(self, index, state):
		game_frame = self._game_frame_class(self, index, state)
		return game_frame

	def _empty_board(self):
		return {}

	def _store(self, index, board):
		self._cache[index] = board


	def _uncache(self, index):
		if index in self._cache:
			del self._cache[index]


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

			if add == EMPTY and key in future:
				del future[key]
			else:
				future[key] = add

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

			if add == EMPTY and key in future:
				del future[key]
			else:
				future[key] = add

		return future


	# returns difffernce between the two boards
	def _difference(self, in_board, out_board):
		changes = {}
		for x in range(0, self._width):
			for y in range(0, self._height):
				
				point = x, y
				key = self.hash_key(point)

				original = self.get(in_board, point)
				new = self.get(out_board, point)

				if original == new:
					continue
				else:
					changes[key] = BASE * original + new


		return changes


	# calculates board state at out index based on input board state and its index
	def _compute_game_state(self, current_board, in_index, out_index):
		length = len(self._changes)
		board = copy_board(current_board)

		if in_index < out_index:
			for i in range(in_index, out_index):
				changes = self._changes[i]
				self._forward(board, changes, copy=False)
		elif in_index > out_index:
			for i in range(in_index - 1, out_index - 1, -1):
				changes = self._changes[i]
				self._backward(board, changes, copy=False)

		return board


	# condenses point tuple down to unique keyable integer
	def hash_key(self, point):
		x, y = point
		return self._width * y + x

	# returns integer back to point tuple
	def unhash(self, integer):
		x = integer % self._width
		y = integer // self._width
		return x, y


	# to isolate input validation
	def valid_point(self, point):
		return 0 <= point[X] < self._width and 0 <= point[Y] < self._height

	def valid_color(self, color):
		return color in self._allowable_colors

	def valid_index(self, index):
		return 0 <= index < len(self)

	# go to next move
	def close(self):
		diff = self._difference(self._last, self._current)

		self._last = self._current
		self._current = copy_board(self._last)
		self._changes.append(diff)

		index = len(self) - 1
		if index % self._cache_frequency == 0:
			self._store(index, self._last)

	# takes parameters of tuples (point, color)
	# where point is a tuple (x, y)
	# and adds them to current game state
	def put(self, *stones):
		for point, color in stones:
			assert self.valid_point(point)
			assert self.valid_color(color)

			key = self.hash_key(point)		
			self._current[key] = color

	# sets given points to empty
	def take(self, *points):
		for point in points:
			assert self.valid_point(point)

			key = self.hash_key(point)
			if key in self._current:
				del self._current[key]

	def pop(self):
		assert len(self._current) == 0
		self._uncache(len(self) - 1)
		self._changes.pop()



	def get(self, board, point):
		
		if not 0 <= point[X] < self._width:
			return OFFBOARD

		if not 0 <= point[Y] < self._height:
			return OFFBOARD

		key = self.hash_key(point)
		if not key in board:
			return EMPTY
		else:
			return board[key]


	# chooses optimal calculation function based on relative distance
	# feature not yet implemented
	def get_state(self, index):
		assert 0 <= index < len(self), "Invalid index"

		found = False
		if index in self._cache:
			out_board = self._cache[index]
			found = True

		if not found:
			origin = index - index % self._cache_frequency
			print index, origin
			in_board = self._cache[origin]
			out_board = self._compute_game_state(in_board, origin, index)
			found = True

		return copy_board(out_board)





