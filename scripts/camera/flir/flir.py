# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2023 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# Acquisition.py shows how to acquire images. It relies on
# information provided in the Enumeration example. Also, check out the
# ExceptionHandling and NodeMapInfo examples if you haven't already.
# ExceptionHandling shows the handling of standard and Spinnaker exceptions
# while NodeMapInfo explores retrieving information from various node types.
#
# This example touches on the preparation and cleanup of a camera just before
# and just after the acquisition of images. Image retrieval and conversion,
# grabbing image data, and saving images are all covered as well.
#
# Once comfortable with Acquisition, we suggest checking out
# AcquisitionMultipleCamera, NodeMapCallback, or SaveToAvi.
# AcquisitionMultipleCamera demonstrates simultaneously acquiring images from
# a number of cameras, NodeMapCallback serves as a good introduction to
# programming with callbacks and events, and SaveToAvi exhibits video creation.
#
# Please leave us feedback at: https://www.surveymonkey.com/r/TDYMVAPI
# More source code examples at: https://github.com/Teledyne-MV/Spinnaker-Examples
# Need help? Check out our forum at: https://teledynevisionsolutions.zendesk.com/hc/en-us/community/topics

import os
import PySpin
import sys
import zmq
import time

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)



NUM_IMAGES = 100000  # number of images to grab


def acquire_images(cam, nodemap, nodemap_tldevice):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        # Set acquisition mode to continuous
        #
        #  *** NOTES ***
        #  Because the example acquires and saves 10 images, setting acquisition
        #  mode to continuous lets the example finish. If set to single frame
        #  or multiframe (at a lower number of images), the example would just
        #  hang. This would happen because the example has been written to
        #  acquire 10 images while the camera would have been programmed to
        #  retrieve less than that.
        #
        #  Setting the value of an enumeration node is slightly more complicated
        #  than other node types. Two nodes must be retrieved: first, the
        #  enumeration node is retrieved from the nodemap; and second, the entry
        #  node is retrieved from the enumeration node. The integer value of the
        #  entry node is then set as the new value of the enumeration node.
        #
        #  Notice that both the enumeration and the entry nodes are checked for
        #  availability and readability/writability. Enumeration nodes are
        #  generally readable and writable whereas their entry nodes are only
        #  ever readable.
        #
        #  Retrieve enumeration node from nodemap

        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        #
        #  *** NOTES ***
        #  What happens when the camera begins acquiring images depends on the
        #  acquisition mode. Single frame captures only a single image, multi
        #  frame catures a set number of images, and continuous captures a
        #  continuous stream of images. Because the example calls for the
        #  retrieval of 10 images, continuous mode has been set.
        #
        #  *** LATER ***
        #  Image acquisition must be ended when no more images are needed.
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Retrieve, convert, and save images

        # Create ImageProcessor instance for post processing images
        processor = PySpin.ImageProcessor()

        # Set default image processor color processing method
        #
        # *** NOTES ***
        # By default, if no specific color processing algorithm is set, the image
        # processor will default to NEAREST_NEIGHBOR method.
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

        start_t = time.time()
        while True:
#            print("FPS: ", 1/(time.time() - start_t))
            start_t = time.time()
            try:
                image_result = cam.GetNextImage(1000)
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                else:
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    # print('Grabbed Image, width = %d, height = %d' % (width, height))
                    image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)

                    socket.send(image_converted.GetData(), zmq.NOBLOCK)

                    # # Create a unique filename
                    if device_serial_number:
                        filename = 'Acquisition-%s.jpg' % (device_serial_number)
                    else:  # if serial number is empty
                        filename = 'Acquisition.jpg'

                    # image_converted.Save(filename)
                    # print('Image saved at %s' % filename)

                    image_result.Release()

            except KeyboardInterrupt:
                return True
            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not readable.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def configure_custom_image_settings(cam):
    """
    Configures a number of settings on the camera including offsets X and Y,
    width, height, and pixel format. These settings must be applied before
    BeginAcquisition() is called; otherwise, those nodes would be read only.
    Also, it is important to note that settings are applied immediately.
    This means if you plan to reduce the width and move the x offset accordingly,
    you need to apply such changes in the appropriate order.

    :param cam: Camera to configure settings on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print('\n*** CONFIGURING CUSTOM IMAGE SETTINGS ***\n')

    try:
        result = True

        # Apply pixel format
        #
        # *** NOTES ***
        # In QuickSpin, enumeration nodes are as easy to set as other node
        # types. This is because enum values representing each entry node
        # are added to the API.
        if cam.PixelFormat.GetAccessMode() == PySpin.RW:
            cam.PixelFormat.SetValue(PySpin.PixelFormat_BayerRG8)
            print('Pixel format set to %s...' % cam.PixelFormat.GetCurrentEntry().GetSymbolic())

        else:
            print('Pixel format not available...')
            result = False

        if cam.BinningHorizontal.GetAccessMode() == PySpin.RW:
            cam.BinningHorizontal.SetValue(2)
            print('BinningHorizontal set to %s...' % cam.BinningHorizontal.GetValue())

        else:
            print('Pixel format not available...')
            result = False

        if cam.BinningVertical.GetAccessMode() == PySpin.RW:
            cam.BinningVertical.SetValue(2)
            print('BinningVertical set to %s...' % cam.BinningVertical.GetValue())
        else:
            print('Pixel format not available...')
            result = False

        # Set maximum width
        #
        # *** NOTES ***
        # Other nodes, such as those corresponding to image width and height,
        # might have an increment other than 1. In these cases, it can be
        # important to check that the desired value is a multiple of the
        # increment.
        #
        # This is often the case for width and height nodes. However, because
        # these nodes are being set to their maximums, there is no real reason
        # to check against the increment.
        print(cam.Width.GetAccessMode(), "==" ,PySpin.RW)
        if cam.Width.GetAccessMode() == PySpin.RW and cam.Width.GetInc() != 0 and cam.Width.GetMax != 0:
            cam.Width.SetValue(cam.Width.GetMax())
            print('Width set to %i...' % cam.Width.GetValue())

        else:
            print('Width not available...')
            result = False

        # Set maximum height
        #
        # *** NOTES ***
        # A maximum is retrieved with the method GetMax(). A node's minimum and
        # maximum should always be a multiple of its increment.
        if cam.Height.GetAccessMode() == PySpin.RW and cam.Height.GetInc() != 0 and cam.Height.GetMax != 0:
            cam.Height.SetValue(cam.Height.GetMax())
            print('Height set to %i...' % cam.Height.GetValue())

        else:
            print('Height not available...')
            result = False


        # Set AcquisitionFrameRateEnable
        if cam.AcquisitionFrameRateEnable.GetAccessMode() == PySpin.RW:
            cam.AcquisitionFrameRateEnable.SetValue(True)
            print('AcquisitionFrameRateEnable set to %s...' % cam.AcquisitionFrameRateEnable.GetValue())
        else:
            print('AcquisitionFrameRateEnable not available...')
            result = False

        # Set AcquisitionFrameRate
        if cam.AcquisitionFrameRate.GetAccessMode() == PySpin.RW:
            cam.AcquisitionFrameRate.SetValue(cam.AcquisitionFrameRate.GetMax())
            print('AcquisitionFrameRate set to %s...' % cam.AcquisitionFrameRate.GetValue())
        else:
            print('AcquisitionFrameRate not available...')
            result = False

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)
        
        # Initialize camera
        cam.Init()

        # cam.DeviceReset.Execute()

        # Configure
        if not configure_custom_image_settings(cam):
            cam.DeviceReset.Execute()
            return False
        
        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()
        cam.DeviceReset.Execute()
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
