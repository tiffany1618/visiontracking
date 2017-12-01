
#from vision import filterImageTape, findContours, filterContours
import cv2 as cv
import numpy as np
import math
#from camera import Camera
import time
from operator import itemgetter
from os import listdir
from random import random

CONST_IMG_HEIGHT = 800 #pixels
CONST_IMG_WIDTH = 1280 #pixels

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def findDiagonals(contour):
    # return boolean isDiagonalsEqual
    w, x, y, z = cv.boxPoints(cv.minAreaRect(contour))
    leftDiagonal = math.sqrt((w[0] - y[0]) * (w[0] - y[0]) + (w[1] - y[1]) * (w[1] - y[1]))
    rightDiagonal = math.sqrt((x[0] - z[0]) * (x[0] - z[0]) + (x[1] - z[1]) * (x[1] - z[1]))
    if leftDiagonal == rightDiagonal:
        return True

def checkCoordinates(contour):
    # boolean coordinateMatch
    w, x, y, z = cv.boxPoints(cv.minAreaRect(contour))
    if w[0] == x[0] and w[1] == z[1]:
        return True

def filterImageTape(input):
	input = cv.blur(input, (5,5))
	input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
	#return cv.inRange(input, np.array([100,100,100]), np.array([255,255,255]), input) #white light BGR
	return cv.inRange(input, np.array([0,0,200]), np.array([50,100,255]), input) #white light HSV

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def drawContours(input, contours):
    for i in range(len(contours)):
        color = (random() * 255, random() * 255, random() * 255)
        input = cv.drawContours(input, contours, i, color, 3)
    return input

def vision():
    #for file in listdir("oldimages"):
    #print(file)
    #frame = cv.imread("oldimages/" + file)
    frame = cv.imread("testL-Shape.png")
    image = filterImageTape(frame)
    image, contours, hierarchy = findContours(image)
    print contours
    contoursFinal = []
    for contour in contours:
        if findDiagonals(contour) is True:
            if checkCoordinates(contour) is True:
                contoursFinal.append(contour)
    print len(contoursFinal)
    frame = drawContours(frame, contoursFinal)
    """
    frame = cv.rectangle(frame, (int(CONST_IMG_WIDTH/2), 0), (int(CONST_IMG_WIDTH/2) + 4, 1000), (0,0,255))
    frame = cv.rectangle(frame, (int(findMid(contours))-2, 0), (int(findMid(contours))-2, 1000), (0,0,255))
    #cv.imwrite("newpaint/" + file, frame)
    cv.imwrite("lifeisconfusing/" + file, frame)
    """
    #contours = filterContours(contours)
        #contours = findRect(contours)
    #mid = int(findMid(contours))
    cv.imwrite("final.png", frame)

def main():
    vision()
    #getAngle()

if __name__ == "__main__":
    main()
