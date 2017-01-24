import cv2 as cv
import numpy as np
import math
from camera import Camera
import time
from operator import itemgetter
#import picamera
from os import listdir
from random import random

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 480 #pixels
CONST_IMG_WIDTH = 720 #pixels
#CONST_CAMERA_HEIGHT #inches
CONST_TAPE_HEIGHT = 7 #inches
CONST_TAPE_WIDTH = 17 #inches
#CONST_CAMERA_ANGLE #convert to radians

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def takeImage():
    image = camera.getFrame()
    displayImage(image)

def filterImageTape(input):
    input = cv.blur(input, (5,5))
    input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
    #return cv.inRange(input, np.array([250,250,250]), np.array([255,255,255]), input) #white light BGR
    #return cv.inRange(input, np.array([100,200,0]), np.array([255,255,100]), input) #green light BGR
    #return cv.inRange(input, np.array([0, 150, 80]), np.array([255, 255, 200]), input) #white light HSV
    return cv.inRange(input, np.array([40, 0, 200]), np.array([100, 255, 255]), input) #green light HSV

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def highestContours(contours):
    index = [0,1]
    x0,y0,w0,h0 = cv.boundingRect(contours[0])
    x1,y1,w1,h1 = cv.boundingRect(contours[1])
    if h1 > h0:
        index = [1,0]
        temp = h0
        h0 = h1
        h1 = temp
    for i in range(2, len(contours)):
        x,y,width,height = cv.boundingRect(contours[i])
        if height > h0:
            h1 = h0
            h0 = height
            index[1] = index[0]
            index[0] = i
        elif height > h1:
            h1 = height
            index[1] = i
    return [contours[index[0]], contours[index[1]]]

def filterContours(contours):
    contoursFinal = []
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        aspectRatio = float(w)/h
        #if cv.isContourConvex(contour):
        if len(cv.approxPolyDP(contour, 5, True)) == 4:
            if aspectRatio > 0.38 and aspectRatio < 0.5:
                contoursFinal.append(contour)
    if len(contoursFinal) >= 2: #deletes duplicate contours
        contoursCopy = []
        for i in range(len(contoursFinal)):
            x,y,w,h = cv.boundingRect(contoursFinal[i])
            for j in range((i + 1), len(contoursFinal)):
                xx,yy,ww,hh = cv.boundingRect(contoursFinal[j])
                if math.fabs(x - xx) < 10 and math.fabs(y - yy) < 10:
                    contoursFinal[i] = None
        for contour in contoursFinal:
            if contour != None:
                contoursCopy.append(contour)
        contoursFinal = contoursCopy
    if len(contoursFinal) == 1: #finds cut off tape
        x,y,w,h = cv.boundingRect(contoursFinal[0])
        contours.remove(contoursFinal[0])
        for contour in contours:
            xx,yy,ww,hh = cv.boundingRect(contour)
            if math.fabs(hh - h) < 10:
                contoursFinal.append(contour)
    if len(contoursFinal) > 2:
        contoursFinal = highestContours(contoursFinal)
    """
    if len(contoursFinal) == 2:
        if cv.matchShapes(contoursFinal[0], contoursFinal[1], 1, 0.0) < 0.002:
            print("matchshapes: " + str(len(contoursFinal)))
            return contoursFinal
        else:
            return []
    """
    return contoursFinal

def drawContours(input, contours):
    for i in range(len(contours)):
        color = (random() * 255, random() * 255, random() * 255)
        input = cv.drawContours(input, contours, i, color, 3)
    return input

def approxPoly(contour):
    contour = cv.convexHull(contour)
    return cv.approxPolyDP(contour, 5, True)

def findVertices(contour):
    return cv.boxPoints(cv.minAreaRect(contour))

def pointDistance(point1, point2): #finds distance between two points
    distance = math.sqrt(((point1[0]-point2[0])*(point1[0]-point2[0]))+((point1[1]-point2[1])*(point1[1]-point2[1])))
    return distance

def findTapeHeight(vertices):
    vertices = sorted(vertices, key = itemgetter(0))
    return pointDistance(vertices[len(vertices) - 1], vertices[len(vertices) - 2])

def findTapeWidth(vertices):
    vertices = sorted(vertices, key = itemgetter(1))
    return pointDistance(vertices[len(vertices) - 1], vertices[len(vertices) - 2])

def findMidpoint(contours): #finds midpoint of tape, takes in a list of two contours
    midpoint = [0, 0]
    vertices1 = sorted(findVertices(contours[0], key = itemgetter(0)))
    vertices2 = sorted(findVertices(contours[1], key = itemgetter(0)))
    midpoint[0] = math.fabs((vertices1[len(vertices1) - 1][0] - vertices2[0][0])/2)
    midpoint[1] = math.fabs((vertices1[len(vertices1) - 1][1] - vertices2[0][1])/2)
    return midpoint

def findHeight(contours): #finds distance from bottom of image to bottom of tape
    midpoint = findMidpoint(contours)
    return (CONST_IMG_HEIGHT - midpoint[1])

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

def findDistance(height, tapeHeight):
    heightIn = (height * CONST_TAPE_HEIGHT)/tapeHeight #inches
    vertPTR = CONST_IMG_HEIGHT/CONST_VERTFOV #vertical pixels to radians
    phi = height/vertPTR 
    cameraDistance = heightIn/math.sin(phi) #direct hypotenuse
    robotDistance = math.sqrt((cameraDistance * cameraDistance) - (heightIn * heightIn))
    return robotDistance #inches
          
camera = Camera(-6)
camera.getFrame()
#camera = picamera.PiCamera()

def vision():
    interval = time.time() 
    """
    for i in range(10):
        print("taking image")
        image = camera.getFrame()
        cv.imwrite("imagesNew/tape" + str(i) + ".png", image)
        sleep(15)
    #camera.capture("stuff2.png")
    #image = cv.imread("stuff1.png")
    #print("Capture:" + str(time.time()-interval))
    """
    for file in listdir("imagesNeww"):
        print(file)
        image = cv.imread("imagesNeww/" + str(file))
        imgt = filterImageTape(image)
    #print("Filter Tape:" + str(time.time()-interval))
    #imgy = filterImageBg(image)
    #print("Filter Image Background:" + str(time.time()-interval))
    #img1, contoursy, hierarchy1 = findContours(imgy)
    #print("Find Tape Contours:" + str(time.time()-interval))
        img2, contourst, hierarchy2 = findContours(imgt)
    #print("Find Tape Contours:" + str(time.time()-interval))
        contoursFinal = filterContours(contourst)
    #print("Filter Contours:" + str(time.time()-interval))
        #image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        image = drawContours(image, contoursFinal)
        print("contoursFinal: " + str(len(contoursFinal)))
        if len(contoursFinal) == 2:
            x,y,w,h = cv.boundingRect(contoursFinal[0])
            xx,yy,ww,hh = cv.boundingRect(contoursFinal[1])
            mid = findMid(contoursFinal)
            print("mid: " + str(mid))
            angle = findAngle(mid)
            print("angle: " + str(angle))
        cv.imwrite("imagesFiltered/new" + str(file), image)
        print("\n")
    #cv.imwrite("images/tape" + str(i) + ".png", image)
    #displayImage(image)
    """
    print(len(contoursFinal))
    if len(contoursFinal) == 2:
        points = findVertices(contoursFinal[0])
        distance = findDistance(findHeight(contoursFinal), findTapeHeight(points))
        print("Distance:" + str(distance))
        angle = findAngle(contoursFinal)
        print("Angle: " + str(angle))
    else:
        print("cannot find contours...blame build")
    print("find distance:" + str(time.time()-interval))
    """
    #return image

def getAngle():
    frame = camera.getFrame()
    image = filterImageTape(frame)
    image, contours, hierarchy = findContours(image)
    contoursTape = filterContours(contours)
    frame = drawContours(frame, contoursTape)
    if len(contoursTape) == 2:
        mid = findMid(contoursTape)
        angle = findAngle(mid)
        frame = cv.rectangle(frame, (int(mid), 0), (int(mid) + 4, 1000), 255 << 16 + 255)
        isFlipped = True
        if isFlipped:
            angle *= -1
        cv.imwrite("tape.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
        return str(angle)
    elif len(contoursTape) == 1:
        return "tape not in range"
    else:
        return "could not find tape"

def main():
    vision()
    #cv.waitKey(0)
    #takeImage()
    #getAngle()

if __name__ == "__main__":
    main()
