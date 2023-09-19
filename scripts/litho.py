from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from litho_img_lib import fit_image, convert_to_alpha_channel

# This code was written by Luca Garlati
# it is intended for use in Hacker Fab
# please credit on redistribution

# TODO:
# - auto convert images to monochrome
# - convert RGB images to alpha masks
# - auto apply alpha masks to images
# - add help popup window
# - auto crop correction images
# - use a dict to speed up mask creation
# - add progress bar
# - - Show progress when patterning
# - - Show progress when generating mask
# - fit alpha 
# - add a max/min alpha input
# - add ability to toggle alpha correction for all images on UI
# - better error handling

# declare root tk object
root: Tk = Tk()
# v1    working initial prototype
# v2    added UV focus image option
#   .1  major UI overhaul
#   .2  added debug printouts
#   .3  transferred image utils to separate lib
#   .4  working alpha mask
#   .5  several minor code optimizations
#   .6  reworked UI again 
# v3    brightness correction implemented
#   .1  idiot-proofing
root.title("Litho V3.1")

# Text box at the bottom
debug_widget: Label = Label(
  root,
  text = "test",
  justify = 'left',
  anchor = 'w'
)
debug_widget.grid(
  row = 3,
  column = 0,
  columnspan = 4,
  sticky='nesw'
)

def debug(text: str):
  debug_widget.config(text = text+"\nMade by Luca Garlati")
  print(text)
  root.update()

# get projector dimentions
def win_size() -> tuple[int,int]:
  return (proj.winfo_width(), proj.winfo_height())

# toggle alpha variable for projecting, return new status
use_alpha: bool = False
def toggle_alpha():
  global use_alpha, alpha_button
  use_alpha = not use_alpha
  if(use_alpha):
    alpha_button.config(bg="black", fg="white", text = 'using flat field')
    debug("Flat field correction ENabled")
  else:
    alpha_button.config(bg="white", fg="black", text = 'NOT using flat field')
    debug("Flat field correction DISabled")

# set alpha range if specified, returns alpha range
last_alpha_used: tuple[int,int] = (0,0)
def alpha_range(new_range: tuple[int,int] = (0,0)) -> tuple[int,int]:
  assert(new_range[0] >= 0)
  assert(new_range[0] <= 255)
  assert(new_range[1] >= 0)
  assert(new_range[1] <= 255)
  global last_alpha_used
  if(new_range!=(0,0)):
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
pattern_img:   Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
focus_img:     Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
uv_img:        Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
mask_img:      Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,0))
alpha_channel: Image.Image
current_img:   Label = Label()

def update_alpha_channel() -> bool:
  # if we don't need to update, then we already know it's good (recursive assurance)
  alphas: tuple[int,int] = (min_alpha.get(), max_alpha.get())
  if (alpha_range() == alphas):
    return True
  else:
    if(alphas[0] < 0):
      debug("min alpha < 0")
      return False
    if(alphas[0] > 255):
      debug("min alpha > 255")
      return False
    if(alphas[1] < 0):
      debug("max alpha < 0")
      return False
    if(alphas[1] > 255):
      debug("max alpha > 255")
      return False
    if(alphas[0] > alphas[1]):
      debug("min > max alpha")
      return False
    #update alpha stuff
    alpha_range(alphas)
    global alpha_channel
    alpha_channel = convert_to_alpha_channel(mask_img, new_scale=alpha_range(), target_size=(proj.winfo_width(), proj.winfo_height()))
    return True

prev_pattern_button: Button = Button()
# set new pattern image
def set_pattern(query: bool = True):
  global pattern_img, prev_pattern_button
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      debug("Pattern import cancelled")
    else:
      debug("Pattern set to "+basename(path))
    # save the image
    pattern_img = Image.open(path).copy()
    # resize to projector
    pattern_img = pattern_img.resize(fit_image(pattern_img, win_size=win_size()),
                                     Image.Resampling.LANCZOS)
  # delete previous button
  prev_pattern_button.destroy()
  # create thumbnail version
  small: Image.Image = pattern_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with button
  button: Button = Button(
    root,
    image = img,
    text = "Pattern",
    compound = "top",
    command = set_pattern
    )
  button.image = img
  button.grid(
    row = 2,
    column = 0,
    sticky='nesw')
  prev_pattern_button = button

prev_focusing_button: Button = Button()
# set new pattern image
def set_focusing(query: bool = True):
  global focus_img, prev_focusing_button
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      debug("Red focus import cancelled")
    else:
      debug("Red focus set to "+basename(path))
    # save the image
    focus_img = Image.open(path).copy()
    # resize to projector
    focus_img = focus_img.resize(fit_image(focus_img, win_size=win_size()),
                                     Image.Resampling.LANCZOS)
  # delete previous button
  prev_focusing_button.destroy()
  # create thumbnail version
  small: Image.Image = focus_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with button
  button: Button = Button(
    root,
    image = img,
    text = "Red Focus",
    compound = "top",
    command = set_focusing
    )
  button.image = img
  button.grid(
    row = 2,
    column = 3,
    sticky='nesw')
  prev_focusing_button = button

prev_uv_focus_button: Button = Button()
def set_uv_focus(query: bool = True):
  global uv_img, prev_uv_focus_button
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      debug("UV focus import cancelled")
    else:
      debug("UV focus set to "+basename(path))
    # save the image
    uv_img = Image.open(path).copy()
    # resize to projector
    uv_img = uv_img.resize(fit_image(uv_img, win_size=win_size()),
                                     Image.Resampling.LANCZOS)
  # delete previous button
  prev_uv_focus_button.destroy()
  # create thumbnail version
  small: Image.Image = uv_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with button
  button: Button = Button(
    root,
    image = img,
    text = "UV Focus",
    compound = "top",
    command = set_uv_focus
    )
  button.image = img
  button.grid(
    row = 2,
    column = 4,
    sticky='nesw')
  prev_uv_focus_button = button

prev_mask_button: Button = Button()
def set_mask(query: bool = True):
  global mask_img, prev_mask_button, alpha_channel
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    # save the image
    mask_img = Image.open(path).copy()
  # create alpha channel using mask
  debug("creating alpha channel mask...")
  success = update_alpha_channel()
  if(not success):
    return
  debug("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" with "+str(alpha_range())+" alpha channel mask")
  # delete previous button
  prev_mask_button.destroy()
  # create thumbnail version
  small: Image.Image = mask_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with button
  button: Button = Button(
    root,
    image = img,
    text = "Correction Image",
    compound = "top",
    command = set_mask
    )
  button.image = img
  button.grid(
    row = 2,
    column = 1,
    columnspan = 2,
    sticky='nesw')
  prev_mask_button = button

# private method to show an image on the projection window
max_alpha: Variable = IntVar()
min_alpha: Variable = IntVar()
max_alpha.set(255)
min_alpha.set(0)
def __show_img(input_image: Image.Image) -> bool:
  # setup
  window_size: tuple[int,int] = (proj.winfo_width(), proj.winfo_height())
  img_copy: Image.Image = input_image.copy()
  global current_img, alpha_channel
  # resample if image isn't correct size
  if(img_copy.width != window_size[0] or
     img_copy.height != window_size[1]):
    debug("resampling image for projection...")
    img_copy = img_copy.resize(fit_image(img_copy, window_size), Image.Resampling.LANCZOS)
  # apply alpha mask if enabled
  if(use_alpha):
    # check if alpha has changed
    if(alpha_range() != (max_alpha.get(), min_alpha.get())):
      debug("rebuilding mask for projection...")
      success = update_alpha_channel()
      if(not success):
        return False
      debug("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" with "+str(alpha_range())+" alpha channel mask")
    img_copy.putalpha(alpha_channel)
  # destroy currently displayed image
  current_img.destroy()
  # create new button
  photo = ImageTk.PhotoImage(img_copy)
  label: Label = Label(proj, image = photo, bg='black')
  label.image = photo
  label.grid(row=0,column=0,sticky="nesw")
  # assign this as the current button
  current_img = label
  return True

# private method to delete image widget, effectively clearing the proj
def __hide_img():
  current_img.destroy()
  root.update()

# do the patterning
def begin_patterning():
  # check duration and alpha are valid
  if (duration.get() <= 0):
    debug("duration = "+str(duration.get())+" < 0, aborting")
    return
  # prepare for patterning
  global is_patterning
  pattern_button.configure(bg="black")
  if(not __show_img(pattern_img)):
    return
  debug("Patterning for "+str(duration.get())+"ms...")
  # begin
  root.update()
  sleep(duration.get() / 1000)
  # clean up
  __hide_img()
  pattern_button.configure(bg="red")
  root.update()
  debug("Finished patterning")

# show patterning image
def show_focusing():
  if(not __show_img(focus_img)):
    return
  debug("showing red focus pattern")
  root.update()

# show uv focusing image
def show_uv_focus():
  if(not __show_img(uv_img)):
    return
  debug("showing uv focus pattern")
  root.update()

# wrapper for clear button
def clear_image():
  __hide_img()
  debug("Projector cleared")

###########
### GUI ###
###########



# setup GUI
root.geometry("900x220")
# don't make control window resizable
# root.resizable(width = True, height = True)

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
set_pattern(False)
set_focusing(False)
set_uv_focus(False)
set_mask(False)

# clear images button
button: Button = Button(
  root,
  text = 'clear',
  command = clear_image,
  bg = 'black',
  fg = 'white')
button.grid(
  row = 0,
  rowspan = 2,
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

# toggle alpha mask button
alpha_button: Button = Button(
  root,
  text = 'NOT using flat field',
  fg = "black",
  bg = "white",
  command = toggle_alpha)
alpha_button.grid(
  row = 1,
  column = 1,
  columnspan = 2,
  sticky='nesw')

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



debug("Debug info will be displayed here.")
root.mainloop()

