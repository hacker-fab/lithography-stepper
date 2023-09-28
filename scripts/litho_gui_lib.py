from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label
from PIL import ImageTk, Image
from time import sleep
from os.path import basename
from types import FunctionType

# window to display info, errors, warning, and text
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
