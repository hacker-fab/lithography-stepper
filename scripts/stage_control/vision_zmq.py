# sudo modprobe v4l2loopback
# scrcpy --v4l2-sink=/dev/video4 --no-video-playback --video-source=camera --camera-size=2560x1920  --camera-facing=front
import cv2
import numpy as np
import sys
import zmq

cv2.ocl.setUseOpenCL(False)
# # %% OpenCV
# try:
# 	# Returns True if OpenCL is present
# 	ocl = cv2.ocl.haveOpenCL()
# 	# Prints whether OpenCL is present
# 	print("OpenCL Supported?: ", end='')
# 	print(ocl)
# 	print()
# 	# Enables use of OpenCL by OpenCV if present
# 	if ocl == True:
# 		print('Now enabling OpenCL support')
# 		cv2.ocl.setUseOpenCL(True)
# 		print("Has OpenCL been Enabled?: ", end='')
# 		print(cv2.ocl.useOpenCL())
# except cv2.error as e:
# 	print('Error using OpenCL')


# ZMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:%s" % 5556)
socket.subscribe("")


def get_img():
	global socket
	im = socket.recv()
	return True, np.frombuffer(im, dtype=np.uint8).reshape((1824, 2736))[470:-470:, 470:-470:]

# while True:
# 	_, im = get_img()

# 	cv2.imshow('preview', im[470:-470:4, 470:-470:4])
# 	cv2.waitKey(1)

# Set Reference Image
imgdata = {
	"refimg": None,
	"liveimg": None,
	"refcrop": None,
}
def set_ref(cropidx):
	global imgdata
	liveimg_ = cv2.UMat.get(imgdata["liveimg"])
	imgdata["refcrop"] = [
		(cropidx[0] - 1), (cropidx[1]), (cropidx[2] - 1), (cropidx[3]),
		(cropidx[4] - 1), (cropidx[5] - 1)]
	imgdata["refimg"] = cv2.UMat(liveimg_[
		imgdata["refcrop"][0]:imgdata["refcrop"][1], 
		imgdata["refcrop"][2]:imgdata["refcrop"][3]])
	return liveimg_

# Perform Alignment
def align_next():
	global imgdata, camera
	retval, im = get_img()
	img = cv2.rotate(cv2.UMat(im), cv2.ROTATE_90_CLOCKWISE)
	
	liveimg = img
	imgdata["liveimg"] = liveimg
	if imgdata["refimg"] is None:
		imgdata["refimg"] = liveimg
		imgdata["refcrop"] = [0, im.shape[1], 0, im.shape[0], 0, 0]

	h, w = (imgdata["refcrop"][1] - imgdata["refcrop"][0]), (imgdata["refcrop"][3] - imgdata["refcrop"][2])
	res = cv2.matchTemplate(imgdata["refimg"], liveimg, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

	# cv2.imshow('preview', cv2.UMat.get(imgdata["refimg"])[::4, ::4])
	# cv2.waitKey(1)

	top_left = max_loc
	bottom_right = (top_left[0] + w, top_left[1] + h)
	dx, dy = (imgdata["refcrop"][4] - top_left[0], imgdata["refcrop"][5] - top_left[1])

	liveimg_ = cv2.UMat.get(liveimg)
	cv2.rectangle(liveimg_,top_left, bottom_right, 255, 5)
	return (dx, dy), liveimg_