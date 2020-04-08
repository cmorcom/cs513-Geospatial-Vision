#CONSTANTS TO USE

trajectoryFile = ".\\final_project_data\\trajectory.fuse"
cameraFile = ".\\final_project_data\\image\\camera.config"
pointcloudFile = ".\\final_project_data\\final_project_point_cloud.csv"

threshold = 8 #pick a number (8-255) to filter out pointcloud points
eps=3.5
minsamples = 6500//threshold

outfilename = ".\\results\\pointcloud_thresh={}_eps={}_minsamples={}.html"\
				.format(threshold,eps,minsamples)

import os

cpuCount = os.cpu_count()
print("Number of CPUs to use:", cpuCount) 
##### CONSTANTS #####
"""
Coordinate Range: 
    (N/S) Latitude:   45.90487933  to  45.90329572 
    (W/E) Longitude:  11.02701384  to  11.02965733
     (Z)  Altitude:   221.8044     to  234.5053

    (UTM) (E,N,Zone): (657224.13, 11.027014, 32T) to 
                      (657433.61, 5085306.11 32T)
"""

import pandas as pd
import re
import numpy as np
from math import sqrt
import utm
import plotly.graph_objects as go
import plotly.offline as po
from sklearn.cluster import DBSCAN
#DBSCAN - Density-Based Spatial Clustering of Applications with Nois


def xyDistFromCam(c, p):
	return abs(sqrt((c[0]-p[0])**2+(c[1]-p[1])**2))

def xyDistFromTrajectory(c, t_list):
	dists = [abs(sqrt((c[0]-p[0])**2+(c[1]-p[1])**2)) for p in t_list]
	dists.append(0x7FFFFFFF)#max int 
	return min(dists)

def colorcluster(clusterNo):
	if clusterNo == -1: return 'white'
	colors=['saddlebrown','black','green','navy','purple','darkslategray','orange','maroon','olive','darkolivegreen']
	return colors[clusterNo%len(colors)]

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

f = open(pointcloudFile, 'r', encoding='utf-8-sig')

# hard coded constants for the bounding box
utmMin = (657224.13-20, 5085306.11-20, "32T") #East, North, Zone #pad with 20
utmMax = (657433.61, 5085476.77, "32T") #East, North, Zone

#process Camera(s)
CamX,CamY,CamZ,CamQ, cameraPlot = processCameraData(cameraFile,'red', utmMin=utmMin)

#process Car Data And Plot it
CarX, CarY, CarZ, carPlot = processCarData(trajectoryFile, utmMin=utmMin)
carXY= zip(CarX,CarY)

# Process Point Cloud here
done = False
num=0
Xs, Ys, Zs, Is = [], [], [], []
while not done:
	tup = readXYZi(f.readline())
	if not tup: 
		done = True
	else:
		x,y,z,i = tup
		utmCoor = utm.from_latlon(y,x)
		if i > threshold:# and z < CamZ-1: #ignore all points higher than 0.5 meter below camera
			if xyDistFromCam((CamX,CamY),(x,y)) > 12.14:  #ignore points closer than legal lane width (12.1391 ft) to cam
				if xyDistFromTrajectory((CamX,CamY),carXY) > 12.14: #iNEED TO: ignore points in direction of trajectory
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
est = DBSCAN(eps=eps, min_samples=minsamples, algorithm='auto', n_jobs=cpuCount)
clusterArray = est.fit_predict(data, sample_weight=IsN) #tree is 3-6 levels deep (4 cores)
print(data); print(len(data)); print(est); print(clusterArray); print(len(clusterArray));

#generate meshes for clusters

"""
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
"""

#generate pointcloud graph
pointcloud = go.Scatter3d(
	name="Lidar Point Cloud",
	x=data[:,0],
	y=data[:,1],
	z=data[:,2],
	mode='markers',
	marker=dict(
		size=3,
		color=[colorcluster(cn) for cn in clusterArray],
		opacity=0.25
	)
)


# Plot Figure Here
fig = go.Figure(
	data=[pointcloud, cameraPlot, carPlot], #plot: pointcloud, cameraplot
	layout=go.Layout(
		title="Final Project Point Cloud Plot",
		margin=dict(l=0, r=0, b=0, t=0),
		paper_bgcolor='dimgray',#'rgb(120,120,120)',
		plot_bgcolor='rgba(0,0,100,50)',
		scene=dict(
			aspectmode='manual',
			aspectratio=dict(x=6,y=6,z=1),
			xaxis=dict(autorange=False,
				title="Easting + 657224.13 (m)",
				range=(20,230),
				tick0=0,
				dtick=10,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='lightgrey',
			),
			yaxis=dict(autorange=False,
				title="Northing + 5085306.11 (m)",
				range=(10,220),
				tick0=0,
				dtick=10,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='lightgrey',
			),
			zaxis=dict(
				title="Altitude (m)",
				range=(220,235),
				dtick=5,
				showticklabels=True,
				gridcolor='tan',
				backgroundcolor='lightgrey',

			)
		)
	)
)

po.plot(fig, filename=outfilename, auto_open=False)
fig.show()