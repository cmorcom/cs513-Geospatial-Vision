import pandas as pd
import re
import numpy as np
import utm
import plotly.graph_objects as go
from sklearn.cluster import KMeans

##### CONSTANTS #####
"""
Coordinate Range: 
    (N/S) Latitude:   45.90487933  to  45.90329572 
    (W/E) Longitude:  11.02701384  to  11.02965733
     (Z)  Altitude:   221.8044     to  234.5053

    (UTM) (E,N,Zone): (657224.13, 11.027014, 32T) to 
                      (657433.61, 5085306.11 32T)
"""

def colorcluster(clusterNo):
	hexColors=[0xFF6800,0xD909E8,0x036CFF,0x09E839,0xFFDD0A,0xFF0303,0x00FFD9,0xA5E80C]
	return hexColors[clusterNo]

def skiplines(fp, n):
	for _ in range(n):
		fp.readline()
	return

def readXYZi(text):
	if not text: return None
	t = re.split(r'[, \t]', text.strip('\n'))
	y,x,z,i = tuple(map(float, t))
	return (x,y,z,i)

def processCarData(filename, utmMin=(657224.13, 5085306.11, "32T")):
	f = open(filename, encoding='utf-8-sig')
	done = False
	Xs, Ys, Zs = [], [], []
	while not done:
		tup = readXYZi(f.readline())
		if not tup: done = True
		else:
			x,y,z,i = tup
			utmCoor = utm.from_latlon(y,x)
			Xs.append(utmCoor[0]-utmMin[0])
			Ys.append(utmCoor[1]-utmMin[1])
			Zs.append(z)

	f.close()
	return Xs,Ys,Zs,go.Scatter3d(
		name="Trajectory",
		x=Xs,
		y=Ys,
		z=Zs,
		line=dict(dash="solid", color="mediumblue", width=4),
		marker=dict(
			size=6,
			color='blue', #shades of BW
			opacity=1
		),
	)


def processCameraData(filename, pointcolor, utmMin=(657224.13, 5085306.11, "32T")):
	f = open(filename, encoding='utf-8-sig')
	f.readline() #remove header line
	done = False
	Xs, Ys, Zs, Qs = [], [], [], []
	while not done:
		buf = f.readline()
		if buf == '': done = True
		else:
			buf = re.split(r'[, \t]+', buf.strip('\n'))
			data = list(map(float,buf))
			
			y,x,z = tuple(data[0:3])
			utmCoor = utm.from_latlon(y,x)
			q = tuple(data[3:])
			fX, fY = utmCoor[0]-utmMin[0], utmCoor[1]-utmMin[1]
			Xs.append(fX)
			Ys.append(fY)
			Zs.append(z)
			Qs.append(q)
	f.close()

	return Xs[0],Ys[0],z,q,go.Scatter3d(
		name="Camera",
		x=Xs,
		y=Ys,
		z=Zs,
		mode='markers',
		hovertext=["Q(s,x,y,z) = "+s for s in map(str,Qs)],
		marker=dict(
			size=10,
			color=pointcolor, #shades of BW
			opacity=1
	))

f = open(".\\final_project_data\\final_project_point_cloud.csv", 'r', encoding='utf-8-sig')

# hard coded constants for the bounding box
utmMin = (657224.13-20, 5085306.11-20, "32T") #East, North, Zone #pad with 20
utmMax = (657433.61, 5085476.77, "32T") #East, North, Zone

#process Camera(s)
CamX,CamY,CamZ,CamQ, cameraPlot = processCameraData(".\\final_project_data\\image\\camera.config",'red', utmMin=utmMin)

#process Car Data And Plot it
CarX, CarY, CarZ, carPlot = processCarData(".\\final_project_data\\trajectory.fuse", utmMin=utmMin)

# Process Point Cloud here
done = False
threshold = 10
num=0
Xs, Ys, Zs, Is = [], [], [], []
while not done:
	tup = readXYZi(f.readline())
	if not tup: 
		done = True
	else:
		x,y,z,i = tup
		utmCoor = utm.from_latlon(y,x)
		if i > threshold and z < CamZ-1: #ignore all points higher than 0.5 meter below camera

			Xs.append(utmCoor[0]-utmMin[0])
			Ys.append(utmCoor[1]-utmMin[1])
			Zs.append(z)
			Is.append(i)

#generate numpy 2D array for clustering data
Xs = np.array(Xs)
Ys = np.array(Ys)
Zs = np.array(Zs)
IsN = np.array(Is)
data = np.column_stack((Xs, Ys, Zs))

#generate model and fit data
print("BEGIN CLUSTERING POINTCLOUD")
est = KMeans(n_clusters=3)
est.fit(data, sample_weight=IsN)
ykmeans = est.predict(data)
print(ykmeans); print(data); print(len(ykmeans)); print(len(data))

#generate meshes for clusters


centers = est.cluster_centers_
centersPlot = go.Scatter3d(
	name="Lidar Point Cloud",
	x=centers[:,0],
	y=centers[:,1],
	z=centers[:,2],
	mode='markers',
	marker=dict(
		size=9,
		color='fuchsia', #shades of BW
		opacity=0.6
	)
)

#generate pointcloud graph
pointcloud = go.Scatter3d(
	name="Lidar Point Cloud",
	x=data[:,0],
	y=data[:,1],
	z=data[:,2],
	mode='markers',
	marker=dict(
		size=3,
		color=[colorcluster(cn) for cn in ykmeans],
		opacity=0.25
	)
)


# Plot Figure Here
fig = go.Figure(
	data=[pointcloud, centersPlot, cameraPlot, carPlot], #plot: pointcloud, cameraplot
	layout=go.Layout(
		title="Final Project Point Cloud Plot",
		margin=dict(l=0, r=0, b=0, t=0),
		paper_bgcolor='rgb(120,120,120)',
		plot_bgcolor='rgba(0,0,100,50)',
		scene=dict(
			xaxis=dict(autorange=False,
				range=(0,240),
				tick0=0,
				dtick=10,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='antiquewhite',
			),
			yaxis=dict(autorange=False,
				range=(0,240),
				tick0=0,
				dtick=10,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='antiquewhite',
			),
			zaxis=dict(
				range=(220,230),
				tick0=0,
				dtick=1,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='antiquewhite',

			)
		)
	)
)

fig.show()