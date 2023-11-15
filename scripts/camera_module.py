from abc import ABC, abstractmethod
from enum import Enum, auto

class CameraModule(ABC):
    class ImageFormat(Enum):
        RGB888 = auto()

    # describes combinations of resolutions and image formats the camera supports
    class ResolutionMode:
        width = 0
        height = 0
        supportedFormats = None

        def __str__(self):
            formatsString = ""
            for f in self.supportedFormats:
                formatsString += str(f) + ", "
            return f"({self.width}, {self.height}, [{formatsString[:-2]}])"

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
    def getExposureTime(self):
        pass

    @abstractmethod
    def setExposureTime(self, micros):
        pass
    
    @abstractmethod
    def getAvailableResolutionModes(self):
        pass # returns list of ResolutionModes
    
    @abstractmethod
    def getResolutionMode(self):
        pass # returns current ResolutionMode

    @abstractmethod
    def setResolutionMode(self, mode):
        pass

    # other settings...

    # camera interfacing functions
    @abstractmethod
    def liveImageReady(self): # returns bool
        pass

    @abstractmethod
    def stillImageReady(self): # returns bool
        pass
        
    @abstractmethod
    def isOpen(self): # returns bool
        pass

    @abstractmethod
    def open(self): # returns true on success
        pass
        
    @abstractmethod
    def close(self): # returns true on success
        pass

    @abstractmethod
    def singleCapture(self): # returns true on success
        pass

    @abstractmethod
    def streamCapture(self): # returns true on success
        pass

    # camera description functions
    @abstractmethod
    def getDeviceVendor(self):
        pass

    @abstractmethod
    def getDeviceName(self):
        pass

    @abstractmethod
    def getSingleCaptureImage(self, width, height, imageFormat):
        pass

    @abstractmethod
    def getStreamCaptureImage(self, width, height, imageFormat):
        pass
