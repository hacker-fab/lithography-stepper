#include "config.hpp"

#include "ControlInterface.hpp"
#include "cameramodule.hpp"
#include "AmScopeCamera.hpp"

//for testing purposes
#include <iostream>
#include <fstream>

AmScopeCamera amscopeCamera;
CameraModule *camera;
uint8_t *cameraData;

void callback(uint8_t *img, int width, int height, CameraModule::ImageFormat fmt) {
    for(int y = 0; y < height; y++) {
        for(int x = 0; x < width; x++) {
            cameraData[3*(y*width+x)] = img[3*(width*y+x)];
            cameraData[3*(y*width+x)+1] = img[3*(width*y+x)+1];
            cameraData[3*(y*width+x)+2] = img[3*(width*y+x)+2];
        }
    }

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

    int count = 0;
    for(int i = 0; i < 3 * width * height; i++) {
        count += (cameraData[i] != 0);
        bmpData[56+i] = cameraData[i];
    }
    std::cout << "count in main is " << count << std::endl;

    bitmap.write(bmpData, 14 + 40 + 2 + 3*width*height);
    bitmap.close();

    delete[] bmpData;
}

void testCamera() {
    //camera test for V2
    camera = &amscopeCamera;
    camera->setSingleCaptureCallback(callback);

    if(camera->isOpen()) {
        camera->closeCamera();
    }

    if(camera->openCamera()) {
        camera->singleCapture();
    }

    //camera->getSingleCaptureImage(cameraData, 6000, 4000, AmScopeCamera::RGB888);
}

int main(int argc, char *argv[])
{
    //V2 Camera test code
    cameraData = new uint8_t[6000*4000*3];

    ControlInterface gui;

    std::cout << "If this message is already showing with the GUI open, then we're good. "
                 "Otherwise, we should open the GUI in a separate thread and do some "
                 "inter-process communication." << std::endl;

    return EXIT_SUCCESS;
}
