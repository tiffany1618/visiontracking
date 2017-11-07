import cv2 as cv
import numpy as np
import math
#from camera import Camera
import time
from operator import itemgetter
from os import listdir
from random import random

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 800 #pixels
CONST_IMG_WIDTH = 1280 #pixels
CONST_DIST_RATIO = 6.25 / 5 #ratio of distance between tapes to height of tape
CONST_TAPE_HEIGHT = 7 #inches

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def filterImageTape(input):
	input = cv.blur(input, (5,5))
	input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
	#return cv.inRange(input, np.array([100,100,100]), np.array([255,255,255]), input) #white light BGR
	return cv.inRange(input, np.array([0,0,200]), np.array([50,100,255]), input) #white light HSV

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours):
    contoursFinal = []
    print(str(len(contours)))
    if len(contours) > 1: #deletes duplicate contours
        contoursCopy = []
        for i in range(len(contours)):
            x,y,w,h = cv.boundingRect(contours[i])
            for j in range((i + 1), len(contours)):
                xx,yy,ww,hh = cv.boundingRect(contours[j])
                if math.fabs(x - xx) < 10 and math.fabs(y - yy) < 10:
                    contours[i] = None
        for contour in contours:
            if contour != None:
                contoursCopy.append(contour)
        contours = contoursCopy
        print("aspectratio: " + str(len(contoursCopy)))
    #find vert rectangle
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        aspectRatio = float(w)/h
        if w > 10 and h > 20:
            if aspectRatio > 0.3 and aspectRatio < 0.6:
            	contoursFinal.append(contour)

    print("aspectratio: " + str(len(contoursFinal)))
    if len(contoursFinal) > 2:
        contoursHolder = contoursFinal
        contoursFinal = []
        match = cv.matchShapes(contoursHolder[0], contoursHolder[1], 3, 0.0)
        matches = [0,1]
        for i in range(len(contoursHolder)):
            for j in range(i + 1, len(contoursHolder)):
                if cv.matchShapes(contoursHolder[i], contoursHolder[j], 3, 0.0) < match:
                    match = cv.matchShapes(contoursHolder[i], contoursHolder[j], 3, 0.0)
                    matches = [i,j]
        contoursFinal.append(contoursHolder[matches[0]])
        contoursFinal.append(contoursHolder[matches[1]])
    if len(contoursFinal) ==  2:
        print("matchshapes: " + str(cv.matchShapes(contoursFinal[0], contoursFinal[1], 3, 0.0)))
        if cv.matchShapes(contoursFinal[0], contoursFinal[1], 3, 0.0) > 0.4:
            contoursFinal = []
        print("matchshapes: " + str(len(contoursFinal)))
    if len(contoursFinal) == 1: #finds cut off tape
        x,y,w,h = cv.boundingRect(contoursFinal[0])
        for contour in contours:
            xx,yy,ww,hh = cv.boundingRect(contour)
            if xx != x and yy != y and math.fabs(hh - h) < 10:
                contoursFinal.append(contour)
        print("cutoff: " + str(len(contoursFinal)))
    return contoursFinal

def drawContours(input, contours):
    for i in range(len(contours)):
        color = (random() * 255, random() * 255, random() * 255)
        input = cv.drawContours(input, contours, i, color, 3)
    return input

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

def estimateMid(contour):
    x,y,w,h = cv.boundingRect(contour)
    vertices = findVertices(contour)
    xss = [vertex[0] for vertex in vertices]
    xss = sorted(xss)
    if (x + w/2) <= (CONST_IMG_WIDTH / 2):
        xdist = (xss[0][0] + xss[0][1]) / 2
        mid = xdist - (CONST_DIST_RATIO * h / 2)
    if (x + w/2) > (CONST_IMG_WIDTH / 2):
        xdist = ((xss[0][len(xss) - 1] + xss[0][len(xss) - 2]) / 2)
        mid = xdist + (CONST_DIST_RATIO * h / 2)
    return mid

def findAngle(mid):
    radians = (mid - CONST_IMG_WIDTH / 2) * CONST_HORZFOV / CONST_IMG_WIDTH
    return math.degrees(radians)

#camera = Camera(-7)
#camera.getFrame()

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

def vision():
    for file in listdir("oldimages"):
        print(file)
        #frame = cv.imread("oldimages/" + file)
        frame = cv.imread("oldimages/" + file)
        #print("readimage: " + str(time.time() - currentTime))
        image = filterImageTape(frame)
        #print("filter image: " + str(time.time() - currentTime))
        image, contours, hierarchy = findContours(image)
        #print("find contours: " + str(time.time() - currentTime))
        contours = filterContours(contours)
        #contours = findRect(contours)
        print(len(contours))
        print("filter contours: " + str(time.time() - currentTime))
        print(len(contours))
        mid = int(findMid(contours))
        frame = drawContours(frame, contours)
        frame = cv.rectangle(frame, (int(CONST_IMG_WIDTH/2), 0), (int(CONST_IMG_WIDTH/2) + 4, 1000), (0,0,255))
        frame = cv.rectangle(frame, (int(findMid(contours))-2, 0), (int(findMid(contours))-2, 1000), (0,0,255))
        #cv.imwrite("newpaint/" + file, frame)
        angle = findAngle(mid) * -1
        print("Angle: " + str(angle))

        distance = findDistance(findHeight(contours[0]), findTapeHeight(contours[0]))
        print("Distance: " + str(distance))

        print(str(time.time() - currentTime))
        #print("writeimage: " + str(time.time() - currentTime))
        #if len(contours) == 1:
            #angle = findAngle(estimateMid(contours[0]))
            #print(angle)
        #if len(contours) == 2:
            #mid = findMid(contours)
            #angle = findAngle(mid)
            #print("findangle: " + str(time.time() - currentTime))
            #frame = cv.rectangle(frame, (int(mid), 0), (int(mid) + 4, 1000), (255,0,0))
            #print(angle)
        #print("\n")

        cv.imwrite("lifeisconfusing/" + file, frame)
        #cv.imwrite("image.png", frame)

def getAngle():
	isFlipped = True
	frame = camera.getFrame()
	#cv.imwrite("original1.png", frame)
	image = filterImageTape(frame)
	image, contours, hierarchy = findContours(image)
	contoursTape = filterContours(contours)
	#frame = drawContours(frame, contoursTape)
	#cv.imwrite("contours1.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
	print(len(contoursTape))
	if len(contoursTape) == 2:
		mid = findMid(contoursTape)
		angle = findAngle(mid)
		#frame = cv.rectangle(frame, (int(mid), 0), (int(mid) + 4, 1000), 255 << 16 + 255)
		#cv.imwrite("tape1.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
		if isFlipped:
			angle *= -1
		print(angle)
		return str(angle)
	elif len(contoursTape) == 1:
		"""
        angle = findAngle(estimateMid(contoursTape[0]))
        cv.imwrite("tape1.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
        if isFlipped:
            angle *= -1
        print(angle)
        return str(angle)
		"""
		return "one tape found"
	else:
		return "could not find tape"

def main():
    vision()
    #getAngle()

if __name__ == "__main__":
    main()
