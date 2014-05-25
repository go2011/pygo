# here I define stuff that will come in handy throughout the project

# best to use names rather than values as they may change
BLACK = 0
WHITE = 1
EMPTY = 2
OFFBOARD = 3

def alternate_color():
	color = BLACK
	while True:
		yield color
		color = opposite_color(color)

def opposite_color(color):
	return BLACK if color is WHITE else WHITE


