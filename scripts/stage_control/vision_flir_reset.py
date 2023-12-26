# %%
import PySpin
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
num_cameras = cam_list.GetSize()
print('Number of cameras rebooted: %d' % num_cameras)
cam = cam_list[0]

# %%
cam.Init()
cam.DeviceReset.Execute()
# %%
