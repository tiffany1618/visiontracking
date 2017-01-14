import cv2 as cv
import math
import numpy as np

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 1944 #pixels
CONST_IMG_WIDTH = 2592 #pixels
CONST_CAMERA_HEIGHT; #inches
CONST_TAPE_HEIGHT; #inches
CONST_TAPE_WIDTH; #inches
CONST_CAMERA_ANGLE; #convert to radians

src = cv.imread("test.png")

def filterContours():
	#filter contours	
	
def findContours(input):
	cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def findHeight():
	#find height!

def findDistance(heightTape):
	vertPTR = CONST_IMG_HEIGHT/CONST_VERTFOV #vertical pixels to radians
	height = heightTape - CONST_CAMERA_HEIGHT #bottom of image to bottom of tape
	phi = height/vertPTR
	cameraDistance = height/math.sin(phi) #direct hypotenuse
	robotDistance = math.sqrt((cameraDistance * cameraDistance) - (height * height))
	return robotDistance





	
	
