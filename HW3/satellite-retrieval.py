import argparse
from math import pi, cos, sin, log, radians, degrees
from PIL import Image

EarthRadius = 6378137

#create parser for coordinate bounds
parser = argparse.ArgumentParser(description="Generate a map tile given lattitude and longitude coordinates.")
parser.add_argument("coordinate", type=float, nargs=4, action="store", help="specify bounding box in decimal degrees: x1 y1 x2 y2") #must have four coordinates
parser.add_argument("detail_level", type=int, nargs=1, action="store", help="specify the level of detail in the map [1-23]")
parser.add_argument("-f", "--filename", action="store", default="tile", nargs=1, help="specify an output filename (no extension)") #option for custom filename
parser.add_argument('--verbose', '-v', action='store_true', default=0, help="verbosity flag") #verbose flag
args = parser.parse_args()

v = args.verbose #symbolic V makes it easier to write

#short, sorted, symbolic links
minX, minY, maxX, maxY = tuple(args.coordinate) 
lvl = args.detail_level[0]

#Error Checking
if (abs(minX)>180.0 or abs(maxX)>180.0 or abs(minY)>85.05112878 or abs(maxY)>85.05112878):
	raise Exception("Invalid coordinates. Longitude +/-180, Lattitude +/-85.05112878")
if maxX==minX: raise Exception("Invalid coordinates. Specify two different Lattitudes.")
if maxY==minY: raise Exception("Invalid coordinates. Specify two different Longitudes.")
if (lvl>23 or lvl<1): raise Exception("Invalid Detail Level. Choose 1 to 23.")

#reformat bounding box to go from min->max
def switch(a,b): a,b = b,a
if maxX<minX: switch(minX,maxX)
if maxY<minY: switch(minY,maxY)
if v: print("Bounding Box: ({},{}) -> ({},{})".format(minX,minY,maxX,maxY))
if v: print("\nLevel of Detail =", lvl)

#took these from the source material given to us
sinLatMin = sin(radians(minY))
sinLatMax = sin(radians(maxY))

pXmin = (((minX+180)/360)*256)*(2**lvl)
pXmax = (((maxX+180)/360)*256)*(2**lvl)
pYmin = (0.5-log((1+sinLatMin)/(1-sinLatMin), 10)/(4*pi))*256*(2**lvl)
pYmax = (0.5-log((1+sinLatMax)/(1-sinLatMax), 10)/(4*pi))*256*(2**lvl)
if (v): print("sinLatMin: {}\nsinLatMax: {}\npXmin: {}\npXmax: {}\npYmin: {}\npYmax: {}".format(sinLatMin, sinLatMax, pXmin, pXmax, pYmin, pYmax))

#Calc Tile Numbers for each coordinate given c is a pixel coordinate and l is lvl
tXmin = (int)(pXmin//256)
tXmax = (int)(pXmax//256)
tYmin = (int)(pYmin//256)
tYmax = (int)(pYmax//256)
if v: print("TileBox: ({},{}) -> ({},{})".format(tXmin,tYmin,tXmax,tYmax))
#generate array of tiles that we need
tiles=[]

for xx in list(range(tXmin, tXmax+1)):
	for yy in list(range(tYmin, tYmax+1)):
		tiles.append(tuple(xx,yy))

if v: print('Tiles:', tiles)