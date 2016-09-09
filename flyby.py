from mapbox import Static
import pygame, sys, os
import os.path
from all_nearest_planes import Flyover
from pygame.locals import *
import math
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')

access_token='YOUR API KEY'
service = Static(access_token=access_token)

pygame.init()
pygame.mouse.set_visible(False)

#here is the width and the height of the LCD aka FB1
screen_width = 480
screen_height = 320

center_lon = -122.185724
center_lat = 37.617190

tile_zoom = 14
tile_dimension = 256
map_folder = "_vect"
 
# set up the window
#for the mini screen
DISPLAYSURF = pygame.display.set_mode((screen_width, screen_height)) 
#DISPLAYSURF = pygame.display.set_mode((screen_width, screen_height),pygame.FULLSCREEN) 

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myFontSize = 40
myfont = pygame.font.SysFont("monospace", myFontSize)
mySmallfont = pygame.font.SysFont("monospace", myFontSize)
mySmallerFont = pygame.font.SysFont("monospace", myFontSize/2)
 
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
LOW_WHITE = (200, 200, 200)
OFF_WHITE = (125, 125, 125)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

the_plane = pygame.image.load("planes/boeing-737-256.png")
mini_plane = pygame.image.load("planes/boeing-737-256-mini.png")
 
# draw on the surface object
DISPLAYSURF.fill(BLACK)
pygame.draw.line(DISPLAYSURF, BLUE, (60, 120), (120, 120), 4)
 
pixObj = pygame.PixelArray(DISPLAYSURF)
pixObj[380][280] = BLACK
pixObj[382][282] = BLACK
pixObj[384][284] = BLACK
pixObj[386][286] = BLACK
pixObj[388][288] = BLACK
del pixObj

flyover = Flyover()

#the tiles that we store the graphics in
w, h = 5, 5
tiles = [[{} for y in xrange(0,h)] for x in xrange(0,w)] 
#print flyover.get_nearest_airplane('')
#flyover.get_all_planes('')

#This is for satellite images
def getSatelliteImage(lat, lon, z, x, y):
	#first create an empty file to mark it so the request is not sent twice
	response = service.image('mapbox.satellite', lon=lon, lat=lat, z=z, width=tile_dimension, height=tile_dimension)
	with open('map_images/'+ str(x) + '_' + str(y) +'.png', 'wb') as output:
    	 _ = output.write(response.content)

#This is for satellite images
def getStreetImage(lat, lon, z, x, y):
	#first create an empty file to mark it so the request is not sent twice
	open('map_images_vect/'+ str(x) + '_' + str(y) +'.png', 'a').close()
	response = service.image('mapbox.streets', lon=lon, lat=lat, z=z, width=tile_dimension, height=tile_dimension)
	with open('map_images_vect/'+ str(x) + '_' + str(y) +'.png', 'wb') as output:
    	 _ = output.write(response.content)

def getPlanePos(lat, lon, map_x, map_y, offset_x, offset_y):
	tile = deg2num(lat, lon, 9)
	offset = getOffset(lat, lon, 9)

	x = (tile[0] - map_x)*256 + offset[0] 
	y = (tile[1] - map_y)*256 + offset[1] 

	print (x,y)
	return (x,y)

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def loadTiles(center_x,center_y, zoom):
  for x in range(0,w):
	for y in range(0,h):
	  new_x = center_x - 2 + x
	  new_y = center_y - 2 + y
	  fileName = "map_images{}/{}_{}.png".format(map_folder,new_x, new_y)
	  if tiles[x][y].get('name') != fileName:
		  if os.path.isfile(fileName) and os.stat(fileName).st_size != 0:
			tiles[x][y]['name'] = fileName
			tiles[x][y]['tile'] = pygame.image.load(fileName)
		  else:
		  	tilePos = num2deg(new_x, new_y, tile_zoom)
		  	if tilePos[0] == 0:
		  		return
		  	if map_folder == '_vect':
				getStreetImage(tilePos[0], tilePos[1], tile_zoom, new_x, new_y)
			else:
				getSatelliteImage(tilePos[0], tilePos[1], tile_zoom, new_x, new_y)

def blitMap(offset_x,offset_y):
	for x in range(0,w):
		for y in range(0,h):
			if tiles[x][y].get('tile'):
				DISPLAYSURF.blit(tiles[x][y].get('tile'), (offset_x-128+((x-2)*256), offset_y-128+((y-2)*256) ))

def blitPlane(angle):
	angledplane = rot_center(the_plane, angle)
	DISPLAYSURF.blit(angledplane, (screen_width/2-32,screen_height/2-32))

def loadAndBlitMap(x,y,offset_x,offset_y, angle):
	loadTiles(x,y, tile_zoom)
	blitMap(offset_x,offset_y)
	blitPlane(360 - angle)

#functions for finding the right image tile
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def getOffset(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = 256 - (((lon_deg + 180.0) / 360.0 * n) % 1) * 256
  ytile = 256 - (((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n) % 1)  * 256
  return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def decideWhatToTrack(flights):
	pass

def updateTracking(flights):
	pass

def clearScreen():
	DISPLAYSURF.fill(BLACK)

def paintPlaneInfoAt(flight, position_y):
	# render text
	plan = flyover.get_flight_plan( flight.get('flight'))
	if plan is None:
		plan = ""
	renderText = "{} {}".format(flight.get('flight').strip(), plan)
	bottomText = "{}ft {}fpm {} {}".format(flight.get('altitude'), flight.get('vert_rate'), flight.get('status'),  flight.get('area'))

	if map_folder == '_vect':
		label = myfont.render(renderText, 1, BLACK)
		lower_lable = mySmallerFont.render(bottomText, 1, RED)
	else:
		label = myfont.render(renderText, 1, WHITE)
		lower_lable = mySmallerFont.render(bottomText, 1, LOW_WHITE)

	DISPLAYSURF.blit(label, (10, position_y))
	DISPLAYSURF.blit(lower_lable, (15, position_y + myFontSize))

def paintPlaneInfo(flight):
	# render text
	label = myfont.render(flight.get('flight'), 1, WHITE)
	DISPLAYSURF.blit(label, (10, 10))

def printAllVisiblePlanes(flights, offset):
	for x in xrange(0,len(flights)):
		flight = flights[x]
		paintPlaneInfoAt(flight, 10 + (x * (myFontSize + myFontSize)) + offset)

#print everything that is in the sky
def printInTheSky(flights):
	for x in xrange(0,len(flights)):
		flight = flights[x]
		paintPlaneInfoAt(flight, 10 + (x * (myFontSize + myFontSize)))

def printNoPlanes():
	label = myfont.render("No planes now.", 1, OFF_WHITE)
	DISPLAYSURF.blit(label, (10, 10))

def blitHome():
	tile = deg2num(37.342741, -121.893402, tile_zoom)
	offset = getOffset(37.342741, -121.893402, tile_zoom)
	loadTiles(tile[0],tile[1], tile_zoom)
	blitMap(offset[0],offset[1])

def blitPlaneOnMap(flight):
	tile = deg2num(flight.get('lat'), flight.get('lon'), tile_zoom)
	offset = getOffset(flight.get('lat'), flight.get('lon'), tile_zoom)	
	loadAndBlitMap(tile[0], tile[1], offset[0], offset[1], flight.get('track'))
	paintPlaneInfoAt(flight, 10 + (0 * (myFontSize + myFontSize)))

# run the game loop
while True:
	for event in pygame.event.get():
		if(event.type is MOUSEBUTTONDOWN):
			pos = pygame.mouse.get_pos()
			print pos
		elif(event.type is MOUSEBUTTONUP):
			pos = pygame.mouse.get_pos()
			#Find which quarter of the screen we're in
			x_pos,y_pos = pos
			if y_pos < 120:
				if x_pos < 160:
					map_folder = "_vect"
				else:
					map_folder = "_vect"
			else:
				if x_pos < 160:
					map_folder = ""
				else:
					map_folder = ""
		if event.type == QUIT:
					pygame.quit()
					sys.exit()

	clearScreen()

	all_flights = flyover.get_nearest_airplane('')

	if len(all_flights) > 0:
		north_flow = [value for key, value in all_flights.iteritems() if value.get('area') == 'north_flow']		
		if len(north_flow) > 0:
			blitPlaneOnMap(north_flow[0])
			pygame.display.update()
			continue

		south_flow = [value for key, value in all_flights.iteritems() if value.get('area') == 'south_flow']		
		if len(south_flow) > 0:
			blitPlaneOnMap(south_flow[0])
			pygame.display.update()
			continue

		flybys = [value for key, value in all_flights.iteritems() if value.get('area') == 'flybys']		
		if len(flybys) > 0:
			blitPlaneOnMap(flybys[0])
			pygame.display.update()
			continue

		everything_in_the_air = [value for key, value in all_flights.iteritems()]
		blitPlaneOnMap(everything_in_the_air[0])
		pygame.display.update()

		# tile = deg2num(center_lat, center_lon, 9)
		# offset = getOffset(center_lat, center_lon, 9)
		# loadAndBlitBigMap(tile[0],tile[1],offset[0],offset[1], all_flights)
		# printInTheSky(all_flights)
	else:
		#print "No planes now"
		blitHome()
		printNoPlanes()
		pygame.display.update()





