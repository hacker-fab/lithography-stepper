# echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb

# %%
import PySpin
import numpy as np
processor = PySpin.ImageProcessor()
processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

# %%
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
num_cameras = cam_list.GetSize()
print('Number of cameras detected: %d' % num_cameras)
cam = cam_list[0]
cam.Init()
try:
    cam.BeginAcquisition()
except:
    pass

# %%
# Retrieve, convert, and save images
image_result = cam.GetNextImage(1000)
if image_result.IsIncomplete():
    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
else:
    width = image_result.GetWidth()
    height = image_result.GetHeight()
    # print('Grabbed Image, width = %d, height = %d' % (width, height))
    image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
    image_converted = image_converted.GetData()

print((width, height, np.array(image_converted).shape))


def get_img(buffer):
    global cam
    done = False
    while not done:
        image_result = cam.GetNextImage(1000)
        if image_result.IsIncomplete():
            print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
        else:
            width = image_result.GetWidth()
            height = image_result.GetHeight()
            # print('Grabbed Image, width = %d, height = %d' % (width, height))
            image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
            buffer[:, :] = np.reshape(image_converted.GetData(), (height, width)).T
            image_result.Release()
            done = True
    return 1

# import cv2
# img = np.zeros((width, height), dtype=np.uint8)
# while True:
#     get_img(img)
#     cv2.imshow('img', img[::4, ::4])
#     cv2.waitKey(1)