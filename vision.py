import cv2 as cv
import numpy as np
import math
from camera import Camera
import time
from operator import itemgetter
from os import listdir
from random import random

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 480 #pixels
CONST_IMG_WIDTH = 720 #pixels
CONST_DIST_RATIO = 6.25 / 5 #ratio of distance between tapes to height of tape

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def filterImageTape(input):
    input = cv.blur(input, (5,5))
    input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
    return cv.inRange(input, np.array([0,150,150]), np.array([50,255,255]), input) #white light HSV
    #return cv.inRange(input, np.array([100,100,100]), np.array([255,255,255]), input) #white light BGR

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours):
    contoursFinal = []
    print(str(len(contours)))
    if len(contours) > 1: #deletes duplicate contours
        contoursCopy = []
        for i in range(len(contours) - 1):
            x,y,w,h = cv.boundingRect(contours[i])
            for j in range((i + 1), len(contours)):
                xx,yy,ww,hh = cv.boundingRect(contours[j])
                if math.fabs(x - xx) < 10 and math.fabs(y - yy) < 10:
                    contours[i] = None
        for contour in contours:
            if contour != None:
                contoursCopy.append(contour)
        contours = contoursCopy
        print("duplicate: " + str(len(contours)))
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        aspectRatio = float(w)/h
        if w > 10 and h > 20:
            if aspectRatio > 0.3 and aspectRatio < 0.6:
                contoursFinal.append(contour)
    print("aspectratio: " + str(len(contoursFinal)))
    if len(contoursFinal) ==  2:
        if cv.matchShapes(contoursFinal[0], contoursFinal[1], 3, 0.0) > 0.4:
            contoursFinal = []
        print("matchshapes: " + str(len(contoursFinal)))
    elif len(contoursFinal) == 1: #finds cut off tape
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

camera = Camera(-6)
camera.getFrame()

def vision():
    currentTime = time.time()
    #for file in listdir("imagesWhite"):
        #print(file)
    #frame = camera.getFrame()
    ret, frame = cap.read()
    #print("read image: " + str(time.time() - currentTime))
    #frame = cv.imread("imagesWhite/tapew8.png")
    print(cap.get(3))
    print(cap.get(4))
    image = filterImageTape(frame)
    print("filter image: " + str(time.time() - currentTime))
    image, contours, hierarchy = findContours(image)
    print("find contours: " + str(time.time() - currentTime))
    print(len(contours))
    contours = filterContours(contours)
    print("filter contous: " + str(time.time() - currentTime))
    print(len(contours))
    #cv.imwrite("imagesFilteredWhite/new" + str(file), frame)
    frame = drawContours(frame, contours)
    cv.imwrite("image.png", frame)
    if len(contours) == 1:
        angle = findAngle(estimateMid(contours[0]))
        print(angle)
    if len(contours) == 2:
        angle = findAngle(findMid(contours))
        print(angle)
    print("\n")

def getAngle():
    isFlipped = True
    frame = camera.getFrame()
    cv.imwrite("original.png", frame)
    image = filterImageTape(frame)
    image, contours, hierarchy = findContours(image)
    contoursTape = filterContours(contours)
    frame = drawContours(frame, contoursTape)
    cv.imwrite("contours.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
    print(len(contoursTape))
    if len(contoursTape) == 2:
        angle = findAngle(findMid(contoursTape))
        frame = cv.rectangle(frame, (int(mid), 0), (int(mid) + 4, 1000), 255 << 16 + 255)
        cv.imwrite("tape.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
        if isFlipped:
            angle *= -1
        print(angle)
        return str(angle)
    elif len(contoursTape) == 1:
        angle = findAngle(estimateMid(contoursTape[0]))
        cv.imwrite("tape.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
        if isFlipped:
            angle *= -1
        print(angle)
        return str(angle)
    else:
        return "could not find tape"

def main():
    vision()

if __name__ == "__main__":
    main()
