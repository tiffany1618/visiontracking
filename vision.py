import cv2 as cv
import math
import numpy as np
import picamera
import time
from camera import Camera

CONST_VERTFOV = math.radians(41.41) #vertical field of view
CONST_HORZFOV = math.radians(53.50) #horizontal field of view
CONST_IMG_HEIGHT = 1080 #pixels
CONST_IMG_WIDTH = 1920 #pixels
#CONST_CAMERA_HEIGHT #inches
CONST_TAPE_HEIGHT = 7 #inches
CONST_TAPE_WIDTH = 17 #inches
#CONST_CAMERA_ANGLE #convert to radians

def displayImage(image):
    #cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
    #cv.imshow("stuffs", image)
    #cv.waitKey(0)
    pass

def filterImageTape(input):
    input = cv.cvtColor(input, cv.COLOR_BGR2HSV)
    #return cv.inRange(input, np.array([250,250,250]), np.array([255,255,255]), input) #white light BGR
    #return cv.inRange(input, np.array([100,200,0]), np.array([255,255,100]), input) #green light BGR
    #return cv.inRange(input, np.array([0, 0, 235]), np.array([20, 20, 255]), input) #white light HSV
    return cv.inRange(input, np.array([40, 0, 200]), np.array([100, 255, 255]), input) #green light HSV

def filterImageBg(input):
    return cv.inRange(input, np.array([0,100,150]), np.array([50,200,255]), input)

def findContours(input):
    return cv.findContours(input, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

def filterContours(contours):
    contoursFinal = []
    for contour in contours:
        x,y,width,height = cv.boundingRect(contour)
        if width > 50 and width < 1000 and height > 50 and height < 1000:
            contoursFinal.append(contour)
    return contoursFinal

def drawContours(input, contours):
    return cv.drawContours(input, contours, -1, (0,0,255), 3)

def approxPoly(contour):
    contour = cv.convexHull(contour)
    return cv.approxPolyDP(contour, 5, True)

def findVertices(contour):
    return cv.boxPoints(cv.minAreaRect(contour))

def pointsX(point):
    return point[0]

def pointsY(point):
    return point[1]

def sortPointsY(points): #sorts points from greatest to least y value
    points = sorted(points, key=pointsY)
    points.reverse()
    return points

def sortPointsX(points): #sorts points from greatest to least x value
    points = sorted(points, key=pointsX)
    points.reverse()
    return points

def pointDistance(point1, point2): #finds distance between two points
    distance = math.sqrt(((point1[0]-point2[0])*(point1[0]-point2[0]))+((point1[1]-point2[1])*(point1[1]-point2[1])))
    return distance

def findTapeHeight(vertices):
    vertices = sortPointsX(vertices)
    return pointDistance(vertices[0], vertices[1])

def findTapeWidth(vertices):
    vertices = sortPointsY(vertices)
    return pointDistance(vertices[0], vertices[1])

def findMidpoint(contours): #finds midpoint of tape, takes in a list of two contours
    midpoint = [0, 0]
    vertices1 = sortPointsX(findVertices(contours[0]))
    vertices2 = sortPointsX(findVertices(contours[1]))
    print((vertices1))
    print((vertices2))
    midpoint[0] = math.fabs((vertices1[len(vertices1)-1][0] - vertices2[0][0])/2)
    midpoint[1] = math.fabs((vertices1[len(vertices1)-1][1] - vertices2[0][1])/2)
    print(midpoint[0])
    return midpoint

def findMidTape(contours): #finds distance from center of image to midpoint of tape
    midpoint = findMidpoint(contours)
    return (midpoint[0] - (CONST_IMG_WIDTH/2)) #negative:left, positive:right

def findHeight(contours): #finds distance from bottom of image to bottom of tape
    midpoint = findMidpoint(contours)
    return (CONST_IMG_HEIGHT - midpoint[1])

def findAngleOld(contours):
    horzPTR = CONST_IMG_WIDTH/CONST_HORZFOV #horizontal pixels to radians
    angle = findMidTape(contours)/horzPTR #angle in radians; left:negative, right:positive
    return math.degrees(angle) #degrees

def findAngle(contours, mid):
    verticess = [findVertices(contour) for contour in contours]
    xss = [[vertex[0] for vertex in vertices] for vertices in verticess]
    xss = [sorted(xs) for xs in xss]
    if xss[0][0] > xss[1][0]:
        temp = xss[1]
        xss[1] = xss[0]
        xss[0] = temp
    left = xss[0][len(xss[0]) - 1]
    right = xss[1][0]
    mid = (left + right) / 2
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
    image = camera.getFrame()
    #cv.imwrite("images/tape" + str(i) + ".png", image)
    #camera.capture("stuff2.png")
    #image = cv.imread("stuff1.png")
    #print("Capture:" + str(time.time()-interval))

    imgt = filterImageTape(image)
    print("Filter Tape:" + str(time.time()-interval))
    #imgy = filterImageBg(image)
    #print("Filter Image Background:" + str(time.time()-interval))
    #img1, contoursy, hierarchy1 = findContours(imgy)
    #print("Find Tape Contours:" + str(time.time()-interval))
    img2, contourst, hierarchy2 = findContours(imgt)
    print("Find Tape Contours:" + str(time.time()-interval))
    contoursFinal = filterContours(contourst)
    print("Filter Contours:" + str(time.time()-interval))
    image = drawContours(image, contoursFinal)
    cv.imwrite("tape.png", image)
    #cv.imwrite("images/tape" + src(i) + ".png", image)
    #displayImage(image)
    print(len(contoursFinal))
    if len(contoursFinal) == 2:
        points = findVertices(contoursFinal[0])
        #distance = findDistance(findHeight(contoursFinal), findTapeHeight(points))
        #print("Distance:" + str(distance))
        angle = findAngle(contoursFinal)
        print("Angle: " + str(angle))
    else:
        print("cannot find contours...blame build")
    print("find distance:" + str(time.time()-interval))
    #return image

def main():
    vision()
    cv.waitKey(0)

if __name__ == "__main__":
    main()

def getAngle():
    frame = camera.getFrame()
    #image = cv.imread("stuff6.png")
    image = filterImageTape(frame)
    image, contours, hierarchy = findContours(image)
    contoursTape = filterContours(contours)
    frame = drawContours(frame, contoursTape)
    if len(contoursTape) == 2:
        mid = 0.0
        angle = findAngle(contoursTape, mid)
        frame = cv.rectangle(frame, (int(mid), 0), (int(mid) + 4, 1000), 255 << 16 + 255)
        isFlipped = True
        if isFlipped:
            angle *= -1
        cv.imwrite("tape.png", cv.cvtColor(frame, cv.COLOR_BGR2HSV))
        return str(angle)
    elif len(contoursTape) > 0:
        return "could not find tape"
    else:
        return "nope"
	
	
