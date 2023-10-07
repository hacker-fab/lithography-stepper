from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from litho_img_lib import *
from litho_gui_lib import *

THUMBNAIL_SIZE: tuple[int,int] = (160,90)


#region: widgets

# GUI Controller
GUI: GUI_Controller = GUI_Controller(grid_size = (4,5),
                                     title = "Lithographer V1.0.0")

# Debugger
debug: Debug = Debug(root=GUI.root)
debug.grid(3,0,colspan=5)
GUI.add_widget("debug", debug)

#region: Import thumbnails
pattern_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                     thumb_size=THUMBNAIL_SIZE,
                                     text="Pattern",
                                     debug=debug)
pattern_thumb.grid(2,0)
GUI.add_widget("pattern_thumb", pattern_thumb)

flatfield_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        text="Flatfield",
                                        debug=debug,
                                        accept_alpha=True)
flatfield_thumb.grid(2,1, colspan=2)
GUI.add_widget("flatfield_thumb", flatfield_thumb)

red_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        text="Red Focus",
                                        debug=debug)
red_focus_thumb.grid(2,3)
GUI.add_widget("red_focus_thumb", red_focus_thumb)

uv_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                      thumb_size=THUMBNAIL_SIZE,
                                      text="uv Focus",
                                      debug=debug)
uv_focus_thumb.grid(2,4)
GUI.add_widget("uv_focus_thumb", uv_focus_thumb)
#endregion

#region: Toggles
posterize_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Now Posterizing","NOT Posterizing"),
                                  debug=debug)
posterize_toggle.grid(1,0)
flatfield_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Using Flatfield","NOT Using Flatfield"),
                                  debug=debug)
flatfield_toggle.grid(1,1, colspan=2)
#endregion

#region: intput fields
min_alpha_intput: Intput = Intput(root=GUI.root,
                                  name="Min Alpha",
                                  default=0,
                                  min = 0,
                                  max = 255,
                                  debug=debug,
                                  auto_fix=False)
max_alpha_intput: Intput = Intput(root=GUI.root,
                                  name="Max Alpha",
                                  default=255,
                                  min = 0,
                                  max = 255,
                                  debug=debug,
                                  auto_fix=False)

min_alpha_intput.grid(0,1)
max_alpha_intput.grid(0,2)

def min_alpha_extra_verification(value: int) -> bool:
  return value <= max_alpha_intput.get()
def max_alpha_extra_verification(value: int) -> bool:
  return value >= min_alpha_intput.get()

min_alpha_intput.extra_verification = min_alpha_extra_verification
max_alpha_intput.extra_verification = max_alpha_extra_verification

GUI.add_widget("min_alpha_intput", min_alpha_intput)
GUI.add_widget("max_alpha_intput", max_alpha_intput)

duration_intput: Intput = Intput(root=GUI.root,
                                         name="Pattern Duration",
                                         default=1000,
                                         min = 0,
                                         max = 1000,
                                         debug=debug)
duration_intput.grid(1,5)
GUI.add_widget("duration_intput", duration_intput)
#endregion

#region: Buttons
#region: clear button
clear_button: Button = Button(
  GUI.root,
  text = 'clear',
  command = GUI.proj.clear,
  bg = 'black',
  fg = 'white')
clear_button.grid(
  row = 0,
  column = 0,
  sticky='nesw')
GUI.add_widget("clear_button", clear_button)
#endregion
#region: red focus button

# processing for showing red focus
# posterizeing
# TODO flatfield correction
# resizeing
def show_red_focus() -> None:
  debug.info("Showing red focus image")
  # posterizeing
  image: Image.Image = red_focus_thumb.temp_image
  if(posterize_toggle.state and image.mode != 'L'):
    debug.info("Posterizing image...")
    red_focus_thumb.temp_image = posterize(red_focus_thumb.temp_image)
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
  text = 'show red focus',
  command = show_red_focus)
red_focus_button.grid(
  row = 0,
  rowspan = 2,
  column = 3,
  sticky='nesw')
GUI.add_widget("red_focus_button", red_focus_button)
#endregion
#region: uv focus button

# processing for showing uv focus
# TODO flatfield correction
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
  text = 'Show uv Focus',
  command = show_uv_focus)
uv_focus_button.grid(
  row = 0,
  rowspan = 2,
  column = 4,
  sticky='nesw')
GUI.add_widget("uv_focus_button", uv_focus_button)
#endregion
#region: patterning button

# processing for patterning
# posterizeing
# TODO flatfield correction
# TODO check if can resize before flatfield
# resizeing
def show_pattern() -> None:
  # posterizeing
  image: Image.Image = pattern_thumb.temp_image
  if(posterize_toggle.state and (image.mode != 'L' or image.mode != 'LA')):
    debug.info("Posterizing...")
    pattern_thumb.temp_image = posterize(pattern_thumb.image)
    pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  elif(not posterize_toggle.state and (image.mode == 'L' or image.mode == 'LA')):
    debug.info("Resetting...")
    pattern_thumb.temp_image = pattern_thumb.image
    pattern_thumb.update_thumbnail(pattern_thumb.temp_image)
  # flatfield correction
  image = pattern_thumb.temp_image
  if(flatfield_toggle.state and (image.mode == 'L' or image.mode == 'RGB')):
    debug.info("Applying flatfield corretion...")
    alpha_channel = convert_to_alpha_channel(flatfield_thumb.image,
                                             new_scale=(min_alpha_intput.get(),max_alpha_intput.get()),
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
  debug.info("Patterning for " + str(duration_intput.get()) + "ms")
  GUI.proj.show(pattern_thumb.temp_image, duration=duration_intput.get())
  debug.info("Done")

pattern_button: Button = Button(
  GUI.root,
  text = 'Begin\nPatterning',
  command = show_pattern,
  bg = 'red',
  fg = 'white')
pattern_button.grid(
  row = 2,
  rowspan = 2,
  column = 5,
  sticky='nesw')
GUI.add_widget("pattern_button", pattern_button)
#endregion
#endregion

#region: Text Fields
duration_text: Label = Label(
  GUI.root,
  text = "Duration (ms)",
  justify = 'center',
  anchor = 'center'
)
duration_text.grid(
  row = 0,
  column = 5,
  sticky='nesw'
)
GUI.add_widget("duration_text", duration_text)

#endregion

GUI.debug.info("Debug info will appear here")
GUI.mainloop()


#endregion



