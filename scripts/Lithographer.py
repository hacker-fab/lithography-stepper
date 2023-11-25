from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label, Text
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
from litho_img_lib import *
from litho_gui_lib import *

# TODO
# text display (for current motor coordinates)
# Dpad Buttons (moving the motors)
# spot for "entire layer" image
# spot for "current tile" image
# 
# Low Priority
# - an image showing live camera output (I'll just set the image and it will update basically)
# - CLI
# - add a button to show pure white image for flatfield correction
# - fix bug where flatfield pattern is reapplied on second pattern show
#     to reproduce, import flatfield and pattern, enable posterize and flatfield, press show twice
# 


THUMBNAIL_SIZE: tuple[int,int] = (160,90)

# GUI Controller
GUI: GUI_Controller = GUI_Controller(grid_size = (9,9),
                                     title = "Lithographer V1.2.4",
                                     add_window_size=(0,300))
# Debugger
debug: Debug = Debug(root=GUI.root)
debug.grid(8,0,colspan=5)
GUI.add_widget("debug", debug)

#region: Import thumbnails
pattern_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                     thumb_size=THUMBNAIL_SIZE,
                                     text="Pattern",
                                     debug=debug)
pattern_thumb.grid(4,0, rowspan=4)
GUI.add_widget("pattern_thumb", pattern_thumb)

# return a guess for correction intensity, 0 to 50 %
def guess_alpha():
  brightness: tuple[int,int] = get_brightness_range(flatfield_thumb.image, downsample_target=480)
  FF_strength_intput.set(round(((brightness[1]-brightness[0])*100)/510))
flatfield_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        text="Flatfield",
                                        debug=debug,
                                        accept_alpha=True,
                                        func_on_success=guess_alpha)
flatfield_thumb.grid(4,1, colspan=2, rowspan=4)
GUI.add_widget("flatfield_thumb", flatfield_thumb)

red_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        text="Red Focus",
                                        debug=debug)
red_focus_thumb.grid(4,3, rowspan=4)
GUI.add_widget("red_focus_thumb", red_focus_thumb)

uv_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                      thumb_size=THUMBNAIL_SIZE,
                                      text="UV Focus",
                                      debug=debug)
uv_focus_thumb.grid(4,4, rowspan=4)
GUI.add_widget("uv_focus_thumb", uv_focus_thumb)
#endregion

#region: Toggles
posterize_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Now Posterizing","NOT Posterizing"),
                                  debug=debug)
posterize_toggle.grid(2,1)
flatfield_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Using Flatfield","NOT Using Flatfield"),
                                  debug=debug)
flatfield_toggle.grid(3,1)
#endregion

#region: intput fields

FF_strength_intput: Intput = Intput(
  root=GUI.root,
  name="FF Strength",
  default=0,
  min = 0,
  max = 100,
  debug=debug)
FF_strength_intput.grid(3,2)
GUI.add_widget("FF_strength_intput", FF_strength_intput)

duration_intput: Intput = Intput(
  root=GUI.root,
  name="Pattern Duration",
  default=1000,
  min = 0,
  debug=debug)
duration_intput.grid(3,5)
GUI.add_widget("duration_intput", duration_intput)

post_strength_intput: Intput = Intput(
  root=GUI.root,
  name="Post Strength",
  default=50,
  min=0,
  max=100,
  debug=debug
)
post_strength_intput.grid(2,2)
GUI.add_widget("post_strength_intput", post_strength_intput)

#endregion

#region: Buttons
#region: clear button
clear_button: Button = Button(
  GUI.root,
  text = 'Clear',
  command = GUI.proj.clear,
  bg = 'black',
  fg = 'white')
clear_button.grid(
  row = 2,
  column = 0,
  sticky='nesw')
GUI.add_widget("clear_button", clear_button)
#endregion
#region: red focus button

# processing for showing red focus
# posterizeing
# resizeing
def show_red_focus() -> None:
  debug.info("Showing red focus image")
  # posterizeing
  image: Image.Image = red_focus_thumb.temp_image
  if(posterize_toggle.state and (image.mode != 'L' or post_strength_intput.changed())):
    debug.info("Posterizing image...")
    red_focus_thumb.temp_image = posterize(red_focus_thumb.temp_image, round((post_strength_intput.get()*255)/100))
    red_focus_thumb.update_thumbnail(red_focus_thumb.temp_image)
  elif(not posterize_toggle.state and image.mode == 'L'):
    debug.info("Resetting image...")
    red_focus_thumb.temp_image = red_focus_thumb.image
    red_focus_thumb.update_thumbnail(red_focus_thumb.temp_image)
  # resizeing
  image: Image.Image = red_focus_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing image for projection...")
    red_focus_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  GUI.proj.show(red_focus_thumb.temp_image)

red_focus_button: Button = Button(
  GUI.root,
  text = 'Show Red Focus',
  command = show_red_focus)
red_focus_button.grid(
  row = 2,
  rowspan = 2,
  column = 3,
  sticky='nesw')
GUI.add_widget("red_focus_button", red_focus_button)
#endregion
#region: uv focus button

# processing for showing uv focus
# resizeing
def show_uv_focus() -> None:
  debug.info("Showing uv focus image")
  # resizeing
  image: Image.Image = uv_focus_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing image for projection...")
    uv_focus_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  GUI.proj.show(uv_focus_thumb.temp_image)

uv_focus_button: Button = Button(
  GUI.root,
  text = 'Show UV Focus',
  command = show_uv_focus)
uv_focus_button.grid(
  row = 2,
  rowspan = 2,
  column = 4,
  sticky='nesw')
GUI.add_widget("uv_focus_button", uv_focus_button)
#endregion
#region: patterning buttons

# processing for patterning
# posterizeing
# flatfield correction
# resizeing
def prep_pattern() -> None:
  # posterizeing
  image: Image.Image = pattern_thumb.temp_image
  if(posterize_toggle.state and ((not (image.mode == 'L' or image.mode == 'LA')) or post_strength_intput.changed())):
    # posterizing enabled, and image isn't poterized
    debug.info("Posterizing...")
    pattern_thumb.temp_image = posterize(pattern_thumb.image, round((post_strength_intput.get()*255)/100))
    pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  elif(not posterize_toggle.state and (image.mode == 'L' or image.mode == 'LA')):
    # posterizing disabled, but image is posterized
    debug.info("Resetting Posterizing...")
    pattern_thumb.temp_image = pattern_thumb.image
    pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  
  # flatfield correction
  image = pattern_thumb.temp_image
  if(flatfield_toggle.state and (image.mode == 'L' or image.mode == 'RGB' or 
     FF_strength_intput.changed())):
    debug.info("Applying flatfield corretion...")
    alpha_channel = convert_to_alpha_channel(flatfield_thumb.image,
                                             new_scale=dec_to_alpha(FF_strength_intput.get()),
                                             target_size=image.size,
                                             downsample_target=540)
    pattern_thumb.temp_image.putalpha(alpha_channel)
    pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  elif(not flatfield_toggle.state):
    if(image.mode == 'RGBA'):
      debug.info("Removing flatfield corretion...")
      pattern_thumb.temp_image = RGBA_to_RGB(pattern_thumb.temp_image)
      pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
    if(image.mode == 'LA'):
      debug.info("Removing flatfield corretion...")
      pattern_thumb.temp_image = LA_to_L(pattern_thumb.temp_image)
      pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  # resizeing
  image = pattern_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing...")
    pattern_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  
# show pattern for specified duration
def show_pattern_timed() -> None:
  prep_pattern()
  debug.info("Patterning for " + str(duration_intput.get()) + "ms")
  result = GUI.proj.show(pattern_thumb.temp_image, duration=duration_intput.get())
  if(result): debug.info("Done")
pattern_button_timed: Button = Button(
  GUI.root,
  text = 'Begin\nPatterning',
  command = show_pattern_timed,
  bg = 'red',
  fg = 'white')
pattern_button_timed.grid(
  row = 4,
  column = 5,
  rowspan=4,
  sticky='nesw')
GUI.add_widget("pattern_button_timed", pattern_button_timed)

# show pattern until user presses clear
def show_pattern_fixed() -> None:
  prep_pattern()
  debug.info("Showing Pattern")
  GUI.proj.show(pattern_thumb.temp_image)
pattern_button_fixed: Button = Button(
  GUI.root,
  text = 'Show Pattern',
  command = show_pattern_fixed)
pattern_button_fixed.grid(
  row = 3,
  column = 0,
  sticky='nesw')
GUI.add_widget("pattern_button_fixed", pattern_button_fixed)


#endregion
#endregion

#region: Text Fields

#region: Duration
duration_text: Label = Label(
  GUI.root,
  text = "Duration (ms)",
  justify = 'center',
  anchor = 'center'
)
duration_text.grid(
  row = 2,
  column = 5,
  sticky='nesw'
)
GUI.add_widget("duration_text", duration_text)
#endregion

#Region Help Popup

help_text: str = """
How do I import an image?
- Just click on the black thumbnail and a dialog will open
  - The UI will try to fix images in the incorrect mode
  - The UI will reject incorrect file formats


How do I move the projector window?
- On Windows, click the projector window, then win + shift + arrow keys to move it to the second screen 
- On Mac, no clue :P


How do I use flatfield correction?
1. Take a flatfield image
  - Set the projector to UV mode
  - Display a fully white image on the projector
  - Put a clean blank chip under the projector
  - Take a snapshot with the amscope camera (1080p is plenty)
  - Crop out any black borders if present
2. Import the flatfield image
  - Just click on the flatfield image preview thumbnial
  - The UI will automatically guess the correct correction intensity to use 
3. Make sure flatfield correction is enabled
  - press the "use flatfield" button to toggle it
4. Done, though some things to note
  - Flatfield correction will only be applied to the pattern, not red or uv focus
  - The intensity of the correction is normalized from 0 to 100 for your convenience:
    - 0   means no correction, ie completely transparent
    - 50  means the correction is applied at full strength, from pure black pixels to pure white
    - 100 means max correction, ie completely opaque


Posterizer? I barely know her!
- TL;DR, make pattern monochrome for sharper edges
- What is posterizing?
  - Posterizing is the process for reducing the bit depth of an image.
  - For this GUI, it reduces the image to 1 bit depth or monochrome (not greyscale, only pure black and pure white)
- What is that number next to it?
  - The number next to the toggle is the cutoff value
  - Unless you're losing features or lines are growing / shrinking, leave it at 50
  - It behaves as follows:
    - 100 is max cutoff, so only pure white will stay white
    -  50 is default, light greys will be white, and dark greys will be black
    -   0 is min cutoff, so only pure black will stay black
- What does this apply to?
  - Patterning image
  - Red focus image
  - NOT UV focus image because it would just be solid black
- What does it actually do?
  - It makes all edges in the image perfectly sharp, improving the quality of the patterning.
  - It's unlikely, but you may not need to use it if:
    - Your pattern is RGB or L, and doesn't have an alpha channel
    - Your pattern is already monochrome
    - Your pattern is at exactly the projector's resolution. can't be even a single pixel off
- What does this apply to?
  - Patterning image
  - Red focus image
  - NOT UV focus image because it would just be solid black


Think something is missing? Have a suggestion?
see our website for contact methods:
http://hackerfab.ece.cmu.edu


This tool was made by Luca Garlati for Hackerfab
"""
help_popup: TextPopup = TextPopup(
  root=GUI.root,
  title="Help Popup",
  button_text="Help",
  popup_text=help_text)
help_popup.grid(8,5)
#endregion

#region: progress bars
pattern_progress: Progressbar = Progressbar(
  GUI.root,
  orient='horizontal',
  mode='determinate',
  )
pattern_progress.grid(
  row = 1,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.proj.progressbar = pattern_progress
GUI.add_widget("pattern_progress", pattern_progress)
#endregion

#region: Camera
camera: Thumbnail = Thumbnail(root=GUI.root,
                              thumb_size=(GUI.window_size[0],(GUI.window_size[0]*9)//16),
                              debug=debug)
camera.grid(
  row=0,
  col=0,
  colspan=GUI.grid_size[1],
)
#endregion

#region: Stage Control

stage: Stage_Controller = Stage_Controller()
#region: Buttons

### X axis ###
up_x_button: Button = Button(
  GUI.root,
  text = '+x',
  command = lambda : stage.step('+x')
  )
up_x_button.grid(
  row = 4,
  column = 6,
  sticky='nesw')
GUI.add_widget("up_button", up_x_button)

x_intput = Intput(
  root=GUI.root,
  name="X",
  default=stage.x(),
  debug=debug)
x_intput.grid(5,6)
GUI.add_widget("x_intput", x_intput)

down_x_button: Button = Button(
  GUI.root,
  text = '-x',
  command = lambda : stage.step('-x')
  )
down_x_button.grid(
  row = 6,
  column = 6,
  sticky='nesw')
GUI.add_widget("down_button", down_x_button)

### Y axis ###
up_y_button: Button = Button(
  GUI.root,
  text = '+y',
  command = lambda : stage.step('+y')
  )
up_y_button.grid(
  row = 4,
  column = 7,
  sticky='nesw')
GUI.add_widget("up_button", up_y_button)

y_intput = Intput(
  root=GUI.root,
  name="Y",
  default=stage.y(),
  debug=debug)
y_intput.grid(5,7)
GUI.add_widget("y_intput", y_intput)

down_y_button: Button = Button(
  GUI.root,
  text = '-y',
  command = lambda : stage.step('-y')
  )
down_y_button.grid(
  row = 6,
  column = 7,
  sticky='nesw')
GUI.add_widget("down_button", down_y_button)

### Z axis ###
up_z_button: Button = Button(
  GUI.root,
  text = '+z',
  command = lambda : stage.step('+z')
  )
up_z_button.grid(
  row = 4,
  column = 8,
  sticky='nesw')
GUI.add_widget("up_button", up_z_button)

z_intput = Intput(
  root=GUI.root,
  name="Z",
  default=stage.z(),
  debug=debug)
z_intput.grid(5,8)
GUI.add_widget("z_intput", z_intput)

down_z_button: Button = Button(
  GUI.root,
  text = '-z',
  command = lambda : stage.step('-z')
  )
down_z_button.grid(
  row = 6,
  column = 8,
  sticky='nesw')
GUI.add_widget("down_button", down_z_button)

set_coords_button: Button = Button(
  GUI.root,
  text = 'Set Coords',
  command = lambda : stage.set(x_intput.get(), y_intput.get(), z_intput.get())
  )
set_coords_button.grid(
  row = 7,
  column = 6,
  columnspan = 3,
  sticky='nesw')

#endregion

#endregion

GUI.debug.info("Debug info will appear here")
GUI.mainloop()




