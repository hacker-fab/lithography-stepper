import camera_module
from amscope_camera import AmscopeCamera

cameraModule = None

def callback(imageData, width, height, imageFormat):
    global cameraModule
    print(f"(w,y)=({width}, {height})")
    cameraModule.closeCamera()

def cvTest():
    pass

cameraModule = AmscopeCamera()
cameraModule.open()
cameraModule.setSingleCaptureCallback(callback)
cameraModule.close()
