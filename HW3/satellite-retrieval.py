import urllib3 as urllib
import json
import random
import argparse
from io import BytesIO
from math import pi, cos, sin, log, radians, degrees
from PIL import Image
import os

EarthRadius = 6378137
MAXLEVEL=23

apikey = "MYZG07xtzQ3MsfEnzRmv~cccNT6PeSZfYUexFs3s45Q~Ar7OkhMVCiYKLOXwi5GohsojgNu91IGZBIGhlk7PE0j7vp9qAOyKbMKrnjGr-dFg"

#create parser for coordinate bounds
parser = argparse.ArgumentParser(description="Generate a map tile given lattitude and longitude coordinates.")
parser.add_argument("coordinate", type=float, nargs=4, action="store", help="specify bounding box in decimal degrees: x1 y1 x2 y2") #must have four coordinates
parser.add_argument("detail_level", type=int, nargs=1, action="store", help="specify the level of detail in the map [1-23]")
parser.add_argument("-d", "--dir", action="store", default="./map_image/", nargs=1, help="specify an output tile directory") #option for custom filename
parser.add_argument("-s", "--save_map", action="store", default=["map.jpeg"], nargs=1, help="specify an output map filename") #option for custom filename
parser.add_argument('--verbose', '-v', action='store_true', default=False, help="verbosity flag") #verbose flag
args = parser.parse_args()

v = args.verbose #symbolic V makes it easier to write

#process directory to save tiles
args.dir = args.dir[0]
if v: print("\nWill Save tiles to: ./{}\n".format(args.dir))
if not os.path.isdir(args.dir): os.mkdir(args.dir)

#short, sorted, symbolic links
minX, minY, maxX, maxY = tuple(args.coordinate) 
lvl = args.detail_level[0]

#Error Checking
if (abs(minX)>180.0 or abs(maxX)>180.0 or abs(minY)>85.05112878 or abs(maxY)>85.05112878):
	raise Exception("Invalid coordinates. Longitude +/-180, Lattitude +/-85.05112878")
if maxX==minX: raise Exception("Invalid coordinates. Specify two different Lattitudes.")
if maxY==minY: raise Exception("Invalid coordinates. Specify two different Longitudes.")
if (lvl>MAXLEVEL or lvl<1): raise Exception("Invalid Detail Level ({}). Choose 1 to 23.".format(lvl))

#reformat bounding box to go from min->max
if maxX<minX: minX,maxX = maxX,minX
if maxY<minY: minY,maxY = maxY,minY
if v: print("Bounding Box: ({},{}) -> ({},{})".format(minX,minY,maxX,maxY))
if v: print("Level of Detail =", lvl)

#took these from the Tile System Description
sinLatMin = sin(radians(minY))
sinLatMax = sin(radians(maxY))

pXmin = (((minX+180)/360)*256)*(2**lvl); pYmin = (0.5-log((1+sinLatMin)/(1-sinLatMin))/(4*pi))*256*(2**lvl)
pXmax = (((maxX+180)/360)*256)*(2**lvl); pYmax = (0.5-log((1+sinLatMax)/(1-sinLatMax))/(4*pi))*256*(2**lvl)
if (v): print("\nsinLatMin: {}\nsinLatMax: {}\npXmin: {}\npXmax: {}\npYmin: {}\npYmax: {}".format(sinLatMin, sinLatMax, pXmin, pXmax, pYmin, pYmax))

#Calc Tile Numbers for each coordinate given c is a pixel coordinate and l is lvl
tXmin = (int)(pXmin//256); tXmax = (int)(pXmax//256)
tYmin = (int)(pYmin//256); tYmax = (int)(pYmax//256)
#reformat tile box to go from min->max
if tXmax<tXmin: tXmin,tXmax = tXmax, tXmin
if tYmax<tYmin: tYmin,tYmax = tYmax, tYmin

if v: print("\nTileBox: ({},{}) -> ({},{})\n".format(tXmin,tYmin,tXmax,tYmax))

def getTile(url):
	req=http.request('GET', url)
	return Image.open(BytesIO(req.data))


#interleaves the bits of the (x,y) tile coordinate
def genQuadkey(a,b,n): #n=level = length of qkey
	#global v 
	#example:
	#	 tileX: -0-1-1 = 3 (base 2)
	#	 tileY: 1-0-1- = 5 (base 2)
	# quadkey=  100111 = 213 (base 4)
	strx=format(a,"b")
	if len(strx) < n: strx = (n-len(strx))*'0'+ strx
	#if v: print("tileX={}:".format(a),strx)
	stry=format(b,"b")
	if len(stry) < n: stry = (n-len(stry))*'0'+ stry
	qkstr=''.join(y+x for x,y in zip(strx,stry))
	#if v: print("tiley={}:".format(b),stry)
	#if v: print("Binary quadkey:", qkstr)

	#convert to base 4 number string
	l=0;r=2
	qkBase4=''
	while(r<=2*n):
		qkBase4+= str(int(qkstr[l:r],base=2))
		l+=2;r+=2
	#if v: print("Base4 quadkey:", qkBase4,'\n')
	return qkBase4

#generate array of tiles that we need
tileskeys=[] #sorted U->D then L->R
for x in range(tXmin, tXmax+1): 
	for y in range(tYmin, tYmax+1):
		quadkey=genQuadkey(x,y,lvl)
		tileskeys.append([(x,y),quadkey])
#print(tileskeys)

## Once we have the tileBox and quadkeys, we can start downloading tiles ##

baseREST="https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?key="
apikey = "MYZG07xtzQ3MsfEnzRmv~cccNT6PeSZfYUexFs3s45Q~Ar7OkhMVCiYKLOXwi5GohsojgNu91IGZBIGhlk7PE0j7vp9qAOyKbMKrnjGr-dFg"

#get Rest metadata
http=urllib.PoolManager()

req = http.request('GET', baseREST+apikey)
if v: print("REST Metadata URL:",baseREST+apikey)
if v: print("GET response Code:", req.status)

#scan url data for updated url and valid subdomain
d = json.loads((req.data).decode("utf-8"))
resourceDict= d['resourceSets'][0]['resources'][0]
imgurl = resourceDict['imageUrl'] 
subdomains = resourceDict['imageUrlSubdomains'] #we randomly choose one of these
subdomain = random.choice(subdomains)


#create an image to store the tiles
dimx,dimy = (tXmax-tXmin)*256, (tYmax-tYmin+1)*256
if v: print("\nMap will print to 256px x 256px tile grid: {}x{}".format((tXmax-tXmin), (tYmax-tYmin)))
mapfilename = args.save_map[0]
mapflag = False
if v: print("\n[TRY] Processing image tiles into file {} with dimensions {} by {} pixels.".format(mapfilename, dimx,dimy))
try:
	fullmap = Image.new('RGB', (dimx,dimy))
	mapflag = True
except Exception:
	print("[ERROR] Too many tiles. Cannot construct map.")	


### process the Tiles (L->R, U->D)###
x0=0;y0=0 #tile location offset
for a in tileskeys:
	(x,y)=a[0];	quadkey=a[1]
	imgurl = resourceDict['imageUrl']
	#get each tile and download the image 
	imgurl = imgurl.replace('{subdomain}',"t0").replace('{quadkey}', quadkey)
	tile = getTile(imgurl)
	filename=os.path.join(args.dir, str(x)+'-'+str(y)+'.jpeg')
	tile.save(filename)
	print("Saved {}".format(filename), end='\r')

	#process tile into full map image
	if mapflag:
		fullmap.paste(tile,(x0*256,y0*256))
		y0+=1
		if y0 == (tYmax-tYmin+1): #change insertion column
			x0+=1
			y0=0 

if mapflag:
	fullmap.save(mapfilename)
	if v: print("[SUCCESS] Map Created. See", mapfilename,".")