import math
import utm

#LinkData Record Format: (map data, says where road center lines are)

class MapLink():
    def __init__(self, attrs):
        #attrs is a tuple containing one row from the data.
        data = attrs.split(',')

        self.linkPVID = int(data[0])            #published versioned identifier for the link.
        self.refNodeID = int(data[1])           #internal identifier for the link’s reference node.
        self.nrefNodeID = int(data[2])          #internal identifier for the link’s non-reference node.
        self.length = float(data[3])            #length of the link (in decimal meters).
        self.functionalClass = int(data[4])     #functional class for the link (1-5).
        self.directionOfTravel = data[5]        #allowed direction of travel for the link (F – from ref node, T – towards ref node, B - both)
        self.speedCategory = int(data[6])       #speed category for the link (1-8).
        self.fromRefSpeedLimit = int(data[7])   #speed limit for the link (in kph) in the direction of travel from the reference node.
        self.toRefSpeedLimit = int(data[8])     #speed limit for the link (in kph) in the direction of travel towards the reference node.
        self.fromRefNumLanes = int(data[9])     #number of lanes for the link in the direction of travel from the reference node.
        self.toRefNumLanes = int(data[10])      #number of lanes for the link in the direction of travel towards the reference node.
        self.multiDigitized = data[11]          #flag for if the link is multiply digitized (T – is multiply digitized, F – is singly digitized).
        self.urban = data[12]                   #flag for if the link is in an urban area (T – is in urban area, F – is in rural area).
        self.timeZone = float(data[13])         #time zone offset (in decimal hours) from UTC.
        self.shapeInfo = data[14]               #array of shape entries ordered as list of form: [reference node, shape points, non-reference node] each entry is a tuple of form (easting, northing, zone, zoneletter, elevation)
        self.curvatureInfo = data[15]           #array (this can be none)
        self.slopeInfo = data[16].strip('\n')   #array (THIS IS WHAT WE CHECK OUR DERIVED SLOPE AGAINST) (note that this can be none)

        if self.shapeInfo:
            shapedata = self.shapeInfo.split('|')
            self.shapeInfo=[]
            for x in shapedata:
                lat, lon, elev = tuple(x.split('/'))
                #convert lattitude and longitude to UTM coordinate
                utmAndElev = list(utm.from_latlon(float(lat), float(lon)))
                if elev == '': elev = 0
                utmAndElev.append(elev) #easting, northing, zone, zoneletter, elevation
                self.shapeInfo.append(tuple(utmAndElev))

        if self.curvatureInfo == '': 
            self.curvatureInfo = None
        else:
            curvaturedata = self.curvatureInfo.split('|')
            self.curvatureInfo=[]
            for x in curvaturedata:
                if x != '': 
                    b = []
                    for a in x.split('/'):
                        if a != '':
                            b.append(float(a))
                    self.curvatureInfo.append(tuple(b))
                else: 
                    self.curvatureInfo = None

        if self.slopeInfo == '': 
            self.slopeInfo = None
        else:
            slopedata = self.slopeInfo.split('|')
            self.slopeInfo=[]
            for x in slopedata:
                if x != '': 
                    b = []
                    for a in x.split('/'):
                        if a != '':
                            b.append(float(a))
                    self.slopeInfo.append(tuple(b))
                else: 
                    self.slopeInfo = None

    def __str__(self):
        a = "Maplink( \n" + \
            "\tlinkPVID: " + str(self.linkPVID) + "\n" + \
            "\trefNodeID: " + str(self.refNodeID) + "\n" + \
            "\tnrefNodeID: " + str(self.nrefNodeID) + "\n" + \
            "\tlength: " + str(self.length) + "\n" + \
            "\tfunctionalClass: " + str(self.functionalClass) + "\n" + \
            "\tdirectionOfTravel: " + str(self.directionOfTravel) + "\n" + \
            "\tspeedCategory: " + str(self.speedCategory) + "\n" + \
            "\tfromRefSpeedLimit: " + str(self.fromRefSpeedLimit) + "\n" + \
            "\ttoRefSpeedLimit: " + str(self.toRefSpeedLimit) + "\n" + \
            "\tfromRefNumLanes: " + str(self.fromRefNumLanes) + "\n" + \
            "\ttoRefNumLanes: " + str(self.toRefNumLanes) + "\n" + \
            "\tmultiDigitized: " + str(self.multiDigitized) + "\n" + \
            "\turban: " + str(self.urban) + "\n" + \
            "\ttimeZone: " + str(self.timeZone) + "\n" + \
            "\tshapeInfo: " + str(self.shapeInfo) + "\n" + \
            "\tcurvatureInfo: " + str(self.curvatureInfo) + "\n" + \
            "\tslopeInfo: " + str(self.slopeInfo) + "\n" +\
        ")"
        return a

    def refX(self): return self.shapeInfo[0][0]
    def refY(self): return self.shapeInfo[0][1]
    def nonrefX(self): return self.shapeInfo[-1][0]
    def nonrefY(self): return self.shapeInfo[-1][1]
    