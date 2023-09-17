from tkinter import Tk, Label, Button, Toplevel, Entry, IntVar, Variable, filedialog
from PIL import ImageTk, Image
from PIL.ImageOps import grayscale
from time import sleep

# This code was written by Luca Garlati
# it is intended for use in Hacker Fab
# please credit on redistribution

# TODO:
# - auto convert images to monochrome
# - convert RGB images to alpha masks
# - auto apply alpha masks to images

# NOTE:
# is alpha mask the best option? can I just overlay greyscale

# declare root tk object
root: Tk = Tk()

def convert_to_mask(input_image: Image.Image) -> Image.Image:
  # copy the image
  mask: Image.Image = input_image.copy()
  # convert it to grayscale to normalize all values
  mask = grayscale(mask)
  # grab the red channel, since R = G = B
  (r,g,b) = mask.split()
  # return r as the mask
  return r


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
pattern_img: Image.Image = Image.new('RGB', thumbnail_size)
focus_img:   Image.Image = Image.new('RGB', thumbnail_size)
uv_img:      Image.Image = Image.new('RGB', thumbnail_size)
mask_img:    Image.Image = Image.new('RGBA', thumbnail_size, (0,0,0,0))
current_img: Button = Button()

prev_pattern_button: Button = Button()
# set new pattern image
def set_pattern(query: bool = True):
  global pattern_img
  if(query):
    # save the image
    pattern_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
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
    text = "pattern",
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
    # save the image
    focus_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
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
    text = "red focus",
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
    # save the image
    uv_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
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
    text = "UV focus",
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
  global mask_img
  if(query):
    # save the image
    mask_img = Image.open(filedialog.askopenfilename(title ='Select Pattern Image')).copy()
    # delete previous button
    global prev_mask_button
    prev_mask_button.destroy()
  # create thumbnail version
  small: Image.Image = mask_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with button
  button: Button = Button(
    root,
    image = img,
    text = "correction",
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
def __show_img(input_image: Image.Image):
  
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
  
  
  # destroy currently displayed image
  global current_img
  current_img.destroy()
  # modify image to fit window without stretch
  img_copy: Image.Image = input_image.copy()
  image = img_copy.resize(fit_image(img_copy), resample=Image.Resampling.LANCZOS)
  photo = ImageTk.PhotoImage(image)
  # create new button
  button: Button = Button(proj, image = photo, bg='black')
  button.image = photo
  button.grid(row=0,column=0,sticky="nesw")
  # assign this as the current button
  current_img = button

# private method to delete image widget, effectively clearing the proj
def __hide_img():
  current_img.destroy()
  root.update()

# do the patterning
def begin_patterning():
  global is_patterning
  # prepare for patterning
  pattern_button.configure(bg="black")
  __show_img(pattern_img)
  # begin
  root.update()
  sleep(duration.get() / 1000)
  # clean up
  __hide_img()
  pattern_button.configure(bg="red")
  root.update()

# show patterning image
def show_focusing():
  __show_img(focus_img)
  root.update()

# show uv focusing image
def show_uv_focus():
  __show_img(uv_img)
  root.update()

###########
### GUI ###
###########

# setup GUI
root.title("Control Window")
root.geometry("800x200")
# don't make control window resizable
# root.resizable(width = True, height = True)

# weight all rows / cols
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=2)
for col in range(4):
  root.grid_columnconfigure(col, weight=1)
  

# show default images
set_pattern(False)
set_focusing(False)
set_uv_focus(False)
set_mask(False)

### first row ###

# clear images button
button: Button = Button(
  root,
  text = 'clear',
  command = __hide_img,
  bg = 'black',
  fg = 'white')
button.grid(
  row = 0,
  column = 0,
  sticky='nesw')

# Show IR focusing image button
button: Button = Button(
  root,
  text = 'show red focus',
  command = show_focusing)
button.grid(
  row = 0,
  column = 1,
  sticky='nesw')

# Show UV focusing image button
button: Button = Button(
  root,
  text = 'show UV focus',
  command = show_uv_focus)
button.grid(
  row = 0,
  column = 2,
  sticky='nesw')

# show "duration (ms)" text
text: Label = Label(
  root,
  text="duration (ms)"
)
text.grid(
  row = 0,
  column = 3,
  sticky='nesw')

# Show duration field
duration: Variable = IntVar()
duration.set(1000)
entry: Entry = Entry(
  root,
  textvariable = duration
)
entry.grid(
  row = 0,
  column = 4,
  sticky = 'nesw')

### second row

# pattern preview

# mask preview

# IR focus preview

# UV focus preview

# pattern the selected image
pattern_button: Button = Button(
  root,
  text = 'begin\npatterning',
  command = begin_patterning,
  bg = 'red',
  fg = 'white')
pattern_button.grid(
  row = 1,
  column = 4,
  sticky='nesw')


root.mainloop()

