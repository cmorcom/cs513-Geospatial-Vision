import numpy as np
import math
import matplotlib.pyplot as plt
import os
import cv2 as cv
import numpy as np

# HELPER FUNCTIONS #

def div_list(l,n):
	for x in range(0,len(l),n): yield l[x:(x+n)]
#create a blank image
def blank(h,w,rgb=(0,0,0)):
	img = np.zeros((h,w,3), np.uint8)
	color=tuple(reversed(rgb))
	img[:]=color
	return img


#see https://docs.opencv.org/master/d5/daf/tutorial_py_histogram_equalization.html 
def preprocessImg(pathToImg, claheOBJ, blurKernel=(3,3)): #match kernel to CLAHE adaptive equalization
	image = cv.imread(pathToImg)
	if not image.any(): raise NameError("Nonexistent File: \'{}\'".format(pathToImg))
	grayed = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #grayscale image
	#equalized = cv.equalizeHist(gray) 
	equalized = claheOBJ.apply(grayed) #adaptive equalize image to remove noise and improve contrast
	blurred = cv.blur(equalized, blurKernel) #blur
	ret1, threshed = cv.threshold(blurred,127,255,cv.THRESH_BINARY) #apply global threshold as used in OpenCV Documentation to reduce noise
	return threshed

# IMAGE FUNCTIONS #

def gen_mask(path, name, claheTile=(8,8), blurKernel=(3,3), threads=1): 	#threads param says whether to thread these.
	mean_img_name = name
	for root, dirs, files in os.walk(path): pass #all we need is the files variable

	# WORKER FUNCTION FOR THREADING #	
	#chunksize = math.ceil(len(files)/threads) #process equal num of images on each thread
	denominator = 1/len(files)
	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=claheTile) #create CLAHE object
	#preprocess all images and add it to the mean
	mean = preprocessImg(os.path.join(root,files[0]), clahe, blurKernel=blurKernel)*denominator
	x=1
	for path in files[1:]:
		print("Processing image no.",x,"of", len(files), end='\r')
		img = preprocessImg(os.path.join(root,path), clahe, blurKernel=blurKernel)*denominator
		mean = cv.add(mean, img)
		x+=1

	#Apply adaptive threshold to extract smear
	#dst = cv.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C[, dst]	)
	#grayed = cv.cvtColor(mean, cv.COLOR_BGR2GRAY) #grayscale image
	#threshed = cv.adaptiveThreshold(mean, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 100, 10)

	cv.imwrite(mean_img_name, mean) #creates a new jpeg
	print("WROTE PREMASK", mean_img_name)
	return mean_img_name 

def smooth_mask(path, name, kernel=(8,8)): #8x8 is default for clahe so we use it here
	maskname = os.path.join(path, name)
	pre_mask = cv.imread(path)
	pre_mask = cv.cvtColor(pre_mask, cv.COLOR_BGR2GRAY) 
	threshed = cv.adaptiveThreshold(pre_mask, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 105, 10)
	extracted = cv.bitwise_not(pre_mask)
	#create a structuring element to remove the boundary of the foreground obj (smear)
	## fialate the smear to make it smooth and more prominent
	structuring_element = np.ones(kernel, np.uint8) #image is lare enough; we can use a square
	i = (kernel[0]//2+1) #number of iterations for erosion and dilation #iter ceil(kernel/2) times#
	#apply a structuring element to erode the boundaries of foreground object or noise
	#dilate the object to accentuate features
	eroded = cv.erode(extracted, structuring_element, iterations=i) 
	mask = cv.dilate(eroded, structuring_element, iterations=i)

	cv.imwrite(name, mask) #creates a new jpeg
	return maskname

def create_binary_mask(path, name):
	pre_mask = cv.imread(path)
	pre_mask = cv.cvtColor(pre_mask, cv.COLOR_BGR2GRAY) 
	_, bw_mask = cv.threshold(pre_mask, 128, 255, cv.THRESH_BINARY)
	cv.imwrite(name, bw_mask) #creates a new jpeg
	return name