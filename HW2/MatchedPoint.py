import utm
import math
class MatchedPoint:
	def __init__(self, pp=None, ml=None, attrs=None): #pp=probe point, ml=map link
		if pp and ml:
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
		elif attrs:
			data = attrs.split(',')
			self.sampleID = int(data[0])
			self.dateTime = data[1]
			self.sourceCode = int(data[2])
			self.latitude = float(data[3])
			self.longitude = float(data[4])
			self.altitude = int(data[5])
			self.speed = int(data[6])
			self.heading = int(data[7])
			self.linkPVID = int(data[8])
			self.direction = data[9]
			self.distFromRef = float(data[10])
			self.distFromLink = float(data[11].strip('\n'))
		else:
			raise TypeError("Invalid constructor metadata specified")

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
		