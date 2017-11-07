import cv2 as cv
import numpy as np
from vision import filterImageTape, findContours, filterContours

def isConvex(contour):
    return cv.isContourConvex(contour)

def findVertices(contour):
    #return number of vertices
    hi = 0

def findDiagonals(contour):
    # return boolean isDiagonalsEqual
    w, x, y, z = cv.boxPoints(contour)
    leftDiagonal = sqrt((w[0] - y[0]) * (w[0] - y[0]) + (w[1] - y[1]) * (w[1] - y[1]))
    rightDiagonal = sqrt((x[0] - z[0]) * (x[0] - z[0]) + (x[1] - z[1]) * (x[1] - z[1]))
    if leftDiagonal == rightDiagonal:
        return true

def checkCoordinates(contour):
    # boolean coordinateMatch
    w, x, y, z = cv.boxPoints(contour)
    if w[0] == x[0] and w[1] = z[1]:
        return true

def main():
    frame = cv.imread("testrect")
    image = filterImageTape(frame)
    image, contours, hierarchy = findContours(image)
    contoursRect = []
    contoursLshape = []
    for contour in contours:
        if isConvex:
            contoursRect.append(contour)

if __name__ == "__main__":
    main()
