from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from PIL.ImageOps import grayscale, invert
from time import sleep, time
from os.path import basename

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

# declare root tk object
root: Tk = Tk()
# v1    working initial prototype
# v2    added UV focus image option
#   .1  major UI overhaul
#   .2  added debug printouts
# v3    brightness correction implemented
root.title("Litho V2.3")

# Text box at the bottom
debug: Label = Label(
  root,
  text = "test",
  justify = 'left',
  anchor = 'w'
)
debug.grid(
  row = 2,
  column = 0,
  columnspan = 4,
  sticky='nesw'
)

def show_debug(text: str):
  debug.config(text = text+"\nMade by Luca Garlati")
  root.update()


###############
### masking ###
###############

# returns an alpha channel mask equivalent from source image
def convert_to_alpha_channel(input_image: Image.Image) -> Image.Image:  #rescale pixel brightness
  def rescale(scale_old: tuple[int,int], scale_new: tuple[int,int], value: int) -> int:
    if(scale_old[0] == scale_old[1]):
      if(value == scale_old[0]):
        return scale_new[0]
      else:
        print("internal error: errno 3")
        show_debug("internal error: errno 3")
        return -1
    if(scale_old[0] < scale_old[1]):
      print("internal error: errno 0")
      show_debug("internal error: errno 0")
      return -1
    if(scale_new[0] <= scale_new[1]):
      print("internal error: errno 1")
      show_debug("internal error: errno 1")
      return -1
    # get % into the scale
    d = (value - scale_old[1]) / (scale_old[0] - scale_old[1])
    # convert to float in second scale
    return round((d * (scale_new[0]-scale_new[1])) + scale_new[1])
    
  global max_alpha
  #check max alpha
  if (max_alpha.get() < 0):
    show_debug("alpha = "+str(max_alpha.get())+" < 0, aborting")
    return Image.Image()
  elif (max_alpha.get() > 255):
    show_debug("alpha = "+str(max_alpha.get())+" > 255, aborting")
    return Image.Image()
  # copy the image
  mask: Image.Image = input_image.copy()
  # convert it to grayscale to normalize all values
  mask = mask.convert("L")
  # Invert all colors since we want the mask, not the image itself
  mask = invert(mask)
  # Normalize the values to be up to max alpha
  # first step is getting brightest and darkest pixel values
  duration:int = int(time())
  show_debug("Parsing ("+str(mask.width)+","+str(mask.height)+") mask...")
  brightness: list[int] = [0,255]
  for col in range(mask.width):
    for row in range(mask.height):
      # get single-value brightness since it's grayscale
      pixel = mask.getpixel((col, row))
      if pixel < brightness[1]:
        brightness[1] = pixel
      if pixel > brightness[0]:
        brightness[0] = pixel
  # now rescale each pixel
  show_debug("Generating ("+str(mask.width)+","+str(mask.height)+") alpha channel...")
  for col in range(mask.width):
    for row in range(mask.height):
      mask.putpixel((col,row), rescale((brightness[0],brightness[1]),
                                       (max_alpha.get(), 0), 
                                       mask.getpixel((col,row))))
  show_debug("finshed building mask in "+str(int(time())-duration)+" seconds")
  # now mask is finally done
  return mask

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
current_img:   Label = Label()
alpha_channel: Image.Image

prev_pattern_button: Button = Button()
# set new pattern image
def set_pattern(query: bool = True):
  global pattern_img
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      show_debug("Pattern import cancelled")
    else:
      show_debug("Pattern set to "+basename(path))
    # save the image
    pattern_img = Image.open(path).copy()
    # delete previous button
    global prev_pattern_button
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
  global focus_img
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      show_debug("Red focus import cancelled")
    else:
      show_debug("Red focus set to "+basename(path))
    # save the image
    focus_img = Image.open(path).copy()
    # delete previous button
    global prev_focusing_button
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
  global uv_img
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      show_debug("UV focus import cancelled")
    else:
      show_debug("UV focus set to "+basename(path))
    # save the image
    uv_img = Image.open(path).copy()
    # delete previous button
    global prev_uv_focus_button
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
  global mask_img, alpha_channel, prev_mask_button
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      show_debug("Correction image import cancelled")
    else:
      show_debug("Correction image set to "+basename(path))
    # save the image
    mask_img = Image.open(path).copy()
  # generate alpha channel mask
  alpha_channel = convert_to_alpha_channel(mask_img)
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
  
  # return max image size that will fit in window without cropping
  def fit_image(image: Image.Image) -> tuple[int,int]:
    # for easier access
    win_size: tuple[int,int] = (proj.winfo_width(), proj.winfo_height())
    img_size: tuple[int,int] = (image.width, image.height)
    #determine orientation to fit to
    if (img_size[0] / img_size[1]) < (win_size[0] / win_size[1]):
      # fit to height
      return (int(img_size[0] * (win_size[1] / img_size[1])), win_size[1])
    elif (img_size[0] / img_size[1]) > (win_size[0] / win_size[1]):
      # fit to width
      ratio = (win_size[1] / img_size[1])
      return (win_size[0],int(img_size[1] * (win_size[0] / img_size[0])))
    else:
      # same ratio
      return win_size
  
  # return min image size that will fill in window
  def fill_image(image: Image.Image) -> tuple[int,int]:
    # for easier access
    win_size: tuple[int,int] = (proj.winfo_width(), proj.winfo_height())
    img_size: tuple[int,int] = (image.width, image.height)
    # determine orientation to fit to
    if (img_size[0] / img_size[1]) < (win_size[0] / win_size[1]):
      # fit to height
      return (int(img_size[0] * (win_size[1] / img_size[1])), win_size[1])
    elif (img_size[0] / img_size[1]) > (win_size[0] / win_size[1]):
      # fit to width
      ratio = (win_size[1] / img_size[1])
      return (win_size[0],int(img_size[1] * (win_size[0] / img_size[0])))
    else:
      # same ratio
      return win_size

  # destroy currently displayed image
  global current_img
  current_img.destroy()
  # modify image to fit window without stretch
  img_copy: Image.Image = input_image.copy()
  new_size: tuple[int,int] = fit_image(img_copy)
  image = img_copy.resize(new_size, resample=Image.Resampling.LANCZOS)
  if(use_mask):
    # resize alpha mask
    mask = alpha_channel.resize(fit_image(alpha_channel), resample=Image.Resampling.LANCZOS)
    # putalpha requires alpha channel to be same size as original image
    # so we need to crop accordingly (left,top,right,bottom)
    diff: int = mask.width - image.width
    if(diff < 0):
      # if alpha channel is taller than image, abort
      print("internal error: errno 2")
      show_debug("internal error: errno 2")
      return
    left: int = (diff//2)
    right: int = image.width - (diff//2)
    # image sizes need to match exactly, so if odd, add 1 to right
    if(diff % 2 == 1):
      right += 1
    mask = mask.crop((left, 0, right, mask.height))
    # finally, apply alpha mask
    image.putalpha(mask)
  photo = ImageTk.PhotoImage(image)
  # create new button
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
    show_debug("duration = "+str(duration.get())+" < 0, aborting")
    return
  # prepare for patterning
  global is_patterning
  show_debug("Patterning for "+str(duration.get())+"ms at "+str(max_alpha.get())+" alpha...")
  pattern_button.configure(bg="black")
  __show_img(pattern_img, use_mask=True)
  # begin
  root.update()
  sleep(duration.get() / 1000)
  # clean up
  __hide_img()
  pattern_button.configure(bg="red")
  root.update()
  show_debug("Finished patterning")

# show patterning image
def show_focusing():
  __show_img(focus_img)
  show_debug("showing red focus pattern")
  root.update()

# show uv focusing image
def show_uv_focus():
  __show_img(uv_img)
  show_debug("showing uv focus pattern")
  root.update()

# wrapper for clear button
def clear_image():
  __hide_img()
  show_debug("Projector cleared")

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



show_debug("Debug info will be displayed here.")
root.mainloop()

