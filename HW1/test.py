import multiprocessing as mp

import numpy as np

import os

import cv2 as cv

import smeardetect as sd

for x in os.listdir(os.getcwd()):
	if x.endswith(".jpeg"):
		name = x[0:5]+"_mean_filtered_mask.jpeg"
		img_mask = sd.smooth_mask(x, name)
		print("Created Masks for: {}".format(x[: 5]), end="\r")
		bwname= name[0:5]+"_binary_mask.jpeg"
		bw_mask = sd.create_bw_mask(name,bwname)

print("")