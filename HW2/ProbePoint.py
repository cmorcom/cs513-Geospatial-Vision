from MapLink import MapLink
import utm

class ProbePoint:
	def __init__(self, attrs):
        #attrs is a tuple containing one row from the data.
		data = attrs.split(',')
		self.sampleID = int(data[0]) 	#is a *unique* identifier for the set of probe points that were collected from a particular phone.
		self.dateTime = data[1] 		#is the date and time that the probe point was collected.
		self.sourceCode = int(data[2]) 	#is a unique identifier for the data supplier (13 = COMPANY).
		latitude = float(data[3])
		longitude = float(data[4])
		self.altitude = int(data[5]) 	#is the altitude in meters.
		self.speed = int(data[6]) 		#is the speed in KPH.
		self.heading = int(data[7]) 	#is the heading in degrees.

		#Convert lat and long to UTM coordinate
		self.utm = utm.from_latlon(float(latitude), float(longitude))
		#self.utm = (float(coor[0]), float(coor[1]), int(coor[2], str(coor[3])))

		
	def __str__(self):
		a = "ProbePoint(\n"+ \
			"\tsampleID: " + str(self.sampleID ) + "\n" + \
			"\tdateTime: " + str(self.dateTime) + "\n" + \
			"\tsourceCode: " + str(self.sourceCode) + "\n" + \
			"\taltitude: " + str(self.altitude) + "\n" + \
			"\tspeed: " + str(self.speed) + "\n" + \
			"\theading: " + str(self.heading) + "\n" + \
			"\tUTM: " + str(self.utm) + "\n" + \
		")"
		return a

	def X(self): return self.utm[0]
	def Y(self): return self.utm[1]