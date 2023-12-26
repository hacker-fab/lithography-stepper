# using Pkg
# ENV["PYTHON"] = abspath("venv/bin/python")
# Pkg.build("PyCall")
using PyCall
using Observables

# @pyinclude("vision_flir.py")
# liveimgsz = Int[2736, 1824]
@pyinclude("vision_v4l2.py")
liveimgsz = Int[2560, 1920]
@pyinclude("align.py")

py"""
import numpy as np
def preallocarr_live():
    return np.zeros($liveimgsz, dtype = np.uint8)
"""

liveimg = Observable(pycall(py"""preallocarr_live""", PyArray))
annoimg = Observable(pycall(py"""preallocarr_live""", PyArray))
mouseimg = Observable(pycall(py"""preallocarr_live""", PyArray))

visinit = true
function vislooponce(visionCh, refCh)
    global running, liveimg, visinit, shiftimgcrop, originxy
    py"""get_img($(liveimg[]))"""
    if visinit
        margin = 150
        cropx, cropy = size(liveimg[], 1)÷2-margin:size(liveimg[], 1)÷2+margin,
        size(liveimg[], 2)÷2-margin:size(liveimg[], 2)÷2+margin
        shiftx, shifty = cropx, cropy
        shiftimgcrop = liveimg[][cropx, cropy]
        originxy = [shiftx[1], shifty[1]]
        visinit = false
    end
    if isready(refCh)
        xoff, yoff = take!(refCh)

        # Visualization without margin
        margin = 0
        cropx, cropy = max(1 + margin, 1 - xoff):min(liveimgsz[1] - margin, liveimgsz[1] - xoff),
        max(1 + margin, 1 - yoff):min(liveimgsz[2] - margin, liveimgsz[2] - yoff)
        shiftx, shifty = max(1 + margin, 1 + xoff):min(liveimgsz[1] - margin, liveimgsz[1] + xoff),
        max(1 + margin, 1 + yoff):min(liveimgsz[2] - margin, liveimgsz[2] + yoff)

        mouseimg[] .= 0.0
        mouseimg[][shiftx, shifty] .= liveimg[][cropx, cropy]

        # Template Matching with margin
        margin = 500
        cropx, cropy = max(1 + margin, 1 - xoff):min(liveimgsz[1] - margin, liveimgsz[1] - xoff),
        max(1 + margin, 1 - yoff):min(liveimgsz[2] - margin, liveimgsz[2] - yoff)
        shiftx, shifty = max(1 + margin, 1 + xoff):min(liveimgsz[1] - margin, liveimgsz[1] + xoff),
        max(1 + margin, 1 + yoff):min(liveimgsz[2] - margin, liveimgsz[2] + yoff)

        shiftimgcrop = liveimg[][cropx, cropy]
        originxy = [shiftx[1], shifty[1]]
    end
    dxy = py"""align($(liveimg[]), $(shiftimgcrop), $(annoimg[]))"""

    # x y flipped due to row/column major between julia and python
    put!(visionCh, [Int64(time_ns()), Int64.([originxy[1] - dxy[1], originxy[2] - dxy[2]])..., Int64(0)])
end

# Threads.@spawn visloop(visionCh, refCh)
# running = false
# # GC.enable(false)
# shiftxy = [0, 0]
# shiftimgcrop = liveimg[][1:10, 1:20]
# py"""align($(liveimg[]), $shiftimgcrop, $shiftxy, $(annoimg[]))"""

# # annoimg[][1:10, 1:10]

# # visloop(visionCh, refCh)

# dxy = py"""align($(liveimg[]), $shiftimgcrop, $shiftxy, $(annoimg[]))"""
