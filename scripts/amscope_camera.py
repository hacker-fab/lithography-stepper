# J. Kent Wirant
# Amscope Camera Module
# Hacker Fab

from camera_module import *
import amcam

class AmscopeCamera(CameraModule):

    camera = None

    liveIndex = 0
    liveWidth = 0
    liveHeight = 0
    liveData = None

    stillIndex = 0
    stillWidth = 0
    stillHeight = 0
    stillData = None

    liveImageGood = False
    stillImageGood = False

    __resolutionModes = None


    def __init__(self):
        self.singleCaptureCallback = None
        self.streamCaptureCallback = None
        self.close() # reset to known state


    def __del__(self):
        self.close() # reset to known state


    def liveImageReady(self):
        return self.liveImageGood


    def stillImageReady(self):
        return self.stillImageGood


    def isOpen(self):
        return self.camera != None


    def open(self):
        if self.isOpen():
            # DEBUG("[CameraModule] Camera is already open\n")
            return True

        self.camera = amcam.Amcam.Open(None)

        if self.camera == None:
            # DEBUG("[CameraModule] No camera found or open failed\n")
            return False

        self.getAvailableResolutionModes()

        self.camera.put_eSize(self.stillIndex)
        (self.stillWidth, self.stillHeight) = self.camera.get_Size()

        self.camera.put_eSize(self.liveIndex)
        (self.liveWidth, self.liveHeight) = self.camera.get_Size()

        # DEBUG("[CameraModule] Camera opened: live resolution %dx%d, still resolution %dx%d\n", \
        #       liveWidth, liveHeight, stillWidth, stillHeight)
        return True


    def close(self):
        if self.isOpen():
            self.camera.Close()
        
        self.stillData = None
        self.liveData = None
        self.camera = None
        self.liveImageGood = False
        self.stillImageGood = False

        # DEBUG("[CameraModule] Camera closed\n");


    def singleCapture(self):
        self.stillImageGood = False
        self.camera.StartPullModeWithCallback(self.amscopeCallback, None)
        self.camera.Snap(self.stillIndex)

        # DEBUG("[CameraModule] Waiting for still image...\n")
        return True


    def streamCapture(self):
        self.liveImageGood = False
        self.camera.StartPullModeWithCallback(self.amscopeCallback, None)

        # DEBUG("[CameraModule] Waiting for live image...\n")
        return True


    def amscopeCallback(nEvent):
        if (nEvent == amcam.AMCAM_EVENT_IMAGE):
            self.liveImageGood = False
            self.camera.PullImageV2(self.liveData, 24, None)
        
            # DEBUG("[CameraModule] Live image captured.\n")
            self.liveImageGood = True

            if self.streamCaptureCallback != None:
                self.streamCaptureCallback(self.liveData, self.liveWidth, self.liveHeight, self.ImageFormat.RGB888) # modify later

        elif nEvent == amcam.AMCAM_EVENT_STILLIMAGE:
            self.stillImageGood = False
            self.camera.PullStillImageV2(self.stillData, 24, None)
        
            # DEBUG("[CameraModule] Still image captured.\n")
            self.stillImageGood = True

            if self.singleCaptureCallback != None:
                self.singleCaptureCallback(self.stillData, self.stillWidth, self.stillHeight, self.ImageFormat.RGB888) # modify later

        else: # for more robust operation, add more event handlers here
            pass
            # DEBUG("[CameraModule] Other callback: %d\n", nEvent)


    def getSingleCaptureImage(img, width, height, imageFormat):
        if not self.stillImageReady():
            return None
        self.__copyImage(self.stillData, img, self.stillWidth, self.stillHeight, width, height, imageFormat)
        return img


    def getStreamCaptureImage(imgData, width, height, imageFormat):
        if not self.liveImageReady():
            return None
        __copyImage(self.liveData, img, self.liveWidth, self.liveHeight, width, height, imageFormat)
        return img


    def setSingleCaptureCallback(self, callback):
        self.singleCaptureCallback = callback


    def setStreamCaptureCallback(self, callback):
        self.streamCaptureCallback = callback


    # helper function
    def __copyImage(srcData, destData, ws, hs, wd, hd, imageFormat):
        minWidth = ws if (ws < wd) else wd
        minHeight = hs if (hs < hd) else hd

        # DEBUG("%d, %d\n", minWidth, minHeight)

        if True: # normally would check for format here; this assumes 24 bits per pixel
            # copy image data
            for y in range(0, minHeight):
                for x in range(0, minWidth):
                    destData[3*(wd*y + x)] = srcData[3*(ws*y + x)]
                    destData[3*(wd*y + x) + 1] = srcData[3*(ws*y + x) + 1]
                    destData[3*(wd*y + x) + 2] = srcData[3*(ws*y + x) + 2]

            # if there's extrself*(wd*y + x) + 1] = 0
                    destData[3*(wd*y + x) + 2] = 0

            # if there's extra space at the bottom of the destination, set its data to 0
            for y in range(minHeight, hd):
                for x in range(0, wd):
                    destData[3*(wd*y + x)] = 0
                    destData[3*(wd*y + x) + 1] = 0
                    destData[3*(wd*y + x) + 2] = 0


    # camera configuration functions
    def getExposureTime(self):
        pass

    def setExposureTime(self, micros):
        pass
    
    def getAvailableResolutionModes(self):
        if self.__resolutionModes == None:
            num_resolutions = self.camera.ResolutionNumber()
            self.__resolutionModes = [self.ResolutionMode()] * num_resolutions

            for i in range(0, num_resolutions):
                (w, h) = self.camera.get_Resolution(i)
                self.__resolutionModes[i].width = w
                self.__resolutionModes[i].height = h
                self.__resolutionModes[i].supportedFormats = [RGB888]

        return self.__resolutionModes
    

    def getResolutionMode(self):
        return self.__resolutionModes[self.liveIndex]


    def setResolutionMode(self, mode):
        for i in range(0, len(self.__resolutionModes)):
            if self.__resolutionModes[i] is mode or self.__resolutionModes[i] == mode:
                self.stillIndex = i
                self.liveIndex = i
                self.camera.put_eSize(i)
                return True
        return False


    # camera description functions
    def getDeviceVendor(self):
        return self.camera.AmcamDeviceV2.displayname


    def getDeviceName(self):
        return self.camera.AmcamModelV2.name


# test suite
if __name__ == "__main__":
    def testCallback(data, width, height, format):
        pass
        
    camera = AmscopeCamera()
    print("opened: " + str(camera.open()))

    print(camera.getAvailableResolutionModes())

