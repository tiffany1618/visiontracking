from picamera.array import PiRGBArray
from picamera import PiCamera
import time

class Camera():

    def __init__(self, exposure=0):
        self.camera = PiCamera()
        self.camera.exposure_compensation = exposure
        self.rawCapture = PiRGBArray(self.camera)
        time.sleep(0.1)

    def getFrame(self):
        self.camera.capture(self.rawCapture, format="bgr")
        frame = self.rawCapture.array
        self.rawCapture.truncate(0) # allow the rawCapture to be reused
        return frame
