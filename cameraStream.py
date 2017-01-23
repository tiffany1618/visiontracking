import cv2 as cv
import numpy as np

cv.namedWindow("stuffs")
vc = cv.VideoCapture(0)
vc.open(0)
print(vc.isOpened())

if vc.isOpened():
    print("is opened")
    isOpened, frame = vc.read()
else:
    isOpened = False

while isOpened:
    isOpened, frame = vc.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow("stuffs", frame)
    key = cv.waitKey(0)
    if key == 27: #esc key
        vc.release()
        break
