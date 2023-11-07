from abc import ABC, abstractmethod
from enum import Enum, auto

class CameraModule(ABC):
    class ImageFormat(Enum):
        RGB888 = auto()

    class ResolutionMode:
        width = 0
        height = 0

    class CameraImage:
        imageformat = ImageFormat()

    singleCaptureCallback = None
    streamCaptureCallback = None

    # set to None if no callback desired
    @abstractmethod
    def setSingleCaptureCallback(self, callback):
        singleCaptureCallback = callback

    # set to None if no callback desired
    @abstractmethod
    def setStreamCaptureCallback(self, callback):
        streamCaptureCallback = callback

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

    # other settings...

    # camera interfacing functions
    @abstractmethod
    def liveImageReady(): # returns bool
        pass

    @abstractmethod
    def stillImageReady(): # returns bool
        pass
        
    @abstractmethod
    def isOpen(): # returns bool
        pass

    @abstractmethod
    def openCamera(): # returns true on success
        pass
        
    @abstractmethod
    def closeCamera(): # returns true on success
        pass

    @abstractmethod
    def singleCapture(): # returns true on success
        pass

    @abstractmethod
    def streamCapture(): # returns true on success
        pass

    # camera description functions
    @abstractmethod
    def getDeviceVendor():
        pass

    @abstractmethod
    def getDeviceName():
        pass

    @abstractmethod
    def getSingleCaptureImage(int width, int height, ImageFormat fmt):
        pass

    @abstractmethod
    def getStreamCaptureImage(int width, int height, ImageFormat fmt):
        pass
