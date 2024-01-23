import cv2
import numpy as np

# %% OpenCV
try:
	# Returns True if OpenCL is present
	ocl = cv2.ocl.haveOpenCL()
	# Prints whether OpenCL is present
	print("OpenCL Supported?: ", end='')
	print(ocl)
	print()
	# Enables use of OpenCL by OpenCV if present
	if ocl == True:
		print('Now enabling OpenCL support')
		cv2.ocl.setUseOpenCL(True)
		print("Has OpenCL been Enabled?: ", end='')
		print(cv2.ocl.useOpenCL())
except cv2.error as e:
	print('Error using OpenCL')

# Perform Alignment
def align(livimg, refimg, annoimg):
	liveimg_U = cv2.UMat(livimg)

	h, w = refimg.shape
	res = cv2.matchTemplate(refimg, liveimg_U, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	
	top_left = max_loc
	bottom_right = (top_left[0] + w, top_left[1] + h)
	dx, dy = (top_left[0], top_left[1])

	annoimg[:, :] = livimg
	cv2.rectangle(annoimg[:, :],top_left, bottom_right, 255, 5)
	return [dy, dx]