using GLMakie
GLMakie.activate!(inline=false)

# Global Status
running = true
# Vision Data
visionCh = Channel{Array{Int64}}(1)
refCh = Channel{Array{Int64}}(1)

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
image!(ax, @lift($(annoimg)[1:4:end, 1:4:end]))

ax2 = Axis(f[2:5, 2], aspect=DataAspect())
deregister_interaction!(ax2, :rectanglezoom)
image!(ax2, mouseimg)
display(f)

# Mouse Interactions
mouseinit = true
start_position = Float64[0, 0]
register_interaction!(ax2, :my_interaction) do event::Makie.MouseEvent, axis
    global mouseinit
    global start_position
    global liveimgsz
    global refCh

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
        push!(refCh, [xoff, yoff])
    end
    return
end

# deregister_interaction!(ax2, :my_interaction)

display(f)

while true
    vislooponce(visionCh, refCh)

    lock(VisionErrState[:lock]) do
        notify(VisionErrState[:x])
        notify(VisionErrState[:t])
        notify(VisionErrState[:u])
        notify(VisionErrState[:em])
    end
    notify(annoimg)
    notify(mouseimg)
    # sleep(0.03) # 30fps
    yield()
end

# annoimg[]
# running = false

# annoimg[]


# py"""cv2.matchTemplate($(liveimg[]), $(liveimg[]), cv2.TM_CCOEFF_NORMED)"""