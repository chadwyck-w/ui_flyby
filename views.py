# FreqShow application views.
# These contain the majority of the application business logic.
# Author: Tony DiCola (tony@tonydicola.com)
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import math
import sys

import numpy as np
import pygame

import ui_flyby
import ui

import os.path

class ViewBase(object):
	"""Base class for simple UI view which represents all the elements drawn
	on the screen.  Subclasses should override the render, and click functions.
	"""

	def render(self, screen):
		pass

	def click(self, location):
		pass

	def mouse_move(self, location):
		pass

	def view_showing(self):
		pass

class MessageDialog(ViewBase):
	"""Dialog which displays a message in the center of the screen with an OK
	and optional cancel button.
	"""

	def __init__(self, model, text, accept, cancel=None):
		self.accept = accept
		self.cancel = cancel
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(3, 4, 'OK', click=self.accept_click, 
			bg_color=ui_flyby.ACCEPT_BG)
		if cancel is not None:
			self.buttons.add(0, 4, 'CANCEL', click=self.cancel_click, 
				bg_color=ui_flyby.CANCEL_BG)
		self.label = ui.render_text(text, size=ui_flyby.NUM_FONT,
			fg=ui_flyby.BUTTON_FG, bg=ui_flyby.MAIN_BG)
		self.label_rect = ui.align(self.label.get_rect(),
			(0, 0, model.width, model.height))

	def render(self, screen):
		# Draw background, buttons, and text.
		screen.fill(ui_flyby.MAIN_BG)
		self.buttons.render(screen)
		screen.blit(self.label, self.label_rect)

	def click(self, location):
		self.buttons.click(location)

	def accept_click(self, button):
		self.accept()

	def cancel_click(self, button):
		self.cancel()

class NumberDialog(ViewBase):
	"""Dialog which asks the user to enter a numeric value."""

	def __init__(self, model, label_text, unit_text, initial='0', accept=None,
		cancel=None, has_auto=False, allow_negative=False):
		"""Create number dialog for provided model and with given label and unit
		text.  Can provide an optional initial value (default to 0), an accept
		callback function which is called when the user accepts the dialog (and
		the chosen value will be sent as a single parameter), a cancel callback
		which is called when the user cancels, and a has_auto boolean if an
		'AUTO' option should be given in addition to numbers.
		"""
		self.value = str(initial)
		self.unit_text = unit_text
		self.model = model
		self.accept = accept
		self.cancel = cancel
		# Initialize button grid.
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(0, 1, '1', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 1, '2', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 1, '3', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(0, 2, '4', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 2, '5', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 2, '6', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(0, 3, '7', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 3, '8', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 3, '9', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 4, '0', font_size=ui_flyby.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 4, '.', font_size=ui_flyby.NUM_FONT, click=self.decimal_click)
		self.buttons.add(0, 4, 'DELETE', click=self.delete_click)
		if not allow_negative:
			# Render a clear button if only positive values are allowed.
			self.buttons.add(3, 1, 'CLEAR', click=self.clear_click)
		else:
			# Render a +/- toggle if negative values are allowed.
			self.buttons.add(3, 1, '+/-', click=self.posneg_click)
		self.buttons.add(3, 3, 'CANCEL', click=self.cancel_click,
			bg_color=ui_flyby.CANCEL_BG)
		self.buttons.add(3, 4, 'ACCEPT', click=self.accept_click,
			bg_color=ui_flyby.ACCEPT_BG) 
		if has_auto:
			self.buttons.add(3, 2, 'AUTO', click=self.auto_click)
		# Build label text for faster rendering.
		self.input_rect = (0, 0, self.model.width, self.buttons.row_size)
		self.label = ui.render_text(label_text, size=ui_flyby.MAIN_FONT, 
			fg=ui_flyby.INPUT_FG, bg=ui_flyby.INPUT_BG)
		self.label_pos = ui.align(self.label.get_rect(), self.input_rect,
			horizontal=ui.ALIGN_LEFT, hpad=10)

	def render(self, screen):
		# Clear view and draw background.
		screen.fill(ui_flyby.MAIN_BG)
		# Draw input background at top of screen.
		screen.fill(ui_flyby.INPUT_BG, self.input_rect)
		# Render label and value text.
		screen.blit(self.label, self.label_pos)
		value_label = ui.render_text('{0} {1}'.format(self.value, self.unit_text),
			size=ui_flyby.NUM_FONT, fg=ui_flyby.INPUT_FG, bg=ui_flyby.INPUT_BG)
		screen.blit(value_label, ui.align(value_label.get_rect(), self.input_rect,
			horizontal=ui.ALIGN_RIGHT, hpad=-10))
		# Render buttons.
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)

	# Button click handlers follow below.
	def auto_click(self, button):
		self.value = 'AUTO'

	def clear_click(self, button):
		self.value = '0'

	def delete_click(self, button):
		if self.value == 'AUTO':
			# Ignore delete in auto gain mode.
			return
		elif len(self.value) > 1:
			# Delete last character.
			self.value = self.value[:-1]
		else:
			# Set value to 0 if only 1 character.
			self.value = '0'

	def cancel_click(self, button):
		if self.cancel is not None:
			self.cancel()

	def accept_click(self, button):
		if self.accept is not None:
			self.accept(self.value)

	def decimal_click(self, button):
		if self.value == 'AUTO':
			# If in auto gain, assume user wants numeric gain with decimal.
			self.value = '0.'
		elif self.value.find('.') == -1:
			# Only add decimal if none is present.
			self.value += '.'

	def number_click(self, button):
		if self.value == '0' or self.value == 'AUTO':
			# Replace value with number if no value or auto gain is set.
			self.value = button.text
		else:
			# Add number to end of value.
			self.value += button.text

	def posneg_click(self, button):
		if self.value == 'AUTO':
			# Do nothing if value is auto.
			return
		else:
			if self.value[0] == '-':
				# Swap negative to positive by removing leading minus.
				self.value = self.value[1:]
			else:
				# Swap positive to negative by adding leading minus.
				self.value = '-' + self.value

class SettingsList(ViewBase):
	"""Setting list view. Allows user to modify some model configuration."""

	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(ui_flyby.MAIN_BG)
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)

class AllPlanesMap(ViewBase):
	"""The main view for the map of all Planes flying around."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		self.zoom = self.model.tile_zoom
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 6)
		self.buttons.add(5, 0, 'LIST', click=self.controller.change_to_planelist)
		self.buttons.add(5, 1, '+', click=self.zoomIn)
		self.buttons.add(5, 2, '-', click=self.zoomOut)
		self.buttons.add(5, 3, 'SAT', click=self.setSat)
		self.buttons.add(5, 4, 'VECT', click=self.setVect)
		self.buttons.add(5, 5, 'RES', click=self.reset_map)


		self.the_plane = pygame.image.load(os.path.join(os.path.dirname(__file__),"planes","boeing-737-256.png"))
		self.mini_plane = pygame.image.load(os.path.join(os.path.dirname(__file__),"planes","boeing-737-256-mini.png"))

		self.w, self.h = 5, 5
		self.tiles = [[{} for y in xrange(0,self.h)] for x in xrange(0,self.w)]
		self.zoom = self.model.tile_zoomed_out
		self.last_mouse = (0,0)
		self.offset = (0,0)

		self.plane_buttons = None

	def view_showing(self):
		self.reset_map(None)

	def clearTiles(self):
		self.tiles = [[{} for y in xrange(0,self.h)] for x in xrange(0,self.w)]

	def loadTiles(self, center_x,center_y, zoom):
	  for x in range(0,self.w):
		for y in range(0,self.h):
		  new_x = center_x - 2 + x
		  new_y = center_y - 2 + y
		  fileName = os.path.join(os.path.dirname(__file__),"map_images_{}{}/{}_{}.png".format(zoom, self.model.map_folder,new_x, new_y))
		  if self.tiles[x][y].get('name') != fileName:
			  if os.path.isfile(fileName) and os.stat(fileName).st_size != 0:
				self.tiles[x][y]['name'] = fileName
				self.tiles[x][y]['tile'] = pygame.image.load(fileName)
			  else:
			  	tilePos = self.model.num2deg(new_x, new_y, zoom)
			  	if tilePos[0] == 0:
			  		return
			  	if self.model.map_folder == '_vect':
			  		#pass
					self.model.getStreetImage(tilePos[0], tilePos[1], zoom, new_x, new_y)
				else:
					#ass
					self.model.getSatelliteImage(tilePos[0], tilePos[1], zoom, new_x, new_y)

	def blitMap(self, offset_x,offset_y,screen, drag_offset):
		for x in range(0,self.w):
			for y in range(0,self.h):
				if self.tiles[x][y].get('tile'):
					screen.blit(self.tiles[x][y].get('tile'), (drag_offset[0] + offset_x + ((x-2)*256)-128, drag_offset[1] + offset_y + ((y-2)*256)-256 ))

	def blitAllPlanes(self, planes, screen, zoom, centroid, offset, drag_offset):
		self.plane_buttons = ui.FlyingButtons()

		for plane in planes:
			#centroid is at the center of the screen		
			#what is the planes offset from the center in pixels at this zoom?
			plane_offset = self.model.planeOffset(plane.get('lat'), plane.get('lon'), centroid, zoom)
			angledplane = self.rot_center(self.mini_plane, 360-plane.get('track'))
			plane_pos = ((self.model.width/2) - plane_offset[0] - 32, (self.model.height/2) - plane_offset[1] - 32)
			screen.blit(angledplane, ( plane_pos[0] + drag_offset[0], plane_pos[1] + drag_offset[1] ))
			label_flight = ui.render_flight_text(plane.get('flight').encode('utf-8'), fg=ui_flyby.CANCEL_BG, size=ui_flyby.SMALL_FONT)
			screen.blit(label_flight, ( plane_pos[0] - 16.0 + drag_offset[0], plane_pos[1] + 24.0 + drag_offset[1]))

			button_rect = ( plane_pos[0] - 16 + drag_offset[0], plane_pos[1] - 16 + drag_offset[1] , angledplane.get_rect().width * 2, angledplane.get_rect().width * 2 )
			self.plane_buttons.add(button_rect, click=self.controller.change_to_planeMap, flight=plane.get('flight'))

			
	def loadAndBlitMap(self, x,y,offset_x,offset_y, angle, screen, zoom, offset):
		self.loadTiles(x,y, zoom)
		self.blitMap(offset_x,offset_y,screen,offset)

	def rot_center(self, image, angle):
	    """rotate an image while keeping its center and size"""
	    orig_rect = image.get_rect()
	    rot_image = pygame.transform.rotate(image, angle)
	    rot_rect = orig_rect.copy()
	    rot_rect.center = rot_image.get_rect().center
	    rot_image = rot_image.subsurface(rot_rect).copy()
	    return rot_image

	def renderPlanes(self, screen):
		flight_dict = self.model.get_flights()
		if flight_dict and len(flight_dict) > 0:
			flights = [value for key, value in flight_dict.iteritems()]
			centroid = self.model.centroid([(value.get('lat'), value.get('lon')) for value in flights if value.get('lat') != 0])
			tile = self.model.deg2num(centroid.x, centroid.y, self.zoom)
			offset = self.model.getOffset(centroid.x, centroid.y, self.zoom)
			self.loadAndBlitMap(tile[0], tile[1], offset[0], offset[1], None, screen, self.zoom, self.offset)
			self.blitAllPlanes(flights, screen, self.zoom, centroid, offset, self.offset)
		else: #there are no flights now
			centroid = self.model.centroid(None)
			tile = self.model.deg2num(centroid.x, centroid.y, self.zoom)
			offset = self.model.getOffset(centroid.x, centroid.y, self.zoom)
			self.loadAndBlitMap(tile[0], tile[1], offset[0], offset[1], None, screen, self.zoom, self.offset)
			label_flight = ui.render_flight_text("No Flights", size=ui_flyby.MAIN_FONT * 2)
			rect = label_flight.get_rect()
			screen.blit(label_flight, (self.model.width / 2 - rect.width / 2, self.model.height / 2 - ui.MAIN_FONT))

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(ui_flyby.MAIN_BG)
		self.renderPlanes(screen)
		self.buttons.render(screen)
		if self.plane_buttons is not None:
			self.plane_buttons.render(screen)

	def click(self, location):
		#print("click {}" ,location)
		self.last_mouse = location
		self.buttons.click(location)
		if self.plane_buttons is not None:
			self.plane_buttons.click(location)

	def mouse_move(self, location):
		movement = (location[0] - self.last_mouse[0], location[1] - self.last_mouse[1])
		if abs(movement[0]) > 20 or abs(movement[1]) > 20:
			self.offset = (self.offset[0] + movement[0], self.offset[1] + movement[1])
		self.last_mouse = location
		#print("{} {}".format(movement, self.offset))

	def zoomOut(self, button):
		self.zoom = self.zoom - 1
		if self.zoom < self.model.tile_zoomed_out:
			self.zoom = self.model.tile_zoomed_out
		self.clearTiles()
		print("zoomOut " + str(self.zoom))

	def zoomIn(self, button):
		self.zoom = self.zoom + 1
		if self.zoom > self.model.tile_zoom:
			self.zoom = self.model.tile_zoom
		self.clearTiles()
		print("zoomIn " + str(self.zoom))

	def setSat(self, button):
		print("set Sattellite")
		self.model.map_folder = ""

	def setVect(self, button):
		print("set vector map")
		self.model.map_folder = "_vect"

	def reset_map(self, button):
		self.model.map_folder = "_vect"
		self.zoom = self.model.tile_zoomed_out
		self.offset = (0,0)
		self.clearTiles()
		print("reset map")

	def quit_click(self, button):
		self.controller.message_dialog('QUIT: Are you sure?',
			accept=self.quit_accept)

	def quit_accept(self):
		sys.exit(0)

class PlaneMap(ViewBase):
	"""The main view for the map of a Plane flying around."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 6)
		self.buttons.add(5, 0, 'PREV', click=self.controller._change_to_previous)
		self.buttons.add(5, 1, '+', click=self.zoomIn)
		self.buttons.add(5, 2, '-', click=self.zoomOut)
		self.buttons.add(5, 3, 'SAT', click=self.setSat)
		self.buttons.add(5, 4, 'VECT', click=self.setVect)
		self.buttons.add(5, 5, 'RES', click=self.reset_map)
		#self.buttons.add(5, 4, 'X', click=self.quit_click, bg_color=ui_flyby.CANCEL_BG)

		print(os.path.join(os.path.dirname(__file__),"planes","boeing-737-256.png"))

		self.the_plane = pygame.image.load(os.path.join(os.path.dirname(__file__),"planes","boeing-737-256.png"))
		self.mini_plane = pygame.image.load(os.path.join(os.path.dirname(__file__),"planes","boeing-737-256-mini.png"))

		self.zoom = self.model.tile_zoom
		self.w, self.h = 5, 5
		self.tiles = [[{} for y in xrange(0,self.h)] for x in xrange(0,self.w)]
		
	def paintPlaneInfo(self, flight, screen):
		# render text
		plan = flight.get('plan')
		sublables = []
		fromText = "{} {}".format(flight.get('FromAirportLocation'), flight.get('FromAirportCountry')) if flight.get('FromAirportCountry') != "United States" else "{}".format(flight.get('FromAirportLocation'))
		toText = "{} {}".format(flight.get('ToAirportLocation'), flight.get('ToAirportCountry')) if flight.get('ToAirportCountry') != "United States" else "{}".format(flight.get('ToAirportLocation'))
		bottomText = "{} - {}".format(fromText, toText)
		sublables.append(ui.render_flight_text(bottomText, size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))		
		sublables.append(ui.render_flight_text("{} ft".format(flight.get('altitude')), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))
		sublables.append(ui.render_flight_text("{} fpm".format(flight.get('vert_rate')), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))
		sublables.append(ui.render_flight_text(flight.get('area').encode('utf-8'), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))
		sublables.append(ui.render_flight_text( flight.get('status').encode('utf-8'), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))

		sublables.append(ui.render_flight_text( flight.get('typeName'), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))
		sublables.append(ui.render_flight_text("last seen {}".format(flight.get('seen')), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))
		sublables.append(ui.render_flight_text("{} Deg".format(flight.get('track')), size=ui_flyby.SMALL_FONT, fg=ui_flyby.PLANE_TEXT_DETAIL_FG))

		label_flight = ui.render_flight_text(flight.get('OperatorName') if flight.get('OperatorName') else flight.get('flight'), size=ui_flyby.MAIN_FONT * 2)
		label_flight_number = ui.render_flight_text(flight.get('FlightNumber'), size=ui_flyby.MAIN_FONT * 2, fg=ui_flyby.PLANE_TEXT_NUMBER)
		
		screen.blit(label_flight, (10, 10))
		screen.blit(label_flight_number, (self.model.width - label_flight_number.get_rect().width - 10 - self.model.width / 6,
		 ui_flyby.MAIN_FONT * 2 if label_flight.get_rect().width + label_flight_number.get_rect().width > self.model.width - self.model.width / 6 else 10))

		for x in xrange(0,len(sublables)):
			screen.blit(sublables[x], (ui.MAIN_FONT / 2 , ui.MAIN_FONT * 2 + x * ui.SMALL_FONT))

	def clearTiles(self):
		self.tiles = [[{} for y in xrange(0,self.h)] for x in xrange(0,self.w)]

	def loadTiles(self, center_x,center_y, zoom):
	  for x in range(0,self.w):
		for y in range(0,self.h):
		  new_x = center_x - 2 + x
		  new_y = center_y - 2 + y
		  #fileName = "map_images{}/{}_{}.png".format(self.model.map_folder,new_x, new_y)
		  fileName = os.path.join(os.path.dirname(__file__),"map_images_{}{}/{}_{}.png".format(zoom, self.model.map_folder,new_x, new_y))
		  if self.tiles[x][y].get('name') != fileName:
			  if os.path.isfile(fileName) and os.stat(fileName).st_size != 0:
				self.tiles[x][y]['name'] = fileName
				self.tiles[x][y]['tile'] = pygame.image.load(fileName)
			  else:
			  	tilePos = self.model.num2deg(new_x, new_y, zoom)
			  	if tilePos[0] == 0:
			  		return
			  	if self.model.map_folder == '_vect':
					self.model.getStreetImage(tilePos[0], tilePos[1], zoom, new_x, new_y)
				else:
					self.model.getSatelliteImage(tilePos[0], tilePos[1], zoom, new_x, new_y)

	def blitMap(self, offset_x,offset_y,screen):
		for x in range(0,self.w):
			for y in range(0,self.h):
				if self.tiles[x][y].get('tile'):
					screen.blit(self.tiles[x][y].get('tile'), (offset_x-128+((x-2)*256), offset_y-128+((y-2)*256) ))

	def blitPlane(self, angle, screen):
		angledplane = self.rot_center(self.the_plane, angle)
		screen.blit(angledplane, (self.model.width/2-32,self.model.height/2-32))

	def loadAndBlitMap(self, x,y,offset_x,offset_y, angle, screen):
		self.loadTiles(x,y, self.zoom)
		self.blitMap(offset_x,offset_y,screen)
		self.blitPlane(360 - angle,screen)

	def rot_center(self, image, angle):
	    """rotate an image while keeping its center and size"""
	    orig_rect = image.get_rect()
	    rot_image = pygame.transform.rotate(image, angle)
	    rot_rect = orig_rect.copy()
	    rot_rect.center = rot_image.get_rect().center
	    rot_image = rot_image.subsurface(rot_rect).copy()
	    return rot_image

	def renderPlane(self, screen):
		flight_dict = self.model.get_flights()
		flight = flight_dict.get(self.plane)
		if flight is not None:
			tile = self.model.deg2num(flight.get('lat'), flight.get('lon'), self.zoom)
			offset = self.model.getOffset(flight.get('lat'), flight.get('lon'), self.zoom)	
			self.loadAndBlitMap(tile[0], tile[1], offset[0], offset[1], flight.get('track'), screen)
			self.paintPlaneInfo(flight, screen)
		else:
			#return the main screen
			self.controller.change_to_main()

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(ui_flyby.MAIN_BG)
		self.renderPlane(screen)
		self.buttons.render(screen)

	def setPlane(self, plane):
		self.plane = plane

	def zoomOut(self, button):
		self.zoom = self.zoom - 1
		if self.zoom < self.model.tile_zoomed_out:
			self.zoom = self.model.tile_zoomed_out
		self.clearTiles()
		print("zoomOut " + str(self.zoom))

	def zoomIn(self, button):
		self.zoom = self.zoom + 1
		if self.zoom > self.model.tile_zoom:
			self.zoom = self.model.tile_zoom
		self.clearTiles()
		print("zoomIn " + str(self.zoom))

	def setSat(self, button):
		print("set Sattellite")
		self.clearTiles()
		self.model.map_folder = ""

	def setVect(self, button):
		print("set vector map")
		self.clearTiles()
		self.model.map_folder = "_vect"

	def reset_map(self, button):
		self.model.map_folder = "_vect"
		self.zoom = self.model.tile_zoom
		self.clearTiles()
		print("reset map")

	def click(self, location):
		self.buttons.click(location)

	def quit_click(self, button):
		self.controller.message_dialog('QUIT: Are you sure?',
			accept=self.quit_accept)

	def quit_accept(self):
		sys.exit(0)

class PlaneList(ViewBase):
	"""The main view for the list of Planes flying around."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 5)
		self.buttons.add(5, 0, 'MAP', click=self.controller.change_to_allPlanesMap)
		self.buttons.add(5, 4, 'X', click=self.quit_click,
			bg_color=ui_flyby.CANCEL_BG)
		self.plane_buttons = None

	def planeButtons(self, flights, screen):
		self.plane_buttons = ui.AirplaneButtonGrid(self.model.width, self.model.height, 6, 5)
		for x in xrange(0,len(flights)):
			flight = flights[x]
			plan = flight.get('plan')
			if plan is None:
				plan = ""
			renderText = "{} {}".format(flight.get('OperatorName') if flight.get('OperatorName') else '', flight.get('flight'))
			#bottomText = "{}ft {}fpm {} {}".format(flight.get('altitude'), flight.get('vert_rate'), flight.get('status'),  flight.get('area'))
			fromText = "{} {}".format(flight.get('FromAirportLocation'), flight.get('FromAirportCountry')) if flight.get('FromAirportCountry') != "United States" else "{}".format(flight.get('FromAirportLocation'))
			toText = "{} {}".format(flight.get('ToAirportLocation'), flight.get('ToAirportCountry')) if flight.get('ToAirportCountry') != "United States" else "{}".format(flight.get('ToAirportLocation'))

			if fromText == 'None None':
				fromText = flight.get('plan')
				toText = ''

			bottomText = "{} {}".format(fromText, toText)
			self.plane_buttons.add(0, x, renderText, bottomText, click=self.controller.change_to_planeMap, flight=flight.get('flight'), colspan=5)
			self.plane_buttons.render(screen)

	def noFlights(self, screen):
		label_flight = ui.render_flight_text("No Flights", size=ui_flyby.MAIN_FONT * 2)
		rect = label_flight.get_rect()
		screen.blit(label_flight, (self.model.width / 2 - rect.width / 2, self.model.height / 2 - ui.MAIN_FONT))

	def renderPlanes(self, screen):
		flight_dict = self.model.get_flights()
		if flight_dict and len(flight_dict) > 0:
			flights = [value for key, value in flight_dict.iteritems()]
			self.planeButtons(flights, screen)
			#self.printInTheSky(flights, screen)
		else:
			self.noFlights(screen)
		#print(flights)

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(ui_flyby.MAIN_BG)
		self.renderPlanes(screen)
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)
		if self.plane_buttons:
			self.plane_buttons.click(location)

	def quit_click(self, button):
		self.controller.message_dialog('QUIT: Are you sure?',
			accept=self.quit_accept)

	def quit_accept(self):
		sys.exit(0)

