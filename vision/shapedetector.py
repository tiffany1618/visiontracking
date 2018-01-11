
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
CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_DIST_RATIO = 6.25 / 5 #ratio of distance between tapes to height of tape
CONST_TAPE_HEIGHT = 7 #inches

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def findDiagonals(contour):
    # return boolean isDiagonalsEqual
    w, x, y, z = cv.boxPoints(cv.minAreaRect(contour))
    leftDiagonal = math.sqrt((w[0] - y[0]) * (w[0] - y[0]) + (w[1] - y[1]) * (w[1] - y[1]))
    rightDiagonal = math.sqrt((x[0] - z[0]) * (x[0] - z[0]) + (x[1] - z[1]) * (x[1] - z[1]))
    if math.fabs(leftDiagonal - rightDiagonal) < 5:
        return True

def checkConvex(contour):
    k = cv.isContourConvex(contour)
    return k
"""
def checkCoordinates(contour):
    # boolean coordinateMatch
    w, x, y, z = cv.boxPoints(cv.minAreaRect(contour))
    if math.fabs(w[0] - x[0]) < 5 and math.fabs(w[1] - z[1]) < 5 :
        return True
"""
def filterImageTape(input):
	input = cv.blur(input, (5,5))
	input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
	#return cv.inRange(input, np.array([100,100,100]), np.array([255,255,255]), input) #white light BGR
	return cv.inRange(input, np.array([0,0,200]), np.array([50,100,255]), input) #white light HSV

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours):
    contoursFinal = []
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        aspectRatio = float(w)/h
        if w > 36 and h > 70:
            if aspectRatio > 0.4 and aspectRatio < 0.5:
            	contoursFinal.append(contour)
    return contoursFinal

def drawContours(input, contours):
    for i in range(len(contours)):
        color = (random() * 255, random() * 255, random() * 255)
        input = cv.drawContours(input, contours, i, color, 3)
    return input

def storeVertices(contours):
    vertices = []
    for contour in contours:
        w, x, y, z = cv.boxPoints(cv.minAreaRect(contour))
    #store vertices after only 2 rect remaining

def findTwoRect(contours):
    yCoord = []
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        yCoord.append(y)
        print y
    one = 0
    two = len(contours) - 1
    idif = math.fabs(yCoord[0] - yCoord[len(contours) - 1])
    for i in range(0, len(yCoord) - 1):
        dif = math.fabs(yCoord[i] - yCoord[i + 1])
        print idif
        if dif < idif:
            one = i
            two = i + 1
            idif = dif
    contoursFinal = [contours[one], contours[two]]
    return contoursFinal
    #compare y coordinates

#------
def findVertices(contour):
    return cv.boxPoints(cv.minAreaRect(contour))

def findMid(contours):
    verticess = [findVertices(contour) for contour in contours]
    xss = [[vertex[0] for vertex in vertices] for vertices in verticess]
    xss = [sorted(xs) for xs in xss]
    if xss[0][0] > xss[1][0]:
        temp = xss[1]
        xss[1] = xss[0]
        xss[0] = temp
    left = xss[0][len(xss[0]) - 1]
    right = xss[1][0]
    return ((left + right) / 2)

def findAngle(mid):
    radians = (mid - CONST_IMG_WIDTH / 2) * CONST_HORZFOV / CONST_IMG_WIDTH
    return math.degrees(radians)

def findBottomY(points):
     lowestY = points[0][0]
     secondLowestY = points[1][0] # [0] at end needed to unpack point
     for point in points:
         point = point[0] # for unpacking point
         if point[1] < lowestY[1]:
             secondLowestY = lowestY
             lowestY = point
         elif point[1] > secondLowestY[1]:
             secondLowestY = point
     return (lowestY, secondLowestY)

def findTopY(points):
     highestY = points[0][0]
     secondHighestY = points[1][0] # [0] at end needed to unpack point
     for point in points:
         point = point[0] # for unpacking point
         if point[1] > highestY[1]:
             secondHighestY = highestY
             highestY = point
         elif point[1] > secondHighestY[1]:
             secondHighestY = point
     return (highestY, secondHighestY)

def findHeight(vertices):
    verticess = findVertices(vertices)
    bottomY1, bottomY2 = findBottomY(vertices)
    return (CONST_IMG_HEIGHT - bottomY1[1])

def findTapeHeight(vertices):
    bottomY1, bottomY2 = findBottomY(vertices)
    topY1, topY2 = findTopY(vertices)
    return (bottomY1[1] - topY1[1])

def findDistance(height, tapeHeight):
     heightIn = (height * CONST_TAPE_HEIGHT)/tapeHeight #inches
     vertPTR = CONST_IMG_HEIGHT/CONST_VERTFOV #vertical pixels to radians
     phi = height/vertPTR
     cameraDistance = heightIn/math.sin(phi) #direct hypotenuse
     robotDistance = math.sqrt((cameraDistance * cameraDistance) - (heightIn * heightIn))
     return robotDistance #inches
#-----

def vision():
    for file in listdir("oldimages"):
    #print(file)
        frame = cv.imread("oldimages/" + file)
        #frame = cv.imread("testrect.png")
        #frame = cv.imread("test.png")
        image = filterImageTape(frame)
        image, contours, hierarchy = findContours(image)
        print len(contours)
        contoursCheck = []
        contoursFinal = []
        contours = filterContours(contours)
        if len(contours) > 2:
            contours = findTwoRect(contours)
        for contour in contours:
            if findDiagonals(contour) is True:
                contoursFinal.append(contour)
        print len(contoursFinal)
        frame = drawContours(frame, contoursFinal)
        #cv.imwrite("paintimages/" + file, frame)
        #distance and angle
        mid = int(findMid(contours))
        frame = drawContours(frame, contours)
        frame = cv.rectangle(frame, (int(CONST_IMG_WIDTH/2), 0), (int(CONST_IMG_WIDTH/2) + 4, 1000), (0,0,255))
        frame = cv.rectangle(frame, (int(findMid(contours))-2, 0), (int(findMid(contours))-2, 1000), (0,0,255))
        angle = findAngle(mid) * -1
        print("Angle: " + str(angle))
        distance = findDistance(findHeight(contours[0]), findTapeHeight(contours[0]))
        print("Distance: " + str(distance))
        cv.imwrite("paintimages/" + file, frame)
    #cv.imwrite("final.png", frame)


def main():
    vision()
    #getAngle()

if __name__ == "__main__":
    main()

#Eliminate false contours. Set width and height range. Store/save each vertex (Create new method)
