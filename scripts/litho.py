from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from litho_img_lib import fit_image, convert_to_alpha_channel, posterize

# This code was written by Luca Garlati
# it is intended for use in Hacker Fab
# please credit on redistribution

# TODO:
# - add help popup window
# - auto crop amscope screenshots
# - implement a proper error creation and handling system
# - refactor this spaghetti

# declare root tk object
root: Tk = Tk()
# v1    working initial prototype
# v2    added UV focus image option
# v3    brightness correction implemented
#   .1  fixed alpha updating bug
#   .2  idiot-proofing and beautifying
#   .3  added posterizing
root.title("Litho V3.3")

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
  global last_alpha_used
  # check if query or assignment
  if(new_range==(0,0)):
    return last_alpha_used
  # assignment, validate input
  if not (new_range[0] >= 0 and
          new_range[0] <= 255 and
          new_range[1] >= 0 and
          new_range[1] <= 255 and
          new_range[0] < new_range[1]):
    debug("invalid alpha range: "+str(new_range))
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
pattern_img:   Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
focus_img:     Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
uv_img:        Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
mask_img:      Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,0))
alpha_channel: Image.Image
current_img:   Label = Label()

# makes a photo thumbnail copy at specified size
def auto_thumbnail(image: Image.Image, size: tuple[int,int] = thumbnail_size) -> ImageTk.PhotoImage:
  thumb: Image.Image = image.copy()
  thumb.thumbnail(size, Image.Resampling.LANCZOS)
  return ImageTk.PhotoImage(thumb)

# updates alpha channel to current settings
def update_alpha_channel(force:bool = False):
  global alpha_channel
  # if we don't need to update, then we already know it's good (recursive assurance)
  alphas: tuple[int,int] = (min_alpha.get(), max_alpha.get())
  target_size: tuple[int,int] = fit_image(pattern_img, win_size())
  if(not force): 
    debug("checking if mask needs updating...")
  if (alpha_range() == alphas and 
      mask_img.size == target_size and 
      not force):
    debug("skipped updating")
    return
  else:
    debug("updating mask...")
    global alpha_channel, prev_mask_button
    #update alpha stuff
    alpha_range(alphas)
    alpha_channel = convert_to_alpha_channel(mask_img, new_scale=alpha_range(), target_size=target_size)
    prev_mask_button.image = auto_thumbnail(alpha_channel)
    prev_mask_button.config(image=prev_mask_button.image)
    debug("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" with "+str(alpha_range())+" alpha channel mask")
    
    
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
    # copy the image
    pattern_img = Image.open(path).copy()
    # resize to projector
    pattern_img = pattern_img.resize(fit_image(pattern_img, win_size=win_size()),
                                     Image.Resampling.LANCZOS)
    # make it monochrome
    pattern_img = posterize(pattern_img)
  # delete previous button
  prev_pattern_button.destroy()
  # create thumbnail version
  img = auto_thumbnail(pattern_img)
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
  img = auto_thumbnail(focus_img)
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
  img = auto_thumbnail(uv_img)
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
  update_alpha_channel(force=True)
  debug("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" with "+str(alpha_range())+" alpha channel mask")
  # delete previous button
  prev_mask_button.destroy()
  # create thumbnail version
  img = auto_thumbnail(alpha_channel)
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
def __show_img(input_image: Image.Image):
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
    update_alpha_channel()
    if(img_copy.size != alpha_channel.size):
      debug("mismatch image sizes:\npattern: "+str(img_copy.size)+"\nmask: "+str(alpha_channel.size)+"\nproj: "+str((proj.winfo_width(),proj.winfo_height())))
      assert(False)
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
  __show_img(pattern_img)
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
  __show_img(focus_img)
  debug("showing red focus pattern")
  root.update()

# show uv focusing image
def show_uv_focus():
  __show_img(uv_img)
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

