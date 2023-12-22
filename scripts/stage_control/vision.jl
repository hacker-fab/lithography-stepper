# using Pkg
# ENV["PYTHON"] = abspath("venv/bin/python")
# Pkg.build("PyCall")
using PyCall

@pyinclude("vision_v4l2.py")

imgsz = Int[2560 / 4, 1920 / 4]
refimgsz = Int[2560, 1920]

py"""
import numpy as np
def preallocarr_live():
    return np.zeros($imgsz, dtype = np.uint8)
def preallocarr_ref():
    return np.zeros($refimgsz, dtype = np.uint8)
"""

liveimg = Observable(pycall(py"""preallocarr_live""", PyArray))
refimg = Observable(pycall(py"""preallocarr_ref""", PyArray))
liverefimg = Observable(pycall(py"""preallocarr_ref""", PyArray))