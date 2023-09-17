# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 12:11:43 2023

@author: eliob
"""

import numpy as np
import cv2

img = cv2.imread('flat_field_crop.png')
height, width, n = img.shape


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


cv2.imshow('gray_positive', cv2.resize(gray,(500,283)))
# Find the maximum pixel value and its location
(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
# Calculate the scaling factor
scale = 255.0 / (maxVal- minVal)

# Scale the pixel intensities
adjusted_img = 255 - (gray - minVal)*scale

# Convert the pixel intensities to the uint8 data type
adjusted_img = adjusted_img.astype(np.uint8)
cv2.imshow('Adjusted Image, inverted', cv2.resize(adjusted_img,(500,283)))
img_alpha = cv2.cvtColor(adjusted_img, cv2.COLOR_GRAY2BGRA)
img_alpha[:,:,3] = np.zeros((height,width)) + 128 
cv2.imwrite('inverted_flat_field_6_17.png',img_alpha)
