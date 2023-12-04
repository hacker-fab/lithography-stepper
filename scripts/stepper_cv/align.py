#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 19:26:39 2023

@author: frankzhao
"""
import time
import numpy as np
import cv2

#Threshold for matching
MIN_MATCH_COUNT = 10

sift=cv2.SIFT_create()

def find_displacement(ref,input_frame,scale_factor=0.25,MIN_MATCH_COUNT=10,old=False,draw=False,printout=False):
    #start_time=time.time()
    img1 = ref
    img1 = cv2.resize(img1, None, fx=scale_factor, fy=scale_factor)
    img2 = input_frame
    #Resize image2 to match the size of image1, for test only, no need to have this in real application
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    start_time=time.time()
    #Initiate SIFT detector, use xfeatures2d lib only for lower version of openCV
    #sift = cv2.xfeatures2d.SIFT_create()
    #sift=cv2.SIFT_create()
    #find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    #Create FLANN Match
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    #Store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
       if m.distance < 0.7*n.distance:
           good.append(m)
#        good.append(m)

    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #print(src_pts[1])
        #print("\n----\n")
        #print(dst_pts[1])
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h,w = img1.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2) #top-left, bottom-left, bottom-right, top-right; 4 corner points at img1
        dst = cv2.perspectiveTransform(pts,M)                                  #Transform to img2 use M
#       if draw == True:
#            img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)      #Draw White rectangle dst on img2
#       img2 = cv2.polylines(img2,[np.int32(dst)],True,  0,3, cv2.LINE_AA)      #Draw Black rectangle dst on img2

        if old:
            # Extract the translation
            dx = M[0, 2]
            dy = M[1, 2]
        else:# New method
            # dx,dy is x,y offset between center of rectangle dst and center of img2
            rect_dst=np.int32(dst)
            h2,w2=img2.shape
            dx = w2//2 - (rect_dst[0][0][0]+rect_dst[2][0][0])//2
            dy = h2//2 - (rect_dst[0][0][1]+rect_dst[2][0][1])//2
        theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi
        elapsed_time=time.time()-start_time
        if printout == True:
            print(f"Time taken to process image {tests[t]}: {elapsed_time:.2f} seconds")
            print(f"Displacement (dx, dy): ({dx}, {dy})")
            print(f"Rotation angle (theta): {theta} degrees")
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        matchesMask = None
        return None

    if draw==True:
        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                           singlePointColor = None,
                           matchesMask = matchesMask, # draw only inliers
                           flags = 2)
        img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
        
        # Iterate through each good match to draw the coordinates
        for i, match in enumerate(good):
            if matchesMask[i]:  # Check if this match is to be drawn
                # Coordinates in img1
                x1, y1 = kp1[match.queryIdx].pt
                cv2.putText(img3, f"({int(x1)}, {int(y1)})", (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
                # Coordinates in img2 - adjust x coordinate for the width of the first image
                x2, y2 = kp2[match.trainIdx].pt
                #x2 += img1.shape[1]  # Adjustment for the combined image
                cv2.putText(img3, f"({int(x2)}, {int(y2)})", (int(x2+img1.shape[1]), int(y2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        cv2.namedWindow('image')
        cv2.imshow('image',img3)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    ret=(dx/scale_factor,dy/scale_factor,theta)
    return ret


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
