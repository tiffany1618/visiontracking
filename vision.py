import cv2 as cv
import math
import numpy as np
import picamera
import time
from camera import Camera

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 1944 #pixels
CONST_IMG_WIDTH = 2592 #pixels
#CONST_CAMERA_HEIGHT #inches
CONST_TAPE_HEIGHT = 7 #inches
#CONST_TAPE_WIDTH #inches
#CONST_CAMERA_ANGLE #convert to radians

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def filterImageTape(input):
    #return cv.inRange(input, np.array([250,250,250]), np.array([255,255,255]), input) #white light
    return cv.inRange(input, np.array([100,200,0]), np.array([255,255,100]), input) #green light

def filterImageBg(input):
    return cv.inRange(input, np.array([0,100,150]), np.array([50,200,255]), input)

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours1):
    contoursFinal = []
    for contour1 in contours1:
#        for contour2 in contours2:
#            if cv.matchShapes(contour1, contour2, 1, 0.0) < 0.001:
        x,y,width,height = cv.boundingRect(contour1)
        if(width > 200 and width < 500 and height > 200 and height < 500):
            contoursFinal.append(contour1)
    return contoursFinal

def drawContours(input, contours):
    return cv.drawContours(input, contours, -1, (0,0,255), 3)

def findVertices(contour):
    contour = cv.convexHull(contour)
    return cv.approxPolyDP(contour, 5, True)

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
    bottomY1, bottomY2 = findBottomY(vertices)
    return (CONST_IMG_HEIGHT - bottomY1[1])

def findTapeHeight(vertices):
    bottomY1, bottomY2 = findBottomY(vertices)
    topY1, topY2 = findTopY(vertices)
    return math.fabs(bottomY1[1] - topY1[1])

#def findAngle():
    #findAngle!

def findDistance(height, tapeHeight):
    heightIn = (height * CONST_TAPE_HEIGHT)/tapeHeight #inches
    vertPTR = CONST_IMG_HEIGHT/CONST_VERTFOV #vertical pixels to radians
    phi = height/vertPTR 
    cameraDistance = heightIn/math.sin(phi) #direct hypotenuse
    robotDistance = math.sqrt((cameraDistance * cameraDistance) - (heightIn * heightIn))
    return robotDistance #inches
          
#camera = Camera()
#camera.getFrame()
#camera = picamera.PiCamera()

def doTheThing():
    interval = time.time() 

    #image = camera.getFrame()
    #camera.capture("stuffGreen.png")
    image = cv.imread("stuffGreen.png")
    print("Capture:" + str(time.time()-interval))

    imgt = filterImageTape(image)
    print("Filter Tape:" + str(time.time()-interval))
#    imgy = filterImageBg(image)
#    print("Filter Image Background:" + str(time.time()-interval))
#    img1, contoursy, hierarchy1 = findContours(imgy)
#    print("Find Tape Contours:" + str(time.time()-interval))
    img2, contourst, hierarchy2 = findContours(imgt)
    print("Find Tape Contours:" + str(time.time()-interval))
    contoursFinal = filterContours(contourst)
    print("Filter Contours:" + str(time.time()-interval))
    image = drawContours(image, contoursFinal)
    if len(contoursFinal) != 0:
        distance = findDistance(findHeight(contoursFinal[0]), findTapeHeight(contoursFinal[0]))
        print("Distance:" + str(distance))
    else:
        print("no contours found")
    print("find distance:" + str(time.time()-interval))
    return image

image = doTheThing()
displayImage(image)

	
	
