#include "config.hpp"

#include "AmScopeCamera.hpp"

#if defined(DEBUG_MODE_CAMERA)
    #define DEBUG(...) DEBUG_OUTPUT(__VA_ARGS__)
#else
    #define DEBUG(...)
#endif

void (*AmScopeCamera::singleCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);
void (*AmScopeCamera::streamCaptureCallback)(uint8_t *imgData, int width, int height, ImageFormat format);

const int AmScopeCamera::liveIndex = 1;
const int AmScopeCamera::stillIndex = 1;

HAmcam AmScopeCamera::cameraHandle;

int AmScopeCamera::liveWidth;
int AmScopeCamera::liveHeight;
void *AmScopeCamera::liveData;

int AmScopeCamera::stillWidth;
int AmScopeCamera::stillHeight;
void *AmScopeCamera::stillData;

bool AmScopeCamera::liveImageGood;
bool AmScopeCamera::stillImageGood;

AmScopeCamera::AmScopeCamera() {
    singleCaptureCallback = nullptr;
    streamCaptureCallback = nullptr;
    closeCamera(); //reset to known state
}

AmScopeCamera::~AmScopeCamera() {
    closeCamera(); //reset to known state
}

bool AmScopeCamera::liveImageReady() {
    return liveImageGood;
}

bool AmScopeCamera::stillImageReady() {
    return stillImageGood;
}

void AmScopeCamera::setSingleCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) {
    singleCaptureCallback = cb;
}

//set to null if no callback desired
void AmScopeCamera::setStreamCaptureCallback(void (*cb)(uint8_t *data, int w, int h, ImageFormat fmt)) {
    streamCaptureCallback = cb;
}

bool AmScopeCamera::isOpen() {
    return cameraHandle != NULL;
}

bool AmScopeCamera::openCamera() {
    HRESULT hr;

    if(isOpen()) {
        DEBUG("[CameraModule] Camera is already open\n");
        return true;
    }

    cameraHandle = Amcam_Open(NULL);

    if(cameraHandle == NULL) {
        DEBUG("[CameraModule] No camera found or open failed\n");
        return false;
    }

    hr = Amcam_put_eSize(cameraHandle, stillIndex);
    if(SUCCEEDED(hr))
        hr = Amcam_get_Size(cameraHandle, &stillWidth, &stillHeight);

    if (FAILED(hr)) {
        DEBUG("[CameraModule] Failed to set or get still size; hr = %d\n", hr);
        return false;
    }
    else {
        stillData = static_cast<void *>(new uint8_t[TDIBWIDTHBYTES(24 * stillWidth) * stillHeight]);
        if (NULL == stillData) {
            DEBUG("[CameraModule] Failed to allocate memory for still image data\n");
            return false;
        }
    }

    hr = Amcam_put_eSize(cameraHandle, liveIndex);
    if(SUCCEEDED(hr))
        hr = Amcam_get_Size(cameraHandle, &liveWidth, &liveHeight);

    if (FAILED(hr)) {
        DEBUG("[CameraModule] Failed to set or get live size; hr = %d\n", hr);
        return false;
    }
    else {
        liveData = static_cast<void *>(new uint8_t[TDIBWIDTHBYTES(24 * liveWidth) * liveHeight]);
        if (NULL == liveData) {
            DEBUG("[CameraModule] Failed to allocate memory for live image data\n");
            return false;
        }
    }

    DEBUG("[CameraModule] Camera opened: live resolution %dx%d, still resolution %dx%d\n", \
            liveWidth, liveHeight, stillWidth, stillHeight);
    return true;
}

void AmScopeCamera::closeCamera() {
    if(isOpen())
        Amcam_Close(cameraHandle);

    if(liveData)
        delete[] static_cast<uint8_t *>(liveData);

    if(stillData)
        delete[] static_cast<uint8_t *>(stillData);
    
    stillData = NULL;
    liveData = NULL;
    cameraHandle = NULL;
    liveImageGood = false;
    stillImageGood = false;

    DEBUG("[CameraModule] Camera closed\n");
}

bool AmScopeCamera::singleCapture() {
    HRESULT hr = Amcam_StartPullModeWithCallback(cameraHandle, amscopeCallback, NULL);
    hr = Amcam_Snap(cameraHandle, stillIndex);

    stillImageGood = false;

    if (FAILED(hr)) {
        DEBUG("[CameraModule] Failed to capture still image, hr = %d\n", hr);
        return false;
    }
    else {
        DEBUG("[CameraModule] Waiting for still image...\n");
        return true;
    }
}

bool AmScopeCamera::streamCapture() {
    HRESULT hr = Amcam_StartPullModeWithCallback(cameraHandle, amscopeCallback, NULL);

    liveImageGood = false;

    if (FAILED(hr)) {
        DEBUG("[CameraModule] Failed to capture live image, hr = %d\n", hr);
        return false;
    }
    else {
        DEBUG("[CameraModule] Waiting for live image...\n");
        return true;
    }
}

void AmScopeCamera::amscopeCallback(unsigned nEvent, void *pCallbackCtx) {
    HRESULT hr;
    AmcamFrameInfoV2 info = {};

    if (nEvent == AMCAM_EVENT_IMAGE) {
        liveImageGood = false;
        hr = Amcam_PullImageV2(cameraHandle, liveData, 24, &info);

        if (FAILED(hr)) {
            DEBUG("[CameraModule] Failed to pull image, hr = %d\n", hr);
        }
        else {
            DEBUG("[CameraModule] Live image captured.\n");
            liveImageGood = true;

            if(streamCaptureCallback)
                streamCaptureCallback(static_cast<uint8_t *>(liveData), liveWidth, liveHeight, RGB888); //modify later
        }
    }
    else if(nEvent == AMCAM_EVENT_STILLIMAGE) {
        stillImageGood = false;
        hr = Amcam_PullStillImageV2(cameraHandle, stillData, 24, &info);

        if (FAILED(hr)) {
            DEBUG("[CameraModule] Failed to pull image, hr = %d\n", hr);
        }
        else {
            DEBUG("[CameraModule] Still image captured.\n");
            stillImageGood = true;

            if(singleCaptureCallback)
                singleCaptureCallback(static_cast<uint8_t *>(stillData), stillWidth, stillHeight, RGB888); //modify later

            int count = 0;
            for(int i = 0; i < stillWidth * stillHeight; i++) {
                count += (((uint8_t *)stillData)[i] != 0);
            }

            DEBUG("count is %d\n", count);
        }
    }
    else { //for more robust operation, add more event handlers here
        DEBUG("[CameraModule] Other callback: %d\n", nEvent);
    }
}

uint8_t *AmScopeCamera::getSingleCaptureImage(uint8_t *img, int w, int h, ImageFormat fmt) {
    if(!stillImageReady())
        return nullptr;
    copyImage(static_cast<uint8_t *>(stillData), img, stillWidth, stillHeight, w, h, fmt);
    return img;
}

uint8_t *AmScopeCamera::getStreamCaptureImage(uint8_t *img, int w, int h, ImageFormat fmt) {
    if(!liveImageReady())
        return nullptr;
    copyImage(static_cast<uint8_t *>(liveData), img, liveWidth, liveHeight, w, h, fmt);
    return img;
}

void AmScopeCamera::copyImage(uint8_t *src, uint8_t *dest, int ws, int hs, int wd, int hd, ImageFormat fmt) {
    int minWidth = (ws < wd) ? ws : wd;
    int minHeight = (hs < hd) ? hs : hd;

    DEBUG("%d, %d\n", minWidth, minHeight);

    if(1) { //normally would check for format here; this assumes 24 bits per pixel
        //copy image data
        for(int y = 0; y < minHeight; y++) {
            for(int x = 0; x < minWidth; x++) {
                dest[3*(wd*y + x)] = src[3*(ws*y + x)];
                dest[3*(wd*y + x) + 1] = src[3*(ws*y + x) + 1];
                dest[3*(wd*y + x) + 2] = src[3*(ws*y + x) + 2];
            }
        }

        //if there's extra space on the right side of the destination, set its data to 0
        for(int x = minWidth; x < wd; x++) {
            for(int y = 0; y < minHeight; y++) {
                dest[3*(wd*y + x)] = 0;
                dest[3*(wd*y + x) + 1] = 0;
                dest[3*(wd*y + x) + 2] = 0;
            }
        }

        //if there's extra space at the bottom of the destination, set its data to 0
        for(int y = minHeight; y < hd; y++) {
            for(int x = 0; x < wd; x++) {
                dest[3*(wd*y + x)] = 0;
                dest[3*(wd*y + x) + 1] = 0;
                dest[3*(wd*y + x) + 2] = 0;
            }
        }
    }
}

#undef DEBUG
