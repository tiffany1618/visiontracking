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

def displayImage(image):
    cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    cv.imshow("stuffs", image)
    cv.waitKey(0)

def filterImageTape(input):
    input = cv.blur(input, (5,5))
    input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
    #return cv.inRange(input, np.array([250,250,250]), np.array([255,255,255]), input) #white light BGR
    #return cv.inRange(input, np.array([100,200,0]), np.array([255,255,100]), input) #green light BGR
    #return cv.inRange(input, np.array([0, 150, 80]), np.array([255, 255, 200]), input) #white light HSV
    return cv.inRange(input, np.array([40, 0, 200]), np.array([100, 255, 255]), input) #green light HSV

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours):
    contoursFinal = []
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
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        aspectRatio = float(w)/h
        if w > 10 and h > 10:
            if aspectRatio > 0.3 and aspectRatio < 0.5:
                contoursFinal.append(contour)
    if len(contoursFinal) == 2:
        if cv.matchShapes(contoursFinal[0], contoursFinal[1], 3, 0.0) > 0.1:
            contoursFinal = []
    if len(contoursFinal) == 1: #finds cut off tape
        x,y,w,h = cv.boundingRect(contoursFinal[0])
        contours.remove(contoursFinal[0])
        for contour in contours:
            xx,yy,ww,hh = cv.boundingRect(contour)
            if math.fabs(hh - h) < 10:
                contoursFinal.append(contour)
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

def findAngle(mid):
    radians = (mid - CONST_IMG_WIDTH / 2) * CONST_HORZFOV / CONST_IMG_WIDTH
    return math.degrees(radians)

camera = Camera(-6)
camera.getFrame()

def vision():
    for file in listdir("imagesNeww"):
        print(file)
        frame = cv.imread("imagesNeww/" + str(file))
        image = filterImageTape(frame)
        image, contours, hierarchy = findContours(image)
        contours = filterContours(contours)
        print(len(contours))
        frame = drawContours(frame, contours)
        cv.imwrite("imagesFiltered/new" + str(file), frame)
        print("\n")
    """
    frame = cv.imread("image.png")
    image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    image = cv.inRange(image, (30), (100), image) 
    image, contours, hierarchy = cv.findContours(image, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    contourss = []
    for contour in contours:
        x,y,w,h = cv.boundingRect(contour)
        if w > 20 and h > 20:
            contourss.append(contour)
    print(len(contourss))
    contourss = filterContours(contourss)
    print(len(contourss))
    frame = drawContours(frame, contourss)
    displayImage(frame)
    """

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

if __name__ == "__main__":
    main()
