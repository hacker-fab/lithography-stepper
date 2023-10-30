from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label, Widget
from PIL import ImageTk, Image
from time import time
from os.path import basename
from types import FunctionType
from litho_img_lib import *
from typing import Callable, Literal


# TODO
# auto thumbnail size based on widget dimentions
# update thumbnail widget instead of rebuilding it
# Overarching GUI class
# Projector class? or something?
# Better to detect when a processed image actually needs updating
# check if resizing of thumbnails skip works

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
    
  # show error in the debug widget
  def error(self, text:str):
    self.widget.config(text = text)
    self.__set_color__(self.err_color)
    print("e "+text)
  
  # place widget on the grid
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")
    
  # set the text and background color
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
  func_high: Callable | None
  func_low: Callable | None
  func_always: Callable | None
  
  # create new Toggle widget
  def __init__(self, root: Tk,
               text: tuple[str,str], 
               colors: tuple[str,str] = ("black", "white"), 
               initial_state:bool=False,
               debug: Debug | None = None,
               func_on_true: Callable | None = None,
               func_on_false: Callable | None = None,
               func: Callable | None = None):
    # set fields
    self.text = text
    self.colors = colors
    self.state = initial_state
    self.debug = debug
    self.func_high = func_on_true
    self.func_low = func_on_false
    self.func_always = func
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
    if(self.func_always != None):
      self.func_always()
  
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

# creates thumbnail / image import widget
class Thumbnail():
  widget: Button
  # image stuff
  image: Image.Image
  thumb_size: tuple[int, int]
  # optional fields
  text: str
  debug: Debug | None
  accept_alpha: bool
  func_on_success: Callable | None
  # set to a copy of a new image upon import
  # useful to store a modified version of the original image
  temp_image: Image.Image
  
  def __init__(self, root: Tk,
               thumb_size: tuple[int,int],
               text: str = "",
               debug: Debug | None = None,
               accept_alpha: bool = False,
               func_on_success: Callable | None = None):
    # assign vars
    self.thumb_size = thumb_size
    self.text = text
    self.debug = debug
    self.accept_alpha = accept_alpha
    self.func_on_success = func_on_success
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
      if(path[-4] != "." or not (path[-3:] == "jpg" or path[-3:] == "png")):
        self.debug.error(self.text+" invalid file type: "+path[-3:])
        return
      else:
        self.debug.info(self.text+" set to "+basename(path))
    img = Image.open(path)
    if(self.accept_alpha):
      self.image = img.copy()
    else:
      # ensure image is RGB or L
      match img.mode:
        case "RGB":
          self.image = img.copy()
        case "L":
          self.image = img.copy()
        case "RGBA":
          self.image = RGBA_to_RGB(img)
          if(self.debug != None):
            self.debug.warn("RGBA images are not permitted, auto converted to RGB")
        case "LA":
          self.image = LA_to_L(img)
          if(self.debug != None):
            self.debug.warn("LA images are not permitted, auto converted to L")
        case _:
          if(self.debug != None):
            self.debug.error("Invalid image mode: "+img.mode)
          return
    # update temp
    self.temp_image = self.image.copy()
    # update
    self.update_thumbnail(self.image)
    # call optional func if specified
    if(self.func_on_success != None):
      self.func_on_success()
    
  # update the thumbnail, but not original image
  def update_thumbnail(self, new_image: Image.Image):
    new_size: tuple[int, int] = fit_image(new_image, win_size=self.thumb_size)
    if(new_size != new_image.size):
      thumb_img = new_image.resize(new_size, Image.Resampling.LANCZOS)
    else:
      thumb_img = new_image
    photoImage = rasterize(thumb_img)
    self.widget.config(image = photoImage)
    self.widget.image = photoImage
    
  # place widget on the grid
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")

#TODO add a recall / changed function for regenerating masks and stuff
# creates a better int input field
class Intput():
  widget: Entry
  var: Variable
  # user fields
  min: int | None
  max: int | None
  debug: Debug | None
  name: str
  invalid_color: str
  # revert displayed value to last valid value if invalid?
  auto_fix: bool
  # optional validation function, true if input is valid
  extra_validation: Callable[[int], bool] | None
  # the value that will be returned: always valid
  __value__: int
  # value checked by changed()
  last_diff: int
  
  def __init__( self,
                root: Tk,
                name: str = "Intput",
                default: int = 0,
                min: int | None = None,
                max: int | None = None,
                debug: Debug | None = None,
                justify: Literal['left', 'center', 'right'] = "center",
                extra_validation: Callable[[int], bool] | None = None,
                auto_fix: bool = True,
                invalid_color: str = "red"
                ):
    # store user inputs
    self.min = min
    self.max = max
    self.debug = debug
    self.extra_validation = extra_validation
    self.auto_fix = auto_fix
    self.name = name
    self.invalid_color = invalid_color
    # setup var
    self.var = IntVar()
    self.var.set(default)
    self.value = self.min
    self.last_diff = default
    # setup widget
    self.widget = Entry(root,
                        textvariable = self.var,
                        justify=justify
                        )
    # update
    self.__update__()
  
  # place widget on the grid
  def grid(self, row, col, colspan = 1, rowspan = 1):
    self.widget.grid(row = row,
                     column = col,
                     rowspan = rowspan,
                     columnspan = colspan,
                     sticky = "nesw")

  # get the more recent vaid value
  def get(self, update: bool = True) -> int:
    if(update):
      self.__update__()
    return self.__value__
  
  
  # try and set a new value
  def set(self, user_value: int):
    self.__update__(user_value)
  
  # has the value changed since the last time this method was called
  def changed(self) -> bool:
    if(self.get() != self.last_diff):
      self.last_diff = self.get()
      return True
    return False
    
  
  # updates widget and value
  def __update__(self, new_value: int | None = None):
    # get new potential value
    new_val: int
    if(new_value == None):
      new_val = self.var.get()
    else:
      new_val = new_value
    # validate and update accordingly
    if(self.__validate__(new_val)):
      self.__value__ = new_val
      self.widget.config(bg="white")
    else:
      if(self.auto_fix):
        self.var.set(self.__value__)
      else:
        self.widget.config(bg=self.invalid_color)
      if(self.debug != None):
        self.debug.error("Invalid value for "+self.name+": "+str(new_val))
    self.widget.update()
    
  # check if the current value is valid
  def __validate__(self, new_val: int) -> bool:
    # check min / max
    if(self.min != None and new_val < self.min):
      return False
    if(self.max != None and new_val > self.max):
      return False
    # check extra validation
    if(self.extra_validation != None and not self.extra_validation(new_val)):
      return False
    # passed all checks
    return True
    

# TODO Test this
# creates a fullscreen window and displays specified images to it
class Projector_Controller():
  ### Internal Fields ###
  __TL__: Toplevel
  __label__: Label
  __root__: Tk
  # just a black image to clear with
  __clearImage__: ImageTk.PhotoImage
  ### optional user args ###
  debug: Debug | None
  
  def __init__( self,
                root: Tk,
                title: str = "Projector",
                background: str = "#000000",
                debug: Debug | None = None
                ):
    # store user inputs
    self.title = title
    self.__root__ = root
    self.debug = debug
    # setup projector window
    self.__TL__ = Toplevel(root)
    self.__TL__.title(self.title)
    self.__TL__.attributes('-fullscreen',True)
    self.__TL__['background'] = background
    self.__TL__.grid_columnconfigure(0, weight=1)
    self.__TL__.grid_rowconfigure(0, weight=1)
    # create projection Label
    self.__label__ = Label(self.__TL__, bg='black')
    self.__label__.grid(row=0,column=0,sticky="nesw")
    # generate dummy black image
    self.__clearImage__ = rasterize(Image.new("L", self.size())) 
    self.update()
    
  # show an image
  # if a duration is specified, show the image for that many milliseconds
  def show(self, image: Image.Image, duration: int = 0):
    img_copy: Image.Image = image.copy()
    # warn if image isn't correct size
    if(img_copy.size != fit_image(img_copy, self.size())):
      if(self.debug != None):
        self.debug.warn("projecting image with incorrect size")
    photo: ImageTk.PhotoImage = rasterize(img_copy)
    self.__label__.config(image = photo)
    self.__label__.image = photo
    if(duration > 0):
      # prepare end in two steps for a more accurate duration
      end: float = duration / 1000
      end += time()
      # update and begin
      self.update()
      while(time() < end):
        pass
      self.clear()
    else:
      self.update()
  
  # clear the projector window
  def clear(self):
    self.__label__.config(image = self.__clearImage__)
    self.__label__.image = self.__clearImage__
    self.update()

  # get size of projector window
  def size(self, update: bool = True) -> tuple[int,int]:
    if(update): self.update()
    return (self.__TL__.winfo_width(), self.__TL__.winfo_height())
  
  def update(self):
    self.__root__.update()
    self.__TL__.update()


# TODO add row and col weighting
# TODO auto debug widget creation and application to children
# GUI controller and widget manager
class GUI_Controller():
  #region: fields
  ### Internal Fields ###
  root: Tk
  __widgets__: dict[str, Widget | Toggle | Thumbnail | Intput]
  ### User Fields ###
  # Mandatory
  grid_size: tuple[int,int]
  # Optional
  title: str
  window_size: tuple[int,int]
  resizeable: bool
  debug: Debug | None
  proj: Projector_Controller
  #endregion
  
  def __init__( self,
                grid_size: tuple[int,int],
                window_size: tuple[int,int] = (900, 220),
                title: str = "GUI Controller",
                resizeable: bool = True
                ):
    # store user input variables
    self.grid_size = grid_size
    self.window_size = window_size
    self.title = title
    self.resizeable = resizeable
    # setup root / gui window
    self.root = Tk()
    self.root.title(self.title)
    self.root.geometry(str(self.window_size[0])+"x"+str(self.window_size[1]))
    self.root.resizable(width = self.resizeable, height = self.resizeable)
    for row in range(self.grid_size[0]):
      self.root.grid_rowconfigure(row, weight=1)
    for col in range(self.grid_size[1]):
      self.root.grid_columnconfigure(col, weight=1)
    # create projector window
    self.proj = Projector_Controller(self.root)
    # create dictionary of widgets
    self.__widgets__ = {}

  #region: widget management
  #TODO test if typing like this actually works
  def add_widget(self, name: str, widget: Widget | Toggle | Thumbnail | Debug | Intput):
    # if a debug widget is added, save it as the debug field
    if(type(widget) == Debug):
      self.debug = widget
      self.proj.debug = widget
    else:
      self.__widgets__[name] = widget
    self.update()
      
  # return widget by name, or None if not found
  def get_widget(self, name: str) -> Widget | Toggle | Thumbnail | Debug | Intput | None:
    return self.__widgets__.get(name, None)
  
  # remove widget by name
  def del_widget(self, name: str):
    # remove widget from dictionary
    widget = self.__widgets__.pop(name, None)
    # check if widget was found
    if(widget == None):
      if(self.debug != None):
        self.debug.warn("Tried to remove widget "+name+" but it was not found")
      return
    # report success
    self.debug.info("Removed widget "+name)
    self.update()
  #endregion
  
  # update the GUI window  
  def update(self):
    self.root.update()
  
  def mainloop(self):
    self.root.mainloop()
  

  
  
  