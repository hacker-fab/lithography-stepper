# J. Kent Wirant
# Hacker Fab
# Flir Camera Module

from camera.camera_module import *
# import [...]
import time

# for the time being, leave unimplemented in public repos
class FlirCamera(CameraModule):
    # camera description functions
    def getDeviceInfo(self, parameterName):
        match parameterName:
            case 'vendor':
                return "Flir"
            case 'name':
                return "Flir Camera"
            case other:
                return None

