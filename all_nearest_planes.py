#!/usr/bin/python
# encoding: utf-8

# gets the dump1090 JSON, assumes its on localhost
from __future__ import print_function
import requests
import time
import re
import geojson
from sys import stderr
from shapely.geometry import Point, shape
from os import path
from subprocess import check_output, CalledProcessError
import sys
import os.path

import sqlite3 as lite
gSQLDBStandingDBLocn = os.path.join(os.path.dirname(__file__),'db','StandingData.sqb')
gSQLDBBaseStnDBLocn = os.path.join(os.path.dirname(__file__),'db','BaseStation.sqb')

def createDefaultsArgs():
  import argparse
  parser = argparse.ArgumentParser(description='Usage: dump1090_to_nearest_flight.py [options]')
  parser.add_argument('-H', '--host',
                      help="The location of the dump1090 server's HTTP interface",
                      required=False,
                      default='faster-ads.local:8080')
  parser.add_argument("-a", '--altitude',
                      help="a location constraint for aircraft, e.g. '<10000' or '>30000'. In feet. ",
                      required=False,
                      default=None)
  parser.add_argument("-g", '--area',
                      help="path to geojson of a geographic constraint for aircraft",
                      required=False,
                      default=os.path.join(os.path.dirname(__file__),"flyby.geojson"))
  parser.add_argument("-l", '--location',
                      help="Your location, in \"lat,long\" format. E.g. \"40.612345,-73.912345\" ",
                      required=False,
                      default="37.3628,121.9292")  
  # parser.add_argument('-h', '--help',
  #                     help="Display this screen", )
  return parser.parse_args()

class Flyover:
  flight_num_re = re.compile("^[A-Z]{2,3}\d+$", re.IGNORECASE)
  flight_num_re_2 = re.compile("^\d+$", re.IGNORECASE) #southwest airlines
  flights_dict = {}

  @classmethod
  def get_flight_plan_from_callsign(self, pFlightCode):
    con = lite.connect(gSQLDBStandingDBLocn)
    with con:    
        cur = con.cursor()
        cur.execute("SELECT OperatorName, FromAirportName, FromAirportLocation, FromAirportCountry, FromAirportLongitude, FromAirportLatitude, " +
         " ToAirportName, ToAirportLocation, ToAirportCountry, ToAirportLongitude, ToAirportLatitude, FlightNumber FROM RouteView WHERE Callsign = ? ", (pFlightCode,))
        rows = cur.fetchall()
        for row in rows:
            return row

  @classmethod
  def get_planetype_from_ICOA(self, pICAO):
    con = lite.connect(gSQLDBBaseStnDBLocn)
    with con:    
        cur = con.cursor()    
        cur.execute("SELECT ICAOTYPECODE, Type, REGISTRATION FROM AIRCRAFT WHERE MODES = UPPER(?) ", (pICAO,))
        rows = cur.fetchall()
        for row in rows:
          return (row[0], row[1], row[2])


  @classmethod
  def get_flight_plan(self, code):
    try:
      if self.flight_num_re_2.match(code.strip()): #probably SWA
        code = "SWA" + code
        #print(code)

      result = re.findall('\d*\D+',code)
      if result:
        airline = result[0]
        number = result[1].strip()
        try:
          flight_rows = check_output(["grep", "%s,%s,"%(airline, number), os.path.join(os.path.dirname(os.path.realpath(__file__)), "FlightNumbers.csv") ]).decode("utf-8").strip().split("\r\n")
          route = flight_rows[0].split(",")[-1]
          return route
        except CalledProcessError:
          #print("ERROR: No Match for " + code, file=sys.stderr)
          return None
      else:
        print("no match")

    except Exception, e:
      print(e)

  @classmethod
  def landing_or_departing(self, route, airport_code):
    airports = route.split("-")
    if airport_code in airports:
      if airports[0] == airport_code:
        return "Departing"
      else:
        return "Arriving"
    else:
      return "Flyby"

  @classmethod
  def get_all_planes(self, options):
    if options is '':
      options = createDefaultsArgs()
    flights = requests.get("http://%s/dump1090/data.json" % options.host).json()
    flights = [f for f in flights if "flight" in f and self.flight_num_re.match(f["flight"].strip()) and f["seen"] < 60]
    return flights

  #this is the one used by flygame
  @classmethod
  def get_nearest_airplane(self, options):
    if options is '':
      options = createDefaultsArgs()

    if options.location:
      lat, lon = options.location.split(",")
      location = {"lon": float(lon),"lat": float(lat)}
 
    flights = requests.get("http://%s/dump1090/data.json" % options.host).json()

    #convert to a dict
    flights_dict = dict((flight.get('flight').strip().encode('utf-8'),flight) for flight in flights if "flight" in flight and 
      (self.flight_num_re.match(flight["flight"].strip()) or
      self.flight_num_re_2.match(flight["flight"].strip())) 
      #and flight["seen"] > 60
      #and flight["speed"] > 100
      )

    def distance(f):
      return ((f.get("lat", 0) - location["lat"]) ** 2 + (f.get("lon", 0) - location["lon"]) ** 2) ** 0.5

    #north flow landing
    def within_north_landing_area(f, area_geojson_location):
      if not area_geojson_location:
        return True
      try:
        with open(path.expanduser(area_geojson_location), 'r') as geo:
          flight_loc = Point(f.get("lon", 0), f.get("lat", 0))
          return shape(geojson.loads(geo.read())["features"][0]["geometry"]).contains(flight_loc)
      except IOError:
        print("couldn't find geojson file at %s, ignoring" % area_geojson_location, file=stderr)
        return True

    #south flow landing
    def within_south_landing_area(f, area_geojson_location):
      if not area_geojson_location:
        return True
      try:
        with open(path.expanduser(area_geojson_location), 'r') as geo:
          flight_loc = Point(f.get("lon", 0), f.get("lat", 0))
          return shape(geojson.loads(geo.read())["features"][1]["geometry"]).contains(flight_loc)
      except IOError:
        print("couldn't find geojson file at %s, ignoring" % area_geojson_location, file=stderr)
        return True

    #south flow landing
    def within_flyby_area(f, area_geojson_location):
      if not area_geojson_location:
        return True
      try:
        with open(path.expanduser(area_geojson_location), 'r') as geo:
          flight_loc = Point(f.get("lon", 0), f.get("lat", 0))
          #return shape(bounds).contains(flight_loc)
          return shape(geojson.loads(geo.read())["features"][2]["geometry"]).contains(flight_loc)
      except IOError:
        print("couldn't find geojson file at %s, ignoring" % area_geojson_location, file=stderr)
        return True

    def landingOrTakeOff(flight):
      if flight.get('altitude') < 10000 and flight.get('altitude') > 0 and flight.get('speed') > 100:
        if flight.get('vert_rate') > 1000: #ascending
          if flight.get('area') == 'south_flow':
            flight.update(status = 'taking off')
          elif flight.get('area') == 'north_flow':
            flight.update(status = 'taking off')
          else:
            flight.update(status = 'ascending')
        elif flight.get('vert_rate') < -1000: #descending
          if flight.get('area') == 'south_flow':
            flight.update(status = 'landing')
          elif flight.get('area') == 'north_flow':
            flight.update(status = 'landing')
          else:
            flight.update(status = 'descending')
        else:
          flight.update(status = 'low cruise')
      else:
        flight.update(status = 'cruising')

    def altitude(flight, altitude_string):
      if not altitude_string:
        return True 
      altitude_string = altitude_string.strip()
      if 'altitude' not in flight:
        return False 
      if altitude_string[0] == ">":
        return flight['altitude'] > int(altitude_string[1:])
      elif altitude_string[0] == "<":
        return flight['altitude'] < int(altitude_string[1:])
      else: # assume less than
        return flight['altitude'] < int(altitude_string)

    def printFlights(flights, description):
      print(description)
      for flight in flights:
        print(flight.get('flight'))
      print()

    def addFlightInfo(flight):
      plan = Flyover.get_flight_plan( flight.get('flight') )
      if plan:
        flight.update(plan = plan)

      codes = Flyover.get_planetype_from_ICOA(flight.get('hex'))
      if codes:
        flight.update(planeType = codes[0])
        flight.update(typeName = codes[1])
        flight.update(planeRegistration = codes[2])

      dbPlan = Flyover.get_flight_plan_from_callsign(flight.get('flight').strip().encode('utf-8'))
      if dbPlan:
        flight.update(OperatorName = dbPlan[0])
        flight.update(FromAirportName = dbPlan[1].encode("utf-8"))
        flight.update(FromAirportLocation = dbPlan[2].encode("utf-8"))
        flight.update(FromAirportCountry = dbPlan[3].encode("utf-8"))
        flight.update(FromAirportLongitude = dbPlan[4])
        flight.update(FromAirportLatitude = dbPlan[5])
        flight.update(ToAirportName = dbPlan[6].encode("utf-8"))
        flight.update(ToAirportLocation = dbPlan[7].encode("utf-8"))
        flight.update(ToAirportCountry = dbPlan[8].encode("utf-8"))
        flight.update(ToAirportLongitude = dbPlan[9])
        flight.update(ToAirportLatitude = dbPlan[10])
        flight.update(FlightNumber = dbPlan[11])

      #then get the area
      if within_north_landing_area(flight, options.area):
        flight.update(area = 'north_flow')
      #is the flight in north flow?
      elif within_south_landing_area(flight, options.area):
        flight.update(area = 'south_flow')
      #is the flight in the flyby area?
      elif within_flyby_area(flight, options.area):
        flight.update(area = 'flyby')
      else:
        flight.update(area = 'hidden')
      landingOrTakeOff(flight)

      return flight

    def mergeNewData(flights_dict):
      #merge the data
      for key, value in flights_dict.iteritems():
        if key not in self.flights_dict:
          if value.get('seen') < 60:
            print("adding " + value.get('flight'))
            new_value = addFlightInfo(value)
            self.flights_dict.update({key: new_value})
        elif key in self.flights_dict:
          #merge the new data into the old data
          if value.get('seen') > 60: #delete old flights
            print("deleting " + value.get('flight'))
            del self.flights_dict[key]
          else:
            last_data = self.flights_dict.get(key)
            for m_key, m_value in value.iteritems():
              last_data.update({m_key : m_value})
            self.flights_dict.update({key : last_data})


    mergeNewData(flights_dict)

    try:
      return self.flights_dict
    except IndexError:
      return

if __name__ == "__main__":
  args = createDefaultsArgs()
  for i in range(0,10):
    all_flights = Flyover.get_nearest_airplane(args)

    #print(Flyover.get_nearest_airplane(args) or '')

    print(all_flights)
    for f, v in all_flights.iteritems():
      pass
      #print("{} {}".format(v.get('planeType'),v.get('planeRegistration') ))

    print()
    time.sleep (5.0);
  # for flight in flights:
  #   print("{} {} {} {} {}".format(flight.get('flight'), flight.get('plan'), flight.get('area'), flight.get('status'), flight.get('vert_rate') ))

  # #test for getting all flights going to SFO
  # for flight in flights:
  #   plan = Flyover.get_flight_plan( flight.get('flight') )
  #   if plan:
  #     print(plan)
  #     result = Flyover.landing_or_departing(plan, 'KSJC')
  #     print(result)





