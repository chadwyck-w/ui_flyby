import pygame


# Alignment constants.
ALIGN_LEFT   = 0.0
ALIGN_TOP    = 0.0
ALIGN_CENTER = 0.5
ALIGN_RIGHT  = 1.0
ALIGN_BOTTOM = 1.0

def align(child, parent, horizontal=ALIGN_CENTER, vertical=ALIGN_CENTER,
	hpad=0, vpad=0):
	"""Return tuple of x, y coordinates to render the provided child rect 
	aligned inside the parent rect using the provided horizontal and vertical
	alignment.  Each alignment value can be ALIGN_LEFT, ALIGNT_TOP, ALIGN_CENTER,
	ALIGN_RIGHT, or ALIGN_BOTTOM.  Can also specify optional horizontal padding
	(hpad) and vertical padding (vpad).
	"""
	cx, cy, cwidth, cheight = child
	px, py, pwidth, pheight = parent
	return (px+(horizontal*pwidth-horizontal*cwidth)+hpad,
			py+(vertical*pheight-vertical*cheight)+vpad)

font_cache = {}
def get_font(size):
	"""Get font of the specified size.  Will cache fonts internally for faster
	repeated access to them.
	"""
	if size not in font_cache:
		font_cache[size] = pygame.font.Font(None, size)
	return font_cache[size]

def render_text(text, size=34, fg=(255, 255, 255), bg=(0, 0, 0)):
	"""Render the provided text to a surface which is returned."""
	if bg is not None:
		# Optimized case when the background is known.
		return get_font(size).render(text, True, fg, bg)
	else:
		# Less optimized case with transparent background.
		return get_font(size).render(text, True, fg)

def render_flight_text(text, size=34, fg=(90, 90, 90)):
	return get_font(size).render(text, True, fg)


class FlyingButton(object):
		# Default color and other button configuration.  Can override these values
	# to change all buttons.
	fg_color     = (45, 45, 45)
	bg_color     = (255, 0, 0)
	dest_bg_color = (64, 64, 64)

	font_size    = 34
	font_size_small = 22

	def __init__(self, rect, click=None, flight=None, bg_color=None):
		"""Create a button at the provided rect (tuple of x, y, width, height)
		and with the provided text.  Can specify an optional click handler which
		is a function that takes one parameter (the clicked button) and will be
		executed when the button is clicked.
		"""
		self.bg_color = bg_color if bg_color is not None else self.bg_color
		self.border_px = 1
		self.click_func = click
		self.click_func_flight = flight
		# Determine rendered dimensions based on padding.
		# x, y, width, height = rect
		# x += self.padding_px
		# y += self.padding_px
		# width -= 2*self.padding_px
		# height -= 2*self.padding_px
		# self.rect = (x, y, width, height)
		self.rect = rect

	def render(self, screen):
		"""Render the button on the provided surface."""
		#screen.fill(self.bg_color, self.rect)
		#pygame.draw.rect(screen, self.bg_color, self.rect, self.border_px)

	def click(self, location):
		"""Click handler will fire the button's click handler if the provided
		location x, y tuple is inside the button.
		"""
		x, y, width, height = self.rect
		mx, my = location
		if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) \
			and self.click_func is not None:
			self.click_func(self, flight=self.click_func_flight)

class AirplaneButton(object):
		# Default color and other button configuration.  Can override these values
	# to change all buttons.
	fg_color     = (45, 45, 45)
	bg_color     = (255, 255, 255)
	dest_bg_color = (64, 64, 64)
	border_color = (200, 200, 200)
	padding_px   = 1
	border_px    = 1
	font_size    = 34
	font_size_small = 22

	def __init__(self, rect, text, bottom_text, click=None, flight=None, font_size=None, font_size_small=None, bg_color=None):
		"""Create a button at the provided rect (tuple of x, y, width, height)
		and with the provided text.  Can specify an optional click handler which
		is a function that takes one parameter (the clicked button) and will be
		executed when the button is clicked.
		"""
		self.text = text
		self.bg_color = bg_color if bg_color is not None else self.bg_color
		self.font_size = font_size if font_size is not None else self.font_size
		self.font_size_small = font_size_small if font_size_small is not None else self.font_size_small
		self.click_func = click
		self.click_func_flight = flight
		# Determine rendered dimensions based on padding.
		x, y, width, height = rect
		x += self.padding_px
		y += self.padding_px
		width -= 2*self.padding_px
		height -= 2*self.padding_px
		self.rect = (x, y, width, height)
		# Draw label centered in the button for quick rendering later.
		self.label = render_text(text, size=self.font_size, fg=self.fg_color,
			bg=self.bg_color)
		self.label_pos = align(self.label.get_rect(), self.rect, horizontal=ALIGN_LEFT, vertical=ALIGN_TOP, hpad=15, vpad=10)

		self.sub_label = render_text(bottom_text, size=self.font_size_small, fg=self.fg_color,
			bg=self.bg_color)
		self.sub_label_pos = align(self.sub_label.get_rect(), self.rect, horizontal=ALIGN_LEFT, vertical=ALIGN_BOTTOM, hpad=15, vpad=-5)

	def render(self, screen):
		"""Render the button on the provided surface."""
		screen.fill(self.bg_color, self.rect)
		#pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
		screen.blit(self.label, self.label_pos)
		screen.blit(self.sub_label, self.sub_label_pos)

	def click(self, location):
		"""Click handler will fire the button's click handler if the provided
		location x, y tuple is inside the button.
		"""
		x, y, width, height = self.rect
		mx, my = location
		if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) \
			and self.click_func is not None:
			self.click_func(self, flight=self.click_func_flight)

class Button(object):
	# Default color and other button configuration.  Can override these values
	# to change all buttons.
	fg_color     = (225, 225, 225)
	bg_color     = (60, 60, 60)
	border_color = (200, 200, 200)
	padding_px   = 2
	border_px    = 2
	font_size    = 33

	def __init__(self, rect, text, click=None, font_size=None, bg_color=None):
		"""Create a button at the provided rect (tuple of x, y, width, height)
		and with the provided text.  Can specify an optional click handler which
		is a function that takes one parameter (the clicked button) and will be
		executed when the button is clicked.
		"""
		self.text = text
		self.bg_color = bg_color if bg_color is not None else self.bg_color
		self.font_size = font_size if font_size is not None else self.font_size
		self.click_func = click
		# Determine rendered dimensions based on padding.
		x, y, width, height = rect
		x += self.padding_px
		y += self.padding_px
		width -= 2*self.padding_px
		height -= 2*self.padding_px
		self.rect = (x, y, width, height)
		# Draw label centered in the button for quick rendering later.
		self.label = render_text(text, size=self.font_size, fg=self.fg_color,
			bg=self.bg_color)
		self.label_pos = align(self.label.get_rect(), self.rect)

	def render(self, screen):
		"""Render the button on the provided surface."""
		screen.fill(self.bg_color, self.rect)
		pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
		screen.blit(self.label, self.label_pos)

	def click(self, location):
		"""Click handler will fire the button's click handler if the provided
		location x, y tuple is inside the button.
		"""
		x, y, width, height = self.rect
		mx, my = location
		if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) \
			and self.click_func is not None:
			self.click_func(self)

class FlyingButtons(object):
	def __init__(self):
		self.buttons = []

	def add(self, rect, **kwargs):
		"""Add a Button to the grid at the specified row and col position in
		the grid.  Row and col are 0-based indexes.  Buttons can span multiple
		rows and columns by providing optional rowspan and colspan parameters.
		Any other keyword arguments are passed to the Button constructor.
		"""
		self.buttons.append(FlyingButton(rect, **kwargs))

	def render(self, screen):
		"""Render buttons on the provided surface."""
		# Render buttons.
		for button in self.buttons:
			button.render(screen)

	def click(self, location):
		"""Handle click events at the provided location tuple (x, y) for all the
		buttons.
		"""
		for button in self.buttons:
			button.click(location)

class AirplaneButtonGrid(object):
	def __init__(self, width, height, cols, rows):
		"""Create grid of buttons with the provided total width and height in
		pixels and subdivided into cols x rows equally sized buttons.
		"""
		self.col_size = width / cols
		self.row_size = height / rows
		self.buttons = []

	def add(self, col, row, text, bottom_text, rowspan=1, colspan=1, **kwargs):
		"""Add a Button to the grid at the specified row and col position in
		the grid.  Row and col are 0-based indexes.  Buttons can span multiple
		rows and columns by providing optional rowspan and colspan parameters.
		Any other keyword arguments are passed to the Button constructor.
		"""
		x = col*self.col_size
		y = row*self.row_size
		width = colspan*self.col_size
		height = rowspan*self.row_size
		self.buttons.append(AirplaneButton((x,y,width,height), text, bottom_text, **kwargs))

	def render(self, screen):
		"""Render buttons on the provided surface."""
		# Render buttons.
		for button in self.buttons:
			button.render(screen)

	def click(self, location):
		"""Handle click events at the provided location tuple (x, y) for all the
		buttons.
		"""
		for button in self.buttons:
			button.click(location)

class ButtonGrid(object):
	def __init__(self, width, height, cols, rows):
		"""Create grid of buttons with the provided total width and height in
		pixels and subdivided into cols x rows equally sized buttons.
		"""
		self.col_size = width / cols
		self.row_size = height / rows
		self.buttons = []

	def add(self, col, row, text, rowspan=1, colspan=1, **kwargs):
		"""Add a Button to the grid at the specified row and col position in
		the grid.  Row and col are 0-based indexes.  Buttons can span multiple
		rows and columns by providing optional rowspan and colspan parameters.
		Any other keyword arguments are passed to the Button constructor.
		"""
		x = col*self.col_size
		y = row*self.row_size
		width = colspan*self.col_size
		height = rowspan*self.row_size
		self.buttons.append(Button((x,y,width,height), text, **kwargs))

	def render(self, screen):
		"""Render buttons on the provided surface."""
		# Render buttons.
		for button in self.buttons:
			button.render(screen)

	def click(self, location):
		"""Handle click events at the provided location tuple (x, y) for all the
		buttons.
		"""
		for button in self.buttons:
			button.click(location)