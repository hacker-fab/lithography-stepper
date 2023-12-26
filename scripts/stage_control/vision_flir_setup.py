# echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb

# %%
import PySpin
import numpy as np

# %%
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
num_cameras = cam_list.GetSize()
print('Number of cameras detected: %d' % num_cameras)
cam = cam_list[0]
cam.Init()

# %%
# Retrieve TL device nodemap and print device information
nodemap_tldevice = cam.GetTLDeviceNodeMap()

# Initialize camera
cam.Init()
cam.PixelFormat.SetValue(PySpin.PixelFormat_BayerRG8)
cam.BinningHorizontal.SetValue(2)
cam.BinningVertical.SetValue(2)
print(cam.Width.GetAccessMode(), "==" ,PySpin.RW)
cam.Width.SetValue(cam.Width.GetMax())
cam.Height.SetValue(cam.Height.GetMax())
cam.AcquisitionFrameRateEnable.SetValue(True)
cam.AcquisitionFrameRate.SetValue(cam.AcquisitionFrameRate.GetMax())

# %%
nodemap = cam.GetNodeMap()
node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
cam.BeginAcquisition()
device_serial_number = ''
node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
if PySpin.IsReadable(node_device_serial_number):
    device_serial_number = node_device_serial_number.GetValue()
    print('Device serial number retrieved as %s...' % device_serial_number)
image_result = cam.GetNextImage(1000)
cam.EndAcquisition()
		
# %%
