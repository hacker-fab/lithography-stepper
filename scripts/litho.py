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

# declare root tk object
root: Tk = Tk()
# v1    working initial prototype
# v2    added UV focus image option
#   .1  major UI overhaul
#   .2  added debug printouts
#   .3  transferred image utils to separate lib
#   .4  working alpha mask
#   .5  several minor code optimizations
# v3    brightness correction implemented
root.title("Litho V2.4")

# Text box at the bottom
debug_widget: Label = Label(
  root,
  text = "test",
  justify = 'left',
  anchor = 'w'
)
debug_widget.grid(
  row = 2,
  column = 0,
  columnspan = 4,
  sticky='nesw'
)

def debug(text: str):
  debug_widget.config(text = text+"\nMade by Luca Garlati")
  print(text)
  root.update()


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
pattern_img:   Image.Image = Image.new('RGBA', thumbnail_size, (255,255,255,255))
focus_img:     Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
uv_img:        Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,255))
mask_img:      Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,0))
alpha_channel: Image.Image
current_img:   Label = Label()

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
    pattern_img = pattern_img.resize(fit_image())
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
    row = 1,
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
    row = 1,
    column = 2,
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
    row = 1,
    column = 3,
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
  alpha_channel = convert_to_alpha_channel(mask_img, new_scale=(max_alpha.get(), 0), target_size=(proj.winfo_width(), proj.winfo_height()))
  debug("finished building "+str(proj.winfo_width())+"x"+str(proj.winfo_height())+" alpha channel mask")
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
    row = 1,
    column = 1,
    sticky='nesw')
  prev_mask_button = button

# private method to show an image on the projection window
max_alpha: Variable = IntVar()
max_alpha.set(255)
def __show_img(input_image: Image.Image, use_mask:bool = False):
  # setup
  window_size: tuple[int,int] = (proj.winfo_width(), proj.winfo_height())
  img_copy: Image.Image = input_image.copy()
  # destroy currently displayed image
  global current_img
  current_img.destroy()
  # resample if image isn't correct size
  if(img_copy.width != window_size[0] or
     img_copy.height != window_size[1]):
    debug("resampling image...")
    img_copy = img_copy.resize(fit_image(img_copy, window_size), Image.Resampling.LANCZOS)
  # apply alpha mask if enabled
  if(use_mask):
    img_copy.putalpha(alpha_channel)
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
  debug("Patterning for "+str(duration.get())+"ms...")
  pattern_button.configure(bg="black")
  __show_img(pattern_img, use_mask=True)
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
root.geometry("800x200")
# don't make control window resizable
# root.resizable(width = True, height = True)

# weight all rows / cols
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=3)
root.grid_rowconfigure(0, weight=1)
for col in range(4):
  root.grid_columnconfigure(col, weight=1)
  
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
  column = 0,
  sticky='nesw')

# Show max_alpha field
entry: Entry = Entry(
  root,
  textvariable = max_alpha,
  justify = 'center'
)
entry.grid(
  row = 0,
  column = 1,
  sticky = 'nesw')

# Show IR focusing image button
button: Button = Button(
  root,
  text = 'show red focus',
  command = show_focusing)
button.grid(
  row = 0,
  column = 2,
  sticky='nesw')

# Show UV focusing image button
button: Button = Button(
  root,
  text = 'show UV focus',
  command = show_uv_focus)
button.grid(
  row = 0,
  column = 3,
  sticky='nesw')

# Show duration field
duration: Variable = IntVar()
duration.set(1000)
entry: Entry = Entry(
  root,
  textvariable = duration,
  justify = 'center'
)
entry.grid(
  row = 0,
  column = 4,
  sticky = 'nesw')

# pattern the selected image
pattern_button: Button = Button(
  root,
  text = 'begin\npatterning',
  command = begin_patterning,
  bg = 'red',
  fg = 'white')
pattern_button.grid(
  row = 1,
  rowspan = 2,
  column = 4,
  sticky='nesw')



debug("Debug info will be displayed here.")
root.mainloop()

