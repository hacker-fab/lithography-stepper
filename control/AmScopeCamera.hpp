#ifndef AMSCOPECAMERA_HPP
#define AMSCOPECAMERA_HPP

#include "config.hpp"

#include "cameramodule.hpp"

class AmScopeCamera : public CameraModule {
    public:
        AmScopeCamera();
        ~AmScopeCamera() override;

        //camera configuration functions
        //setExposureTime(int millis)
        //setResolution(int mode)
        //int mode getResolution
        //other settings

        //camera interfacing functions
        bool liveImageReady() override;
        bool stillImageReady() override;
        bool isOpen() override;
        bool openCamera() override;
        void closeCamera() override;
        bool singleCapture() override;
        bool streamCapture() override;

        //camera description functions
        //getVendor()
        //getDescription
        //etc.

        //performs a deep copy of the image into the target array imgData.
        //if either of the camera image's dimensions is smaller than the specified dimension, the remaining space
        //in the target buffer for that dimension is is set to 0. If either of the camera's image dimensions is
        //larger than the specified dimension, that part of the image is clipped, i.e. not copied to the target array.
        uint8_t *getSingleCaptureImage(uint8_t *imgData, int width, int height, ImageFormat fmt) override; //returns a deep copy of the image
        uint8_t *getStreamCaptureImage(uint8_t *imgData, int width, int height, ImageFormat fmt) override; //returns a deep copy of the image

        //set to null if no callback desired
        void setSingleCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) override;

        //set to null if no callback desired
        void setStreamCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) override;


    private:
        static void (*singleCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);
        static void (*streamCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);

        static const int liveIndex;
        static const int stillIndex;

        static HAmcam cameraHandle;

        static int liveWidth;
        static int liveHeight;
        static void *liveData;

        static int stillWidth;
        static int stillHeight;
        static void *stillData;

        static bool liveImageGood;
        static bool stillImageGood;

        static void __stdcall amscopeCallback(unsigned nEvent, void* pCallbackCtx);

        static void clearData();
        static void copyImage(uint8_t *src, uint8_t *dest, int ws, int hs, int wd, int hd, ImageFormat fmt);
};

#endif
