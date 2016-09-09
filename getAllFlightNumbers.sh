#get all the flight numbers
#!/bin/bash
# encoding: utf-8
# wget -q -O FlightNumbers.csv -nc http://www.virtualradarserver.co.uk/Files/FlightNumbers.csv

#my way
curl -O http://www.virtualradarserver.co.uk/Files/FlightNumbers.csv
#grep KSJC FlightNumbers.csv > KSJCFlights.csv