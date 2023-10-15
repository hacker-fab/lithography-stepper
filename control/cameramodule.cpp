#include "config.hpp"

#include "cameramodule.hpp"

#if defined(DEBUG_MODE_CAMERA)
    #define DEBUG(...) DEBUG_OUTPUT(__VA_ARGS__)
#else
    #define DEBUG(...)
#endif

CameraModule::~CameraModule() {}

void CameraModule::setSingleCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) {
    singleCaptureCallback = cb;
}

//set to null if no callback desired
void CameraModule::setStreamCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) {
    streamCaptureCallback = cb;
}

#undef DEBUG
