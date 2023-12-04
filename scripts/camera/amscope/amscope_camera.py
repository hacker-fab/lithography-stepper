# J. Kent Wirant
# Hacker Fab
# Amscope Camera Module

from camera.camera_module import *
import amcam
import time

class AmscopeCamera(CameraModule):

    camera = None

    liveIndex = 0
    liveData = None

    stillIndex = 0
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
            return True

        self.camera = amcam.Amcam.Open(None)

        if self.camera == None:
            return False

        self.setResolution(self.getAvailableResolutions()[0])
        return True


    def close(self):
        if self.isOpen():
            self.camera.Close()
        
        self.stillData = None
        self.liveData = None
        self.camera = None
        self.liveImageGood = False
        self.stillImageGood = False


    def singleCapture(self):
        self.stillImageGood = False
        self.camera.StartPullModeWithCallback(self.staticCallback, self)
        self.camera.Snap(self.stillIndex)
        return True


    def streamCapture(self):
        self.liveImageGood = False
        self.camera.StartPullModeWithCallback(self.staticCallback, self)
        return True


    @staticmethod
    def staticCallback(nEvent, ctx):
        ctx.amscopeCallback(nEvent)


    def amscopeCallback(self, nEvent):
        if (nEvent == amcam.AMCAM_EVENT_IMAGE):
            self.liveImageGood = False
            self.camera.PullImageV2(self.liveData, 24, None)
            self.liveImageGood = True

            if self.streamCaptureCallback != None:
                r = self.getResolution()
                self.streamCaptureCallback(self.liveData, r, self.ImageFormat.RGB888) # modify later

        elif nEvent == amcam.AMCAM_EVENT_STILLIMAGE:
            self.stillImageGood = False
            self.camera.PullStillImageV2(self.stillData, 24, None)
            self.stillImageGood = True

            if self.singleCaptureCallback != None:
                r = self.getResolution()
                self.singleCaptureCallback(self.stillData, r, self.ImageFormat.RGB888) # modify later

        else: # for more robust operation, add more event handlers here
            pass


    def getSingleCaptureImage(img, width, height, imageFormat):
        if not self.stillImageReady():
            return None
        r = getResolution()
        self.__copyImage(self.stillData, img, r.width, r.height, width, height, imageFormat)
        return img


    def getStreamCaptureImage(imgData, width, height, imageFormat):
        if not self.liveImageReady():
            return None
        r = getResolution()
        __copyImage(self.liveData, img, r.width, r.height, width, height, imageFormat)
        return img


    def setSingleCaptureCallback(self, callback):
        self.singleCaptureCallback = callback


    def setStreamCaptureCallback(self, callback):
        self.streamCaptureCallback = callback


    # helper function
    def __copyImage(srcData, destData, ws, hs, wd, hd, imageFormat):
        minWidth = ws if (ws < wd) else wd
        minHeight = hs if (hs < hd) else hd

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

    
    # TODO: implement separate single and stream implementations
    def getAvailableResolutions(self, mode=None):
        if self.__resolutionModes == None:
            num_resolutions = self.camera.ResolutionNumber()
            self.__resolutionModes = [None] * num_resolutions

            for i in range(0, num_resolutions):
                self.__resolutionModes[i] = self.camera.get_Resolution(i)

        return self.__resolutionModes
    
    # TODO: implement separate single and stream implementations
    def getResolution(self, mode=None):
        return self.__resolutionModes[self.liveIndex]

    # TODO: implement separate single and stream implementations
    def setResolution(self, resolution, mode=None):
        for i in range(0, len(self.__resolutionModes)):
            if self.__resolutionModes[i] is resolution or self.__resolutionModes[i] == resolution:
                self.stillIndex = i
                self.liveIndex = i
                self.camera.put_eSize(i)
                self.stillData = bytes(resolution[0] * resolution[1])
                self.liveData = bytes(resolution[0] * resolution[1])
                self.stillImageGood = False
                self.liveImageGood = False
                return True
        return False


    # camera description functions
    def getDeviceInfo(self, parameterName):
        match parameterName:
            case 'vendor':
                return self.camera.AmcamDeviceV2.displayname
            case 'name':
                return self.camera.AmcamModelV2.name
            case other:
                return None


# test suite
if __name__ == "__main__":
    def testCallback(image, resolution, format):
        print(f"{resolution[0]} {resolution[1]} {format}")

    def testCase(testName, expectedValues, actualValues):
        global testCount
        global testsPassed
        global testPrefixString

        errorStringLimit = 100

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
            print(testPrefixString + "PASSED Test '" + testName + "'")
        else:
            if(len(errorString) > errorStringLimit):
                errorString = errorString + "]"
            else:
                errorString = errorString[:-2] + "]"
            print(testPrefixString + "FAILED Test '" + testName + "': " + errorString)

        return success


    testCount = 0
    testsPassed = 0
    testPrefixString = "[AmscopeCamera] "

    camera = AmscopeCamera()
    openSuccess = camera.open()
    testCase("open()", True, openSuccess)

    if not openSuccess:
        print(testPrefixString + "Further testing requires connection to Amscope Camera")
    else:
        print(testPrefixString + camera.getDeviceInfo('name'))
        print(testPrefixString + camera.getDeviceInfo('vendor'))
        
        resolutions = camera.getAvailableResolutions()
        print(testPrefixString + "Resolutions: ", end='')

        expectedResolutionMode = []
        actualResolutionMode = []
        
        for r in resolutions:
            print(str(r) + " ", end='')
            camera.setResolution(r)
            expectedResolutionMode.append(r)
            actualResolutionMode.append(camera.getResolution())
        print()
        testCase("setResolution(ResolutionMode)", expectedResolutionMode, actualResolutionMode)

        camera.setStreamCaptureCallback(testCallback)
        camera.startStreamCapture()
        time.sleep(5)

    print(testPrefixString + f"Result: {testsPassed}/{testCount} tests passed")
