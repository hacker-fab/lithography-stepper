#ifndef CAMERAMODULE_HPP
#define CAMERAMODULE_HPP

#include "amcam.h"
#include <cstdint>

//CameraModule is an abstract class; subclasses are implementations or specific camera models
class CameraModule {
    public:
        //camera configuration parameters/info
        enum ImageFormat {RGB888};
        //enum ImageResolution;

        virtual ~CameraModule() = 0;

        //camera configuration functions
        //setExposureTime(int millis)
        //setResolution(int mode)
        //int mode getResolution
        //other settings

        //camera interfacing functions
        virtual bool liveImageReady() = 0;
        virtual bool stillImageReady() = 0;
        virtual bool isOpen() = 0;
        virtual bool openCamera() = 0;
        virtual void closeCamera() = 0;
        virtual bool singleCapture() = 0;
        virtual bool streamCapture() = 0;

        //camera description functions
        //getVendor()
        //getDescription
        //etc.

        //callbacks will pass pointer to image as an argument, but the callback must make a copy of the data it wants to retain
        //(i.e. image data at pointer WILL change)

        //set to null if no callback desired
        virtual void setSingleCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt));

        //set to null if no callback desired
        virtual void setStreamCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt));

        //performs a deep copy of the image into the target array imgData.
        //if either of the camera image's dimensions is smaller than the specified dimension, the remaining space 
        //in the target buffer for that dimension is is set to 0. If either of the camera's image dimensions is
        //larger than the specified dimension, that part of the image is clipped, i.e. not copied to the target array. 
        virtual uint8_t *getSingleCaptureImage(uint8_t *imgData, int width, int height, ImageFormat fmt) = 0; //returns a deep copy of the image
        virtual uint8_t *getStreamCaptureImage(uint8_t *imgData, int width, int height, ImageFormat fmt) = 0; //returns a deep copy of the image

        //getStatus()
    protected:
        void (*singleCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);
        void (*streamCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);
};

#endif // CAMERAMODULE_HPP
