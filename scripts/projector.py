from tkinter import Tk, Label, Button, Toplevel, Entry, IntVar, Variable, filedialog
from PIL import ImageTk, Image
from time import sleep

# This code was written by Luca Garlati
# it is intended for use in Hacker Fab
# please credit on redistribution

# declare root tk object
root: Tk = Tk()

############
### Proj ###
############

# setup projector window
proj: Toplevel = Toplevel(root)
proj.title("Image Window")
proj.attributes('-fullscreen',True)
proj['background'] = '#000000'
proj.grid_columnconfigure(0, weight=1)
proj.grid_rowconfigure(0,weight=1)

# projector variables
thumbnail_size: tuple[int,int] = (160,90)
pattern_img: Image.Image = Image.new('RGB', thumbnail_size)
focus_img:   Image.Image = Image.new('RGB', thumbnail_size)
uv_img:      Image.Image = Image.new('RGB', thumbnail_size)
current_img: Label = Label()

prev_pattern_label: Label = Label()
# set new pattern image
def set_pattern(query: bool = True):
  global pattern_img
  if(query):
    # save the image
    pattern_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
    # delete previous label
    global prev_pattern_label
    prev_pattern_label.destroy()
  # create thumbnail version
  small: Image.Image = pattern_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with label
  label: Label = Label(
    root,
    image = img)
  label.image = img
  label.grid(
    row = 2,
    column = 0)
  prev_pattern_label = label

prev_focusing_label: Label = Label()
# set new pattern image
def set_focusing(query: bool = True):
  global focus_img
  if(query):
    # save the image
    focus_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
    # delete previous label
    global prev_focusing_label
    prev_focusing_label.destroy()
  # create thumbnail version
  small: Image.Image = focus_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with label
  label: Label = Label(
    root,
    image = img)
  label.image = img
  label.grid(
    row = 2,
    column = 1)
  prev_focusing_label = label

prev_uv_focus_label: Label = Label()
def set_uv_focus(query: bool = True):
  global uv_img
  if(query):
    # save the image
    uv_img = Image.open(filedialog.askopenfilename(title ='Open')).copy()
    # delete previous label
    global prev_uv_focus_label
    prev_uv_focus_label.destroy()
  # create thumbnail version
  small: Image.Image = uv_img.copy()
  small.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
  img = ImageTk.PhotoImage(small)
  # display image with label
  label: Label = Label(
    root,
    image = img)
  label.image = img
  label.grid(
    row = 2,
    column = 2)
  prev_uv_focus_label = label

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
  # create new label
  label: Label = Label(proj, image = photo, bg='black')
  label.image = photo
  label.grid(row=0,column=0,sticky="nesw")
  # label.pack(fill='both', anchor='center')
  # assign this as the current label
  current_img = label

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
root.geometry("700x200")
# don't make control window resizable
# root.resizable(width = True, height = True)

# weight all rows / cols
for row in range(3):
  root.grid_rowconfigure(row, weight=1)
for col in range(4):
  root.grid_columnconfigure(col, weight=1)
  

# show default images
set_pattern(False)
set_focusing(False)
set_uv_focus(False)

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

### second row

# import pattern image button
button: Button = Button(
  root,
  text = 'import pattern',
  command = set_pattern)
button.grid(
  row = 1,
  column = 0,
  sticky='nesw')

# import IR focusing image button
button: Button = Button(
  root,
  text = 'import red focus',
  command = set_focusing)
button.grid(
  row = 1,
  column = 1,
  sticky='nesw')

# import UV focusing image button
button: Button = Button(
  root,
  text = 'import UV focus',
  command = set_uv_focus)
button.grid(
  row = 1,
  column = 2,
  sticky='nesw')

# Show duration field
duration: Variable = IntVar()
duration.set(1000)
entry: Entry = Entry(
  root,
  textvariable = duration
)
entry.grid(
  row = 1,
  column = 3,
  sticky = 'nesw')

### third row

# pattern preview

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
  row = 2,
  column = 3,
  sticky='nesw')

root.mainloop()

