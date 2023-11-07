# J. Kent Wirant
# Amscope Camera Module
# Hacker Fab

import camera_module
import amcam

class AmscopeCamera(CameraModule):
    liveIndex = 1;
    stillIndex = 1;

    camera = None

    liveWidth = 0
    liveHeight = 0
    liveData = None

    stillWidth = 0
    stillHeight = 0
    stillData = None

    liveImageGood = False
    stillImageGood = False

    def __init__():
        singleCaptureCallback = None
        streamCaptureCallback = None
        closeCamera() # reset to known state

    def __del__(self)
        closeCamera() # reset to known state

    def liveImageReady(self):
        return liveImageGood

    def stillImageReady(self):
        return stillImageGood

    def isOpen(self):
        return camera != None

    def openCamera(self):
        if isOpen():
            # DEBUG("[CameraModule] Camera is already open\n")
            return True

        camera = amcam.Amcam.Open(None)

        if camera == None:
            # DEBUG("[CameraModule] No camera found or open failed\n")
            return False

        camera.put_eSize(stillIndex)
        (stillWidth, stillHeight) = camera.get_Size()

        camera.put_eSize(liveIndex)
        (liveWidth, liveHeight) = camera.get_Size()

        # DEBUG("[CameraModule] Camera opened: live resolution %dx%d, still resolution %dx%d\n", \
        #       liveWidth, liveHeight, stillWidth, stillHeight)
        return True

    def closeCamera(self):
        if isOpen()
            camera.Close()
        
        stillData = None
        liveData = None
        camera = None
        liveImageGood = False
        stillImageGood = False

        # DEBUG("[CameraModule] Camera closed\n");

    def singleCapture(self):
        stillImageGood = False
        camera.StartPullModeWithCallback(amscopeCallback, None)
        camera.Snap(stillIndex)

        # DEBUG("[CameraModule] Waiting for still image...\n")
        return True

    def streamCapture(self):
        liveImageGood = False
        camera.StartPullModeWithCallback(amscopeCallback, None)

        # DEBUG("[CameraModule] Waiting for live image...\n")
        return True

    def amscopeCallback(nEvent):
        if (nEvent == amcam.AMCAM_EVENT_IMAGE):
            liveImageGood = False
            camera.PullImageV2(liveData, 24, None)
        
            # DEBUG("[CameraModule] Live image captured.\n")
            liveImageGood = True

            if streamCaptureCallback != None:
                streamCaptureCallback(liveData, liveWidth, liveHeight, RGB888) # modify later

        elif nEvent == amcam.AMCAM_EVENT_STILLIMAGE:
            stillImageGood = False
            camera.PullStillImageV2(stillData, 24, None)
        
            # DEBUG("[CameraModule] Still image captured.\n")
            stillImageGood = True

            if singleCaptureCallback != None:
                singleCaptureCallback(stillData, stillWidth, stillHeight, RGB888) # modify later

        else: # for more robust operation, add more event handlers here
            # DEBUG("[CameraModule] Other callback: %d\n", nEvent)

    def getSingleCaptureImage(img, width, height, imageFormat):
        if not stillImageReady():
            return None
        __copyImage(stillData, img, stillWidth, stillHeight, width, height, imageFormat)
        return img

    def getStreamCaptureImage(uint8_t *img, width, height, imageFormat):
        if not liveImageReady()
            return None
        __copyImage(liveData, img, liveWidth, liveHeight, width, height, fmt);
        return img

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

            # if there's extra space on the right side of the destination, set its data to 0
            for x in range(minWidth, wd):
                for y in range(0, minHeight):
                    destData[3*(wd*y + x)] = 0
                    destData[3*(wd*y + x) + 1] = 0
                    destData[3*(wd*y + x) + 2] = 0

            # if there's extra space at the bottom of the destination, set its data to 0
            for y in range(minHeight, hd):
                for x in range(0, wd):
                    destData[3*(wd*y + x)] = 0
                    destData[3*(wd*y + x) + 1] = 0
                    destData[3*(wd*y + x) + 2] = 0



    # camera configuration functions
    @abstractmethod
    def getExposureTime():
        pass

    @abstractmethod
    def setExposureTime(micros):
        pass
    
    @abstractmethod
    def getAvailableResolutionModes():
        pass # returns list of ResolutionModes
    
    @abstractmethod
    def getResolutionMode():
        pass # returns current ResolutionMode

    @abstractmethod
    def setResolutionMode(mode):
        pass

    # camera description functions
    @abstractmethod
    def getDeviceVendor():
        return "AmScope"

    @abstractmethod
    def getDeviceName():
        return None
