# here I define stuff that will come in handy throughout the project

# best to use names rather than values as they may change
EMPTY = 0
BLACK = 1
WHITE = 2
OFFBOARD = 3

# constants to reffer to standard indexes in 3 dimensional grid (currently working only on 2d)
# always use in square [] to standardize and increase readability
X = WIDTH = 0
Y = HEIGHT = 1
#Z = DEPTH = 2

COLUMN = 0
ROW = 1

# base to use when storing info digitally
# must be greater than all the constants
BASE = 10

def alternate_color():
	color = BLACK
	while True:
		yield color
		color = opposite_color(color)

def opposite_color(color):
	return BLACK if color is WHITE else WHITE


