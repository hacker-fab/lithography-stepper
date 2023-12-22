
using GLMakie
GLMakie.activate!(inline=false)

# Global Status
running = true
# Vision Data
visionCh = Channel{Array{Int64}}(1)

include("stage_control.jl")
include("vision.jl")

## Visualize
f = Figure()

ax = Axis(f[1, 1])
lines!(ax, @lift($(VisionErrState[:x])[1, :]), color=:red)
lines!(ax, @lift($(VisionErrState[:x])[2, :]), color=:black)
# lines!(ax, @lift($(VisionErrState[:x])[3, :]), color=:blue)

ax = Axis(f[1, 2])
lines!(ax, @lift($(VisionErrState[:u])[1, :]), color=:red)
lines!(ax, @lift($(VisionErrState[:u])[2, :]), color=:black)
lines!(ax, @lift($(VisionErrState[:u])[3, :]), color=:blue)

ax = Axis(f[2:5, 1], aspect=DataAspect())
deregister_interaction!(ax, :rectanglezoom)
image!(ax, liveimg)

ax2 = Axis(f[2:5, 2], aspect=DataAspect())
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

display(f)


while true
    t_start = time()
    disp, liveimg_ = pycall(py"""align_next""", Tuple{Tuple{Int,Int},PyArray})
    liveimg[] .= liveimg_[1:4:end, 1:4:end]
    if updateref
        refimg[] .= pycall(py"""set_ref""", PyArray, cropidx)
        updateref = false
    end
    if updateref
        put!(visionCh, [Int64(time_ns()), Int64.(disp .* 0)..., Int64(0)])
    else
        put!(visionCh, [Int64(time_ns()), Int64.(disp)..., Int64(0)])
    end
    # println(1 / ((time() - t_start)), " ", disp[1], " ", disp[2])

    lock(VisionErrState[:lock]) do
        notify(VisionErrState[:x])
        notify(VisionErrState[:t])
        notify(VisionErrState[:u])
        notify(VisionErrState[:em])
    end
    notify(liveimg)
    yield()
end
updateref