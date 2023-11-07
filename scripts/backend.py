import camera_module
import amscope_camera

cameraModule = None

def callback(imageData, width, height, imageFormat):
    global cameraModule
    print(f"(w,y)=({width}, {height})")
    cameraModule.closeCamera()

cameraModule = AmscopeCamera()
cameraModule.openCamera()
cameraModule.setSingleCaptureCallback(callback)
