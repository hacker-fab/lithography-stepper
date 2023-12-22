# using Pkg
# ENV["PYTHON"] = abspath("venv/bin/python")
# Pkg.build("PyCall")
using PyCall
using GLMakie
GLMakie.activate!()

@pyinclude("vision_v4l2.py")

imgsz = Int[1920 / 4, 2560 / 4]
refimgsz = Int[1920, 2560]

py"""
import numpy as np
def preallocarr_live():
    return np.zeros($imgsz, dtype = np.uint8)
def preallocarr_ref():
    return np.zeros($refimgsz, dtype = np.uint8)
"""
f = Figure()
liveimg = Observable(pycall(py"""preallocarr_live""", PyArray))
ax1 = Axis(f[1, 1], aspect=DataAspect())
deregister_interaction!(ax1, :rectanglezoom)
image!(ax1, liveimg)

refimg = Observable(pycall(py"""preallocarr_ref""", PyArray))
liverefimg = Observable(pycall(py"""preallocarr_ref""", PyArray))
ax2 = Axis(f[1, 2], aspect=DataAspect())
deregister_interaction!(ax2, :rectanglezoom)
image!(ax2, liverefimg)
display(f)



mouseinit = true
updateref = false
start_position = Float64[0, 0]
cropidx = Int[1, refimgsz[1], 1, refimgsz[2], 0, 0]
register_interaction!(ax2, :my_interaction) do event::Makie.MouseEvent, axis
    global mouseinit
    global start_position
    global refimgsz
    global refimg
    global liverefimg
    global cropidx
    global updateref

    if event.type === Makie.MouseEventTypes.leftclick && !mouseinit
        # deregister_interaction!(ax1, :my_interaction)
        # println("Left click, deregistering interaction")
        mouseinit = true
        return
    end
    if (event.type === Makie.MouseEventTypes.leftclick && mouseinit)
        mouseinit = false
        start_position[1] = event.data[1]
        start_position[2] = event.data[2]
        return
    else
        if mouseinit
            return
        end
        xoff, yoff = round(Int, event.data[1] - start_position[1]), round(Int, event.data[2] - start_position[2])
        cropx, cropy   = max(1, 1-xoff):min(refimgsz[1], refimgsz[1] - xoff), max(1, 1-yoff):min(refimgsz[2], refimgsz[2] - yoff)
        shiftx, shifty = max(1, 1 + xoff):min(refimgsz[1], refimgsz[1] + xoff), max(1, 1 + yoff):min(refimgsz[2], refimgsz[2] + yoff)
        cropidx = [cropx[1], cropx[end], cropy[1], cropy[end], shiftx[1], shifty[1]]
        shiftimgcrop = refimg[][cropx, cropy]
        liverefimg[] .= 0.0
        liverefimg[][shiftx, shifty] .= shiftimgcrop
        notify(liverefimg)
        updateref = true
    end
    return
end

# deregister_interaction!(ax2, :my_interaction)
cropidx
while true
    t_start = time()
    disp, liveimg_ = pycall(py"""align_next""", Tuple{Tuple{Int,Int},PyArray})
    liveimg[] .= liveimg_[1:4:end, 1:4:end]
    if updateref
        refimg[] .= pycall(py"""set_ref""", PyArray, cropidx)
        updateref = false
    end
    println(1 / ((time() - t_start)), " ", disp[1], " ", disp[2])
    notify(liveimg)
    yield()
end