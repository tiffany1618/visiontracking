import cv2 as cv
import numpy as np

cv.namedWindow("stuffs", cv.WINDOW_NORMAL)
vc = cv.VideoCapture(0)
vc.open(0)

if vc.isOpened():
    print("streaming")
    ret, frame = vc.read()
else:
    ret = False

vc.set(3, 320)
vc.set(4, 240)
vc.set(5, 7.5)
while ret:
    ret, frame = vc.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #ret = vc.set(3, 320)
    #ret = vc.set(4, 240)
    #ret = vc.set(5, 7.5)
    cv.imshow("stuffs", frame)
    #cv.waitKey(50) #4 fps
    print("width: " + str(vc.get(3)))
    print("height: " + str(vc.get(4)))
    print("fps: " + str(vc.get(5)))
    print("format: " + str(vc.get(8)))
    print("\n")
    if cv.waitKey(1) & 0xFF == ord('q'):
        vc.release()
        break

