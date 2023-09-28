from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from types import FunctionType
from litho_img_lib import *

# TODO
# auto thumbnail size based on widget dimentions
# update thumbnail widget instead of rebuilding it

# widget to display info, errors, warning, and text
class Debug():
  widget: Label
  text_color: tuple[str, str]
  warn_color: tuple[str, str]
  err_color:  tuple[str, str]
  
  # create new widget
  def __init__(self, root: Tk,
               text_color: tuple[str, str] = ("black", "white"),
               warn_color: tuple[str, str] = ("black", "orange"),
               err_color:  tuple[str, str] = ("white", "red")):
    self.text_color = text_color
    self.warn_color = warn_color
    self.err_color = err_color
    self.widget = Label(
      root,
      justify = "left",
      anchor = "w"
    )
    self.__set_color__(text_color)
  
  # show text in the debug widget
  def info(self, text:str):
    self.widget.config(text = text)
    self.__set_color__(self.text_color)
    print("i "+text)
  
  # show warning in the debug widget
  def warn(self, text:str):
    self.widget.config(text = text)
    self.__set_color__(self.warn_color)
    print("w "+text)
    
  #show error in the debug widget
  def error(self, text:str):
    self.widget.config(text = text)
    self.__set_color__(self.err_color)
    print("e "+text)
  
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")
    
  def __set_color__(self, colors: tuple[str,str]):
    self.widget.config(fg = colors[0],
                       bg = colors[1])

# creates toggle widget
class Toggle():
  # mandatory / main fields
  widget: Button
  state: bool
  
  # user-inputted fields
  text: tuple[str,str]
  colors: tuple[str,str]
  debug: Debug | None
  func_high: FunctionType | None
  func_low: FunctionType | None
  
  # create new Toggle widget
  def __init__(self, root: Tk,
               text: tuple[str,str], 
               colors: tuple[str,str] = ("black", "white"), 
               initial_state:bool=False,
               debug: Debug | None = None,
               func_on_true: FunctionType | None = None,
               func_on_false: FunctionType | None = None):
    # set fields
    self.text = text
    self.colors = colors
    self.state = initial_state
    self.debug = debug
    self.func_high = func_on_true
    self.func_low = func_on_false
    # create button widget
    self.widget = Button(root, command=self.toggle)
    # update to reflect default state
    self.__update__()
  
  # place widget on the grid
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")
  
  # toggle the state and update widget
  # optionally specify function to call when pressed
  def toggle(self, func = None):
    self.state = not self.state
    self.__update__()
    if(self.state and self.func_high != None):
      self.func_high()
    if(not self.state and self.func_low != None):
      self.func_low()
  
  # update widget to reflect current state
  def __update__(self):
    if(self.state):
      self.widget.config( fg = self.colors[1],
                          bg = self.colors[0],
                          text = self.text[0])
      if(self.debug != None):
        self.debug.info(self.text[0])
    else:
      self.widget.config( fg = self.colors[0],
                          bg = self.colors[1],
                          text = self.text[1])
      if(self.debug != None):
        self.debug.info(self.text[1])

"""
### please kill me, existance is suffering
prev_focusing_button: Button = Button()
def set_focusing(query: bool = True):
  global focus_img, prev_focusing_button
  if(query):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(path == ''):
      debug.warn("Red focus import cancelled")
    else:
      debug.info("Red focus set to "+basename(path))
    # save the image
    focus_img = (Image.open(path)).copy()
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
  
  # makes a photo thumbnail copy at specified size
  def auto_thumbnail(image: Image.Image, size: tuple[int,int] = thumbnail_size) -> ImageTk.PhotoImage:
    thumb: Image.Image = image.copy()
    thumb.thumbnail(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(thumb)
### stop the genocide, enough has been lost 
"""


# creates thumbnail / image import widget
class Thumbnail():
  widget: Button
  # image stuff
  image: Image.Image
  thumb_size: tuple[int, int]
  # optional fields
  text: str
  debug: Debug | None
  
  def __init__(self, root: Tk,
               thumb_size: tuple[int,int],
               text: str = "",
               debug: Debug | None = None):
    # assign vars
    self.thumb_size = thumb_size
    self.text = text
    self.debug = debug
    # build widget
    button: Button = Button(
      root,
      command = self.__import_image__
      )
    if(self.text != ""):
      button.config(text = self.text,
                    compound = "top")
    self.widget = button
    # create placeholder images
    placeholder = Image.new("RGB", self.thumb_size)
    self.image = placeholder
    self.update_thumbnail(placeholder)
  
  # prompt user for a new image
  def __import_image__(self):
    # get image
    path: str = filedialog.askopenfilename(title ='Open')
    if(self.debug != None):
      if(path == ''):
        self.debug.warn(self.text+" import cancelled")
      else:
        self.debug.info(self.text+" set to "+basename(path))
    # save the image
    self.image = (Image.open(path)).copy()
    # update thumbnail
    self.update_thumbnail(self.image)
    
  # update the thumbnail, but not original image
  def update_thumbnail(self, new_image: Image.Image):
    thumb_img = new_image.resize(fit_image(self.image, win_size=self.thumb_size), Image.Resampling.LANCZOS)
    photoImage = ImageTk.PhotoImage(thumb_img)
    self.widget.config(image = photoImage)
    self.widget.image = photoImage
    
  # place widget on the grid
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")
  

  