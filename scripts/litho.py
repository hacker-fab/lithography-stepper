from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from litho_img_lib import fit_image, convert_to_alpha_channel, posterize
from litho_gui_lib import *

# This code was written by Luca Garlati
# it is intended for use in Hacker Fab
# please credit on redistribution

# TODO:
# add help popup window
# auto crop amscope screenshots
# implement a proper error creation and handling system
# refactor this spaghetti
# use the image.point function for rescaling
# allow toggling pattern without re-importing
# use max/min difference of grayscale converted flatfield image as suggestion 
#   for the flatfield correction intensity in the debug widget
# refactor alpha range handling
# add advanced options feature to specify things like:
# - downsampling target resolution for mask building
# Better update detection system

# declare root tk object
root: Tk = Tk()
# v1    working initial prototype
# v2    added UV focus image option
# v3    brightness correction implemented
# v4    begin refactoring backend
#   .1  Better Toggles
#   .2  Better Debug
#   .3  Betterer Toggles
#   .4  Better Thumbnails
#   .5  Main UI Controller
#   .6

root.title("Litho V4.4")

# debug box at the bottom
debug: Debug = Debug(root)
debug.grid(3, 0, colspan = 5)


# posterizes pattern image
# def posterize_pattern() -> None:
#   global pattern_img
#   pattern_img = posterize(pattern_img)
#   debug.info("Posterized pattern")


# get projector dimentions
def win_size() -> tuple[int,int]:
  return (proj.winfo_width(), proj.winfo_height())

# set alpha range if specified, returns alpha range
last_alpha_used: tuple[int,int] = (0,0)
def alpha_range(new_range: tuple[int,int] | None = None) -> tuple[int,int]:
  global last_alpha_used
  # check if query or assignment
  if(new_range == None):
    return last_alpha_used
  # assignment, validate input
  if not (new_range[0] >= 0 and
          new_range[0] <= 255 and
          new_range[1] >= 0 and
          new_range[1] <= 255 and
          new_range[0] < new_range[1]):
    debug.error("invalid alpha range: "+str(new_range))
    assert(False)
  #assign new value and return
  last_alpha_used = new_range
  return last_alpha_used

############
### Proj ###
############

# setup projector windows
proj: Toplevel = Toplevel(root)
proj.title("Image Window")
proj.attributes('-fullscreen',True)
proj['background'] = '#000000'
proj.grid_columnconfigure(0, weight=1)
proj.grid_rowconfigure(0, weight=1)

# projector variables
thumbnail_size: tuple[int,int] = (160,90)
# pattern_img:   Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
# mask_img:      Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,0))
# alpha_channel: Image.Image
current_img:   Label = Label()

# makes a photo thumbnail copy at specified size
# def auto_thumbnail(image: Image.Image, size: tuple[int,int] = thumbnail_size) -> ImageTk.PhotoImage:
#   thumb: Image.Image = image.copy()
#   thumb.thumbnail(size, Image.Resampling.LANCZOS)
#   return ImageTk.PhotoImage(thumb)


# will process the input pattern based on the current settings:
#   posterize
#   size
def pattern_processing_func(input_image: Image.Image) -> Image.Image:
  output_image: Image.Image = input_image.copy()
  if(posterize_toggle.state and output_image.mode != 'L'):
    output_image = posterize(output_image)
  if(input_image.size != fit_image(input_image, win_size())):
    output_image = output_image.resize(win_size(), Image.Resampling.LANCZOS)
    # size
  return output_image

pattern_thumb: Thumbnail = Thumbnail(
  root,
  thumb_size=thumbnail_size,
  text = "Pattern",
  debug = debug,
  func = pattern_processing_func)
pattern_thumb.grid(2, 0)


# effectively a wrapper for convert_to_alpha_channel
def generate_flatfield(new_image: Image.Image) -> Image.Image:
  # check if we need to update
  alphas: tuple[int,int] = (min_alpha.get(), max_alpha.get())
  target_size: tuple[int,int] = pattern_thumb.processed_img.size
  debug.info("checking if mask needs updating...")
  if (alpha_range() != alphas):
    # alphas have changed
    debug.info("mismatch alpha range, updating mask...")
  elif (flatfield_thumb.processed_img.size != target_size):
    # pattern image size has changed
    debug.info("mismatch image size, updating mask...")
  else:
    debug.info("mask is up to date")
    return flatfield_thumb.processed_img
  #update alpha stuff
  alpha_range(alphas)
  alpha_channel = convert_to_alpha_channel(new_image, new_scale=alpha_range(),
                                           target_size=target_size, downsample_target=540)
  debug.info("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" mask")
  return alpha_channel

# effectively a wrapper for convert_to_alpha_channel
def force_generate_flatfield(new_image: Image.Image) -> Image.Image:
  # check if we need to update
  alphas: tuple[int,int] = (min_alpha.get(), max_alpha.get())
  target_size: tuple[int,int] = pattern_thumb.processed_img.size
  debug.info("building mask...")
  #update alpha stuff
  alpha_range(alphas)
  alpha_channel = convert_to_alpha_channel(new_image, new_scale=alpha_range(),
                                           target_size=target_size, downsample_target=540)
  debug.info("generating intensity guess...")
  brightness: tuple[int,int] = get_brightness_range(flatfield_thumb.image.convert("L"))
  debug.info("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" mask\n"+
            "Recommended alpha range: ("+str(brightness[1]-brightness[0])+","+str(255)+")")
  return alpha_channel


flatfield_thumb: Thumbnail = Thumbnail(
  root,
  thumb_size = thumbnail_size,
  text = "Flatfield Correction",
  debug = debug,
  func = generate_flatfield,
  import_func=force_generate_flatfield)
flatfield_thumb.grid(2, 1, colspan=2)

red_focus_thumb: Thumbnail = Thumbnail(
  root,
  thumb_size = thumbnail_size,
  text = "Red Focus",
  debug = debug)
red_focus_thumb.grid(2, 3)

UV_focus_thumb: Thumbnail = Thumbnail(
  root,
  thumb_size=thumbnail_size,
  text="UV Focus",
  debug=debug)
UV_focus_thumb.grid(2,4)

# posterize toggle button
posterize_toggle: Toggle = Toggle(root, debug = debug,
                                  text=("Posterizing", "NOT Posterizing"),
                                  func=pattern_thumb.update)
posterize_toggle.grid(1,0)

# toggle alpha mask button
flatfield_toggle: Toggle = Toggle(root, debug = debug,
                                  text=("Using Flatfield", "NOT Using Flatfield"),
                                  func=flatfield_thumb.update)
flatfield_toggle.grid(1,1,colspan=2)


# private method to show an image on the projection window
max_alpha: Variable = IntVar()
min_alpha: Variable = IntVar()
max_alpha.set(255)
min_alpha.set(0)
def __show_img(input_image: Image.Image):
  # setup
  window_size: tuple[int,int] = (proj.winfo_width(), proj.winfo_height())
  img_copy: Image.Image = input_image.copy()
  global current_img
  # resample if image isn't correct size
  if(img_copy.width != window_size[0] or
     img_copy.height != window_size[1]):
    debug.info("resampling image for projection...")
    img_copy = img_copy.resize(fit_image(img_copy, window_size), Image.Resampling.LANCZOS)
  # apply alpha mask if enabled
  if(flatfield_toggle.state):
    flatfield_thumb.update()
    if(img_copy.size != flatfield_thumb.processed_img.size):
      debug.error("mismatch image sizes:\n"+
                  "pattern: "+str(img_copy.size)+"\n"+
                  "mask: "+str(flatfield_thumb.processed_img.size)+"\n"+
                  "proj: "+str((proj.winfo_width(),proj.winfo_height())))
      assert(False)
    img_copy.putalpha(flatfield_thumb.processed_img)
  # destroy currently displayed image
  current_img.destroy()
  # create new button
  photo = ImageTk.PhotoImage(img_copy)
  label: Label = Label(proj, image = photo, bg='black')
  label.image = photo
  label.grid(row=0,column=0,sticky="nesw")
  # assign this as the current button
  current_img = label

# private method to delete image widget, effectively clearing the proj
def __hide_img():
  current_img.destroy()
  root.update()

# do the patterning
def begin_patterning():
  # check duration and alpha are valid
  if (duration.get() <= 0):
    debug.error("duration = "+str(duration.get())+" < 0, aborting")
    return
  # prepare for patterning
  pattern_button.configure(bg="black")
  debug.info("Patterning for "+str(duration.get())+"ms...")
  __show_img(pattern_thumb.processed_img)
  # begin
  root.update()
  sleep(duration.get() / 1000)
  # clean up
  __hide_img()
  pattern_button.configure(bg="red")
  root.update()
  debug.info("Finished patterning")

# show patterning image
def show_focusing():
  __show_img(red_focus_thumb.image)
  debug.info("showing red focus pattern")
  root.update()

# show uv focusing image
def show_uv_focus():
  __show_img(UV_focus_thumb.image)
  debug.info("showing uv focus pattern")
  root.update()

# wrapper for clear button
def clear_image():
  __hide_img()
  debug.info("Projector cleared")

###########
### GUI ###
###########

# setup GUI
root.geometry("900x220")
root.resizable(width = True, height = True)

# weight all rows / cols
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=6)
root.grid_rowconfigure(3, weight=2)

root.grid_columnconfigure(0, weight=5)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=5)
root.grid_columnconfigure(4, weight=5)
  
proj.update()
# show default images
# set_mask(False)

# clear images button
button: Button = Button(
  root,
  text = 'clear',
  command = clear_image,
  bg = 'black',
  fg = 'white')
button.grid(
  row = 0,
  column = 0,
  sticky='nesw')

# Show min_alpha field
entry: Entry = Entry(
  root,
  textvariable = min_alpha,
  justify = 'center'
)
entry.grid(
  row = 0,
  column = 1,
  sticky = 'nesw')

# Show max_alpha field
entry: Entry = Entry(
  root,
  textvariable = max_alpha,
  justify = 'center'
)
entry.grid(
  row = 0,
  column = 2,
  sticky = 'nesw')

# Show IR focusing image button
button: Button = Button(
  root,
  text = 'show red focus',
  command = show_focusing)
button.grid(
  row = 0,
  rowspan = 2,
  column = 3,
  sticky='nesw')

# Show UV focusing image button
button: Button = Button(
  root,
  text = 'show UV focus',
  command = show_uv_focus)
button.grid(
  row = 0,
  rowspan = 2,
  column = 4,
  sticky='nesw')

# "duration ms" text field
label: Label = Label(
  root,
  text = "duration ms",
  justify = 'center',
  anchor = 'center'
)
label.grid(
  row = 0,
  column = 5,
  sticky='nesw'
)

# Show duration field
duration: Variable = IntVar()
duration.set(1000)
entry: Entry = Entry(
  root,
  textvariable = duration,
  justify = 'center'
)
entry.grid(
  row = 1,
  column = 5,
  sticky = 'nesw')

# pattern the selected image
pattern_button: Button = Button(
  root,
  text = 'begin\npatterning',
  command = begin_patterning,
  bg = 'red',
  fg = 'white')
pattern_button.grid(
  row = 2,
  rowspan = 2,
  column = 5,
  sticky='nesw')


debug.info("Debug info will appear here")
root.mainloop()

