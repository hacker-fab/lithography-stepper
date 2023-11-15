# J. Kent Wirant
# Amscope Camera Module
# Hacker Fab

from camera_module import *
import amcam
import time

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
        self.stillData = bytes(self.stillWidth * self.stillHeight)

        self.camera.put_eSize(self.liveIndex)
        (self.liveWidth, self.liveHeight) = self.camera.get_Size()
        self.liveData = bytes(self.liveWidth * self.liveHeight)

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
        self.camera.StartPullModeWithCallback(self.staticCallback, None)

        # DEBUG("[CameraModule] Waiting for live image...\n")
        return True

    @staticmethod
    def staticCallback(nEvent, ctx):
        ctx.amscopeCallback(nEvent)

    def amscopeCallback(self, nEvent):
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
            self.__resolutionModes = [None] * num_resolutions

            for i in range(0, num_resolutions):
                (w, h) = self.camera.get_Resolution(i)
                self.__resolutionModes[i] = self.ResolutionMode()
                self.__resolutionModes[i].width = w
                self.__resolutionModes[i].height = h
                self.__resolutionModes[i].supportedFormats = [self.ImageFormat.RGB888]

        return self.__resolutionModes
    

    def getResolutionMode(self):
        return self.__resolutionModes[self.liveIndex]


    def setResolutionMode(self, mode):
        for i in range(0, len(self.__resolutionModes)):
            if self.__resolutionModes[i] is mode or self.__resolutionModes[i] == mode:
                self.stillIndex = i
                self.liveIndex = i
                self.camera.put_eSize(i)
                self.stillData = bytes(mode.width * mode.height)
                self.liveData = bytes(mode.width * mode.height)
                self.stillImageGood = False
                self.liveImageGood = False
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
        print(f"{width} {height} {format}")

    def testCase(testName, expectedValues, actualValues):
        global testCount
        global testsPassed

        errorStringLimit = 80

        # convert inputs to lists if necessary
        if not isinstance(expectedValues, list):
            expectedValues = [expectedValues]
        if not isinstance(actualValues, list):
            actualValues = [actualValues]
        assert len(expectedValues) == len(actualValues)

        testCount += 1
        success = True
        errorString = "(expected, got) = ["

        for i in range(0, len(expectedValues)):
            if expectedValues[i] is not actualValues[i] or expectedValues[i] != actualValues[i]:
                success = False
                if(len(errorString) <= errorStringLimit):
                    errorString += f"({expectedValues[i]}, {actualValues[i]}); "
                if(len(errorString) > errorStringLimit):
                    errorString = errorString[0:errorStringLimit] + "..."

        if success:
            testsPassed += 1
            print("[AmscopeCamera] PASSED Test '" + testName + "'")
        else:
            errorString = errorString[:-2] + "]"
            print("[AmscopeCamera] FAILED Test '" + testName + "': " + errorString)

        return success


    testCount = 0
    testsPassed = 0

    camera = AmscopeCamera()
    openSuccess = camera.open()
    testCase("open()", True, openSuccess)

    if not openSuccess:
        print("[AmscopeCamera] Further testing requires connection to Amscope Camera")
    else:
        resolutions = camera.getAvailableResolutionModes()
        print("[AmscopeCamera] Resolutions: ", end='')

        expectedResolutionMode = []
        actualResolutionMode = []
        
        for r in resolutions:
            print(str(r) + " ", end='')
            camera.setResolutionMode(r)
            expectedResolutionMode.append(r)
            actualResolutionMode.append(camera.getResolutionMode())
        print()
        testCase("setResolutionMode(ResolutionMode)", expectedResolutionMode, actualResolutionMode)

    camera.setStreamCaptureCallback(testCallback)
    camera.streamCapture()
    time.sleep(5)

    print(f"[AmscopeCamera] Result: {testsPassed}/{testCount} tests passed")
