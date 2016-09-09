# FreqShow main application model/state.
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
import numpy as np
import math
from mapbox import Static
from shapely.geometry import Point, Polygon, LineString

#from rtlsdr import *

access_token='YOUR API KEY'
service = Static(access_token=access_token)

from all_nearest_planes import Flyover
import os.path
import ui_flyby

class UIFlyByModel(object):
	def __init__(self, width, height):
		"""Create main FreqShow application model.  Must provide the width and
		height of the screen in pixels.
		"""
		# Set properties that will be used by views.
		self.width = width
		self.height = height
		self.flyover = Flyover()
		self.all_flights = {}
		self.map_folder = "_vect"
		self.center_lon = -122.185724
		self.center_lat = 37.617190
		self.tile_zoom = 14
		self.tile_zoomed_out = 9
		self.tile_dimension = 256
		self.map_folder = "_vect"

	def get_flights(self):
		self.all_flights = self.flyover.get_nearest_airplane('')
		return self.all_flights

	#This is for satellite images
	def getSatelliteImage(self, lat, lon, z, x, y):
		#first create an empty file to mark it so the request is not sent twice
		directory = os.path.join(os.path.dirname(__file__),"map_images_{}{}".format(z, self.map_folder))
		if not os.path.exists(directory):
			os.makedirs(directory)
		fileName = os.path.join(os.path.dirname(__file__),"map_images_{}{}/{}_{}.png".format(z, self.map_folder,x, y))
		open(fileName, 'a').close()
		response = service.image('mapbox.satellite', lon=lon, lat=lat, z=z, width=self.tile_dimension, height=self.tile_dimension)
		with open(fileName, 'wb') as output:
			 _ = output.write(response.content)

	#This is for satellite images
	def getStreetImage(self, lat, lon, z, x, y):
		#first create an empty file to mark it so the request is not sent twice
		directory = os.path.join(os.path.dirname(__file__),"map_images_{}{}".format(z, self.map_folder))
		if not os.path.exists(directory):
			os.makedirs(directory)
		fileName = os.path.join(os.path.dirname(__file__),"map_images_{}{}/{}_{}.png".format(z, self.map_folder,x, y))
		open(fileName, 'a').close()
		response = service.image('mapbox.streets', lon=lon, lat=lat, z=z, width=self.tile_dimension, height=self.tile_dimension)
		with open(fileName, 'wb') as output:
			 _ = output.write(response.content)

	def planeOffset(self, lat_deg, lon_deg, centroid, zoom):
		planeXY = self.deg2RawNum(lat_deg, lon_deg, zoom)
		centroidXY = self.deg2RawNum(centroid.x, centroid.y, zoom)
		offsetX = (centroidXY[0] - planeXY[0]) * 256
		offsetY = (centroidXY[1] - planeXY[1]) * 256
		return (offsetX, offsetY)

	def deg2RawNum(self, lat_deg, lon_deg, zoom):
		lat_rad = math.radians(lat_deg)
		n = 2.0 ** zoom
		x = ((lon_deg + 180.0) / 360.0 * n)
		y = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
		return (x, y)

	def getOffset(self, lat_deg, lon_deg, zoom):
		lat_rad = math.radians(lat_deg)
		n = 2.0 ** zoom
		xtile = 256 - (((lon_deg + 180.0) / 360.0 * n) % 1) * 256
		ytile = 256 - (((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n) % 1)  * 256
		return (xtile, ytile)

	def deg2num(self, lat_deg, lon_deg, zoom):
		lat_rad = math.radians(lat_deg)
		n = 2.0 ** zoom
		xtile = int((lon_deg + 180.0) / 360.0 * n)
		ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
		return (xtile, ytile)

	def num2deg(self, xtile, ytile, zoom):
		n = 2.0 ** zoom
		lon_deg = xtile / n * 360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
		lat_deg = math.degrees(lat_rad)
		return (lat_deg, lon_deg)

	def centroid(self, flights):
		if flights is None or len(flights) == 0:
			return Point(self.center_lat, self.center_lon)
		elif len(flights) > 1:
			polygon = LineString(flights)
			centroid = polygon.centroid
			return centroid
		else:
			#print(flights)
			return Point(flights[0])

