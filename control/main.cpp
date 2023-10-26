#include "config.hpp"

//#include "ControlInterface.hpp"
#include "cameramodule.hpp"
#include "AmScopeCamera.hpp"

//for testing purposes
#include <iostream>
#include <fstream>
//cross-platform implementation
#ifdef _WIN32
#include <Windows.h>
//TODO: #include windows pthread implementation
#define SLEEP(x) Sleep(x)
#else
#include <pthread.h>
#include <unistd.h>
//#define SLEEP(x) do { struct timespec t; t.tv_sec = x / 1000; t.tv_nsec = x % 1000 * 1000000; nanosleep(&t, NULL); } while(0);
#define SLEEP(x) sleep(1)
#endif

//global variables
const int NUM_BUFFERS = 2;

struct DataFormat {
    uint32_t version;
    uint32_t cameraLiveWidth;
    uint32_t cameraLiveHeight;
    uint8_t *cameraLiveData;
    uint32_t cameraStillWidth;
    uint32_t cameraStillHeight;
    uint8_t *cameraStillData;
    float stageX;
    float stageY;
    float stageZ;
    float stageTheta;
} dataBuffers[NUM_BUFFERS];

int selectedBuffer;

AmScopeCamera amscopeCamera;
CameraModule *camera;
uint8_t *cameraLiveData;
uint8_t *cameraStillData;

void (*dataCallback)(char *data);
bool shouldExit;
int pthreadReturn;

//external functions

extern "C" void setDataCallback(void (*callback)(char *data)) {
    dataCallback = callback;
}

extern "C" void exitCpp() {
    shouldExit = true;
}

//internal functions

void initializeBuffer(int index) {
    dataBuffers[index].version = 1;
    dataBuffers[index].cameraLiveWidth = 0;
    dataBuffers[index].cameraLiveHeight = 0;
    dataBuffers[index].cameraLiveData = nullptr;
    dataBuffers[index].cameraStillWidth = 0;
    dataBuffers[index].cameraStillHeight = 0;
    dataBuffers[index].cameraStillData = nullptr;
    dataBuffers[index].stageX = 0.0f;
    dataBuffers[index].stageY = 0.0f;
    dataBuffers[index].stageZ = 0.0f;
    dataBuffers[index].stageTheta = 0.0f; 
}

void writeBitmapFile(uint8_t *img, int width, int height) {
    std::ofstream bitmap("/home/pi/camera-out.bmp", std::ios::out | std::ios::binary);

    //file header (see https://en.wikipedia.org/wiki/BMP_file_format, accessed 3 Oct 2023)
    char *bmpData = new char[14 + 40 + 2 + 3*width*height];
    bmpData[0] = 'B';
    bmpData[1] = 'M';
    *((int *)&bmpData[2]) = 14 + 40 + 3*width*height; //file size
    *((int *)&bmpData[6]) = 0; //reserved
    *((int *)&bmpData[10]) = 14 + 40 + 2; //offset of data
    *((int *)&bmpData[14]) = 40; //size of DIB header
    *((int *)&bmpData[18]) = width; //width
    *((int *)&bmpData[22]) = height; //height
    *((short *)&bmpData[26]) = 1; //number of color planes
    *((short *)&bmpData[28]) = 24; //bits per pixel
    *((int *)&bmpData[30]) = 0;
    *((int *)&bmpData[34]) = 0;
    *((int *)&bmpData[38]) = 0;
    *((int *)&bmpData[42]) = 0;
    *((int *)&bmpData[46]) = 0;
    *((int *)&bmpData[50]) = 0;
    *((short *)&bmpData[54]) = 0; //padding

    for(int i = 0; i < 3 * width * height; i++) {
        bmpData[56+i] = img[i];
    }

    bitmap.write(bmpData, 14 + 40 + 2 + 3*width*height);
    bitmap.close();

    delete[] bmpData;
}

void stillImageCallback(uint8_t *img, int width, int height, CameraModule::ImageFormat fmt) {
    //use a mutex?
    for(int y = 0; y < height; y++) {
        for(int x = 0; x < width; x++) {
            cameraStillData[3*(y*width+x)] = img[3*(width*y+x)];
            cameraStillData[3*(y*width+x)+1] = img[3*(width*y+x)+1];
            cameraStillData[3*(y*width+x)+2] = img[3*(width*y+x)+2];
        }
    }

    //place this here for now; later add functions to cameramodule:
    dataBuffers[selectedBuffer].cameraStillWidth = width;
    dataBuffers[selectedBuffer].cameraStillHeight = height;

    //writeBitmapFile(cameraData, width, height);
}

void testCamera() {
    //camera test for V2
    camera = &amscopeCamera;
    camera->setSingleCaptureCallback(stillImageCallback);

    if(camera->isOpen()) {
        camera->closeCamera();
    }

    if(camera->openCamera()) {
        camera->singleCapture();
    }
}

void swapBuffer() {
    //select next buffer
    selectedBuffer++;
    selectedBuffer %= NUM_BUFFERS;

    //swap all pointers
    cameraLiveData = dataBuffers[selectedBuffer].cameraLiveData;
    cameraStillData = dataBuffers[selectedBuffer].cameraStillData;
}

void updateData() {
    if(dataCallback) {
        //get most recent data

        //use a mutex?
        dataCallback(reinterpret_cast<char *>(&dataBuffers[selectedBuffer]));
        swapBuffer();
    }
}

void *poll(void *data) {
    while(!shouldExit) {
        SLEEP(1);
        updateData();
    }

    //exit
    pthreadReturn = 0;
    shouldExit = false;
    pthread_exit(&pthreadReturn);
}

//entry point; also external

/*
int main(int argc, char *argv[]) {
    //thread and data communication variables
    pthread_t threadId;
    shouldExit = false;
    dataCallback = nullptr;

    std::cout << "TEST0" << std::endl;
    SLEEP(1000);

    cameraLiveData = new uint8_t[3*3500*2500]; //TODO: proper size initialization
    cameraStillData = new uint8_t[3*4500*3500]; //TODO: proper size initialization

    for(int i = 0; i < NUM_BUFFERS; i++) {
        initializeBuffer(i);
    }
    swapBuffer();

    std::cout << "TEST1" << std::endl;
    SLEEP(1000);

    testCamera();
    std::cout << "TEST2" << std::endl;
    SLEEP(1000);

    pthread_create(&threadId, nullptr, poll, nullptr);
    std::cout << "TEST3" << std::endl;
    SLEEP(1000);

    while(!shouldExit) {
        //TODO: command polling
        //test:
        camera->singleCapture();
        SLEEP(500); //do this every half second
    }

    delete[] cameraLiveData;
    delete[] cameraStillData;
    return 0;
}
*/

int main() {
    return 0;
}