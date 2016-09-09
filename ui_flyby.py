#!/usr/bin/python
#ui_flyby.py

import os
import time

import pygame

import controller
import model
import ui

import signal

#this is here to keep the app from crashing immediatly when launched by systemd 
def dont_quit(signal, frame):
	print 'Catch signal: {}'.format(signal)
 
signal.signal(signal.SIGHUP, dont_quit)

CLICK_DEBOUNCE  = 0.4	# Number of seconds to wait between clicks events. Set
						# to a few hunded milliseconds to prevent accidental
						# double clicks from hard screen presses.

# Font size configuration.
MAIN_FONT = 34
NUM_FONT  = 50
SMALL_FONT = 28

# Color configuration (RGB tuples, 0 to 255).
MAIN_BG        = (  255,   255,   255) # Black
INPUT_BG       = ( 60, 255, 255) # Cyan-ish
INPUT_FG       = (  0,   0,   0) # Black
CANCEL_BG      = (255,  90,  90) # Light red
ACCEPT_BG      = ( 90, 255,  90) # Light green
BUTTON_BG      = ( 255,  255,  255) # Dark gray
BUTTON_FG      = (128, 128, 128) # White
BUTTON_BORDER  = (200, 200, 200) # White/light gray
INSTANT_LINE   = (  0, 255, 128) # Bright yellow green.
PLANE_TEXT_NUMBER = (128, 128, 128)
PLANE_TEXT_FG  = BUTTON_FG
PLANE_TEXT_BG  = MAIN_BG
PLANE_TEXT_DETAIL_FG = INPUT_FG
PLANE_TEXT_DETAIL_BG = MAIN_BG

# Define gradient of colors for the waterfall graph.  Gradient goes from blue to
# yellow to cyan to red.
WATERFALL_GRAD = [(0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)]

# Configure default UI and button values.
ui.MAIN_FONT = MAIN_FONT
ui.SMALL_FONT = SMALL_FONT
ui.Button.fg_color     = BUTTON_FG
ui.Button.bg_color     = BUTTON_BG
ui.Button.border_color = BUTTON_BORDER
ui.Button.padding_px   = 2
ui.Button.border_px    = 2


if __name__ == '__main__':
	# Initialize pygame and SDL to use the PiTFT display and touchscreen.
	os.putenv('SDL_VIDEODRIVER', 'fbcon')
	os.putenv('SDL_FBDEV'      , '/dev/fb1')
	os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
	os.putenv('SDL_MOUSEDEV'   , '/dev/input/event0')
	pygame.display.init()
	pygame.font.init()
	pygame.mouse.set_visible(False)
	# Get size of screen and create main rendering surface.
	size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	screen = pygame.display.set_mode(size, pygame.FULLSCREEN)


	fsmodel = model.UIFlyByModel(size[0], size[1])
	fscontroller = controller.UIFlyByController(fsmodel)


	# Main loop to process events and render current view.
	lastclick = 0
	tracking = 0
	while True:
		# Process any events (only mouse events for now).
		for event in pygame.event.get():
			if event.type is pygame.MOUSEBUTTONDOWN \
				and (time.time() - lastclick) >= CLICK_DEBOUNCE:
				lastclick = time.time()
				fscontroller.current().click(pygame.mouse.get_pos())
				tracking = 1
			elif event.type is pygame.MOUSEBUTTONUP:
				tracking = 0

			if event.type is pygame.MOUSEMOTION \
				and tracking == 1 and (time.time() - lastclick) >= CLICK_DEBOUNCE * 0.1:
				fscontroller.current().mouse_move(pygame.mouse.get_pos())

		# Update and render the current view.
		fscontroller.current().render(screen)
		pygame.display.update()