import camera_module
from amscope_camera import AmscopeCamera

cameraModule = None

def callback(imageData, width, height, imageFormat):
    global cameraModule
    print(f"(w,y)=({width}, {height})")
    cameraModule.closeCamera()

cameraModule = AmscopeCamera()
cameraModule.openCamera()
cameraModule.setSingleCaptureCallback(callback)
