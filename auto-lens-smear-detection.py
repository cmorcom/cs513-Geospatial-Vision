import multiprocessing as mp
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2 as cv

import smeardetect as sd

os.system("clear") #clear the terminal screen

#constants needed for later (will be changed to args)
CPUs = mp.cpu_count() #cpu count for threading
#all out images have the same dimensions. otherwise find center and truncate from there.
img_height = 2032
img_width = 2032
parentdir="./sample_drive/"
tempdir = "./tmp/"

info = "\n\nauto-lens-smear-detection.py\nBY: Christopher Morcom & Brianna Bransfield\nCS 513 -- Spring 2020\n\nUsing OpenCV-4.2.0\nUsing Python-3.7.4"
print(info, end="\n\n\n")

#if not os.path.isdir(tempdir): os.mkdir("tmp") #make a temp directory for storing calc images

cams=[]	#list of photos for each camera

print("Input Directories:")
for root, dirs, files in os.walk(parentdir, topdown=False): #do images before changing dirs
	parentdir = root
	for n in dirs: 
		cams.append(n)
		print(os.path.join(root,n))

print("\n\nNOTE: We assume that the smear is constant per lens.\n")

#loop for getting mean image and applying some filters
for lens in cams:

	curdir=os.path.join(parentdir,lens)
	print("Processing mask for:", lens)

	name = lens + "_mean_extracted.jpeg"
	#generate a mean image and smooth out the smear
	mean_img = sd.gen_mask(curdir, name) #returns (string) path to mean image

#loop that gets us a mask and a binary mask
for x in os.listdir(os.getcwd()):
	if x.endswith(".jpeg"):
		name = x[0:5]+"_mean_filtered_mask.jpeg"
		img_mask = sd.smooth_mask(x, name)
		print("Created Masks for: {}".format(x[: 5]), end="\r")
		bwname= name[0:5]+"_binary_mask.jpeg"
		bw_mask = sd.create_binary_mask(name,bwname)

print("")