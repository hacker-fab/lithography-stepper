import zmq
import random
import sys
import time
import cv2
import numpy as np
import json
import time
import msgpack
import stepper_cv.align as align
import camera.camera_module as camera_module
import camera.amscope.amscope_camera as amscope_camera

# search for config file
try:
    import config
    print("config file found")
    useConfig = True
except ModuleNotFoundError:
    print("config file not found")
    useConfig = False

# %% ZMQ
port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

socketimg = context.socket(zmq.PUB)
socketimg.bind("tcp://*:%s" % "5557")


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class StageControllerLowLevel:
    def __init__(self):
        self.referenceImage = None
        self.total = 0


    def updateImage(self, currentImage, referenceImage=None):
        socketimg.send(currentImage)
        self.total += 1

        if referenceImage is None:
            referenceImage = self.referenceImage
        else:
            self.referenceImage = referenceImage
        # if no reference set, use current image as reference
        if referenceImage is None:
            referenceImage = currentImage
            self.referenceImage = referenceImage

        displacement = align.find_displacement(referenceImage, currentImage)
        if displacement is not None:
            dx, dy, theta = displacement
            print(f"dx{dx}, dy={dy}, theta={theta}")
            socket.send(msgpack.packb([
                    time.time_ns(),
                    dx.tolist(),
                    dy.tolist(),
                    theta.tolist(),
                    referenceImage.tolist(),
                    currentImage.tolist()
                ]))
            return True

        return False


if __name__ == '__main__':
    stage = StageControllerLowLevel()

    def cameraCallback(image, dimensions, format):
        print('image captured')
        grayscale = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        stage.updateImage(grayscale)

    if useConfig:
        camera = config.camera
    else:
        camera = amscope_camera.AmscopeCamera()

    if not camera.open():
        print('failed to start camera')
        exit(-1)
    camera.setSetting('image_format', "mono8")
    camera.setStreamCaptureCallback(cameraCallback)
    if not camera.startStreamCapture():
        print('failed to start stream capture')
        exit(-1)
    print('Testing stage controller')
    time.sleep(5)
