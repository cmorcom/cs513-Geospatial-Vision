import utm
import math
class MatchedPoint:
	def __init__(self, pp, ml): #pp=probe point, ml=map link
		self.sampleID = pp.sampleID
		self.dateTime = pp.dateTime
		self.sourceCode = pp.sourceCode
		self.altitude = pp.altitude
		self.speed = pp.speed
		self.heading = pp.heading
		self.linkPVID = ml.linkPVID
		self.direction = ml.directionOfTravel

		#convert utm to lat,lon first
		self.latitude, self.longitude = utm.to_latlon(*(pp.utm))
		
		#take utm and get euclidian dist
		self.distFromRef =  math.sqrt(abs(pp.X()-ml.refX())**2 + abs(pp.Y()-ml.refY())**2) #.distFromRef
		
		#the shortest distance is the perpindicular distance of line formed between ref and nonref points
		x0,y0 = pp.X(), pp.Y()
		x1,y1 = ml.refX(), ml.refY()
		x2,y2 = ml.nonrefX(), ml.nonrefY()
		self.distFromLink = abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1)/math.sqrt((y2-y1)**2+(x2-x1)**2)
		
	def __str__(self):
		a = \
			str(self.sampleID)+',' + \
			str(self.dateTime)+',' + \
			str(self.sourceCode)+',' + \
			str(self.latitude)+',' + \
			str(self.longitude)+',' + \
			str(self.altitude)+',' + \
			str(self.speed)+',' + \
			str(self.heading)+',' + \
			str(self.linkPVID)+',' + \
			str(self.direction)+',' + \
			str(self.distFromRef)+',' + \
			str(self.distFromLink)
		return a
		