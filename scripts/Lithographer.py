from tkinter import Tk, Button, Toplevel, Entry, IntVar, Variable, filedialog, Label, Text
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
from litho_img_lib import *
from litho_gui_lib import *

# TODO
# - spot for "entire layer" image
# - spot for "current tile" image
# - update the help message to include stage stuff
# - add a progress bar for total progress (tiles left / total tiles)
# - make camera (and thumbnails ideally) auto resize images / have images fill the widget
# - make the big red "begin patterning" button change color while patterning
# - when a tile of the pattern is finished, change it back to red and say "override"
# - add pause when tiling to allow cv to move around
# 
# Low Priority
# - an image showing live camera output (I'll just set the image and it will update basically)
# - CLI
# - add a button to show pure white image for flatfield correction
# - fix bug where flatfield pattern is reapplied on second pattern show
#     to reproduce, import flatfield and pattern, enable posterize and flatfield, press show twice
# - refactor widgets to be organized by category. see stage controls
# - refactor grid location to be based off category offsets instead of asbolute for easier moving
#     of widget groups. see stage controls
# - Make an interactive version of the help message popup, it's getting long
# - make the "show" buttons change color while that pattern is being showed
# - add secondary list in this file to store the modified tiled images similar to the "temp" and
#     "original" images in the thumbnail widgets

''' V1.3.1 Patch Notes

**Major**
- Implemented slicer and stepping
 - The main slicing code is a standalone function in litho_img_lib, it's **very** feature rich and robust
 - implemented a class to allow for easier stepping through the slices
 - integrated this with the rest of the GUI, this was _very_ hard
**Minor**
- Keyboard Input for moving stage
 - Can now move stage with the arrow keys: up/down/left/right for xy and ctrl or shift + up/down for z axis
- Yet another large layout redesign
- backend refactoring
- abort button is dynamic now
- added a progress bar for the total progress of the pattern

**For V2.0.0**
- Add live camera feed
- Integrate with CV

**Nerd Stuff**
- Refactored the widgets to be organized by category.
 - This is significantly easier to move and modify the layout of the full UI

'''


THUMBNAIL_SIZE: tuple[int,int] = (160,90)
CHIN_SIZE: int = 400
GUI: GUI_Controller = GUI_Controller(grid_size = (14,10),
                                     title = "Lithographer V1.2.5",
                                     add_window_size=(0,CHIN_SIZE))
SPACER_SIZE: int = GUI.window_size[0]//(GUI.grid_size[1]*5)
# for row in range(GUI.grid_size[0]):
#   GUI.root.grid_rowconfigure(row, minsize=CHIN_SIZE//(GUI.grid_size[0]-2))
# Debugger
debug: Debug = Debug(root=GUI.root)
GUI.add_widget("debug", debug)


#region: functions

slicer: Slicer = Slicer(output_resolution=GUI.proj.size(),
                        tiling_pattern='snake',
                        debug=debug)

#returns modified version of input image, optionally updates thumbnail with image
def prep_pattern(input_image: Image.Image, thumb: Thumbnail | None = None) -> Image.Image:
  image = input_image.copy()
  def update_thumb() -> None:
    if(thumb != None):
      thumb.temp_image = image
      thumb.update_thumbnail(image)
      
  # posterizeing
  if(posterize_toggle.state and ((not (image.mode == 'L' or image.mode == 'LA')) or post_strength_intput.changed())):
    # posterizing enabled, and image isn't poterized
    debug.info("Posterizing...")
    image = posterize(image, round((post_strength_intput.get()*255)/100))
  elif(not posterize_toggle.state and (image.mode == 'L' or image.mode == 'LA') and thumb != None):
    # posterizing disabled, but image is posterized
      debug.info("Resetting Posterizing...")
      thumb.temp_image = thumb.image
      thumb.update_thumbnail(thumb.image)
      image = thumb.image
  
  # flatfield correction
  if(flatfield_toggle.state and (image.mode == 'L' or image.mode == 'RGB' or 
     FF_strength_intput.changed())):
    debug.info("Applying flatfield corretion...")
    alpha_channel = convert_to_alpha_channel(flatfield_thumb.image,
                                             new_scale=dec_to_alpha(FF_strength_intput.get()),
                                             target_size=image.size,
                                             downsample_target=540)
    image.putalpha(alpha_channel)
  elif(not flatfield_toggle.state):
    if(image.mode == 'RGBA' and thumb != None):
      debug.info("Removing flatfield corretion...")
      thumb.temp_image = RGBA_to_RGB(thumb.temp_image)
      thumb.update_thumbnail(thumb.temp_image)
      image = thumb.image
    if(image.mode == 'LA' and thumb != None):
      debug.info("Removing flatfield corretion...")
      thumb.temp_image = LA_to_L(thumb.temp_image)
      thumb.update_thumbnail(thumb.temp_image)
      image = thumb.image
      
  # resizeing
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing...")
    image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  
  update_thumb()
  return image

#endregion

#region: Camera and progress bars
camera_placeholder = rasterize(Image.new('RGB', (GUI.window_size[0],(GUI.window_size[0]*9)//16), (0,0,0)))
camera: Label = Label(
  GUI.root,
  image=camera_placeholder
  )
camera.grid(
  row = 0,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.add_widget("camera", camera)

# overall pattern progress bar
pattern_progress: Progressbar = Progressbar(
  GUI.root,
  orient='horizontal',
  mode='determinate',
  )
pattern_progress.grid(
  row = 1,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.add_widget("pattern_progress", pattern_progress)

# Current exposure Progress
exposure_progress: Progressbar = Progressbar(
  GUI.root,
  orient='horizontal',
  mode='determinate',
  )
exposure_progress.grid(
  row = 2,
  column = 0,
  columnspan = GUI.grid_size[1],
  sticky='nesw')
GUI.proj.progressbar = exposure_progress
GUI.add_widget("exposure_progress", exposure_progress)

#endregion

#region: Debug and Help 
# the debug widget needs to be added immedaitely, so this is all that needs to be here
debug.grid(GUI.grid_size[0]-1,0,colspan=GUI.grid_size[1]-1)

help_text: str = """
How do I import an image?
- Just click on the black thumbnail and a dialog will open
  - The UI will try to fix images in the incorrect mode
  - The UI will reject incorrect file formats


How do I move the projector window?
- On Windows, click the projector window, then win + shift + arrow keys to move it to the second screen 
- On Mac, no clue :P


How do I use flatfield correction?
1. Take a flatfield image
  - Set the projector to UV mode
  - Display a fully white image on the projector
  - Put a clean blank chip under the projector
  - Take a snapshot with the amscope camera (1080p is plenty)
  - Crop out any black borders if present
2. Import the flatfield image
  - Just click on the flatfield image preview thumbnial
  - The UI will automatically guess the correct correction intensity to use 
3. Make sure flatfield correction is enabled
  - press the "use flatfield" button to toggle it
4. Done, though some things to note
  - Flatfield correction will only be applied to the pattern, not red or uv focus
  - The intensity of the correction is normalized from 0 to 100 for your convenience:
    - 0   means no correction, ie completely transparent
    - 50  means the correction is applied at full strength, from pure black pixels to pure white
    - 100 means max correction, ie completely opaque


Posterizer? I barely know her!
- TL;DR, make pattern monochrome for sharper edges
- What is posterizing?
  - Posterizing is the process for reducing the bit depth of an image.
  - For this GUI, it reduces the image to 1 bit depth or monochrome (not greyscale, only pure black and pure white)
- What is that number next to it?
  - The number next to the toggle is the cutoff value
  - Unless you're losing features or lines are growing / shrinking, leave it at 50
  - It behaves as follows:
    - 100 is max cutoff, so only pure white will stay white
    -  50 is default, light greys will be white, and dark greys will be black
    -   0 is min cutoff, so only pure black will stay black
- What does this apply to?
  - Patterning image
  - Red focus image
  - NOT UV focus image because it would just be solid black
- What does it actually do?
  - It makes all edges in the image perfectly sharp, improving the quality of the patterning.
  - It's unlikely, but you may not need to use it if:
    - Your pattern is RGB or L, and doesn't have an alpha channel
    - Your pattern is already monochrome
    - Your pattern is at exactly the projector's resolution. can't be even a single pixel off
- What does this apply to?
  - Patterning image
  - Red focus image
  - NOT UV focus image because it would just be solid black


Think something is missing? Have a suggestion?
see our website for contact methods:
http://hackerfab.ece.cmu.edu


This tool was made by Luca Garlati for Hackerfab
"""
help_popup: TextPopup = TextPopup(
  root=GUI.root,
  title="Help Popup",
  button_text="Help",
  popup_text=help_text,
  debug=debug)
help_popup.grid(GUI.grid_size[0]-1,GUI.grid_size[1]-1)
#endregion

#region: imports / thumbnails
import_row: int = 3
import_col: int = 0

#region: Pattern
pattern_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                     thumb_size=THUMBNAIL_SIZE,
                                     debug=debug)
pattern_thumb.grid(import_row,import_col, rowspan=4)
GUI.add_widget("pattern_thumb", pattern_thumb)


def show_pattern_fixed() -> None:
  pattern_thumb.temp_image = prep_pattern(pattern_thumb.temp_image)
  debug.info("Showing Pattern")
  GUI.proj.show(pattern_thumb.temp_image)
pattern_button_fixed: Button = Button(
  GUI.root,
  text = 'Show Pattern',
  command = show_pattern_fixed)
pattern_button_fixed.grid(
  row = import_row+4,
  column = import_col,
  sticky='nesw')
GUI.add_widget("pattern_button_fixed", pattern_button_fixed)


#endregion

#region: Flatfield
# return a guess for correction intensity, 0 to 50 %
def guess_alpha():
  brightness: tuple[int,int] = get_brightness_range(flatfield_thumb.image, downsample_target=480)
  FF_strength_intput.set(round(((brightness[1]-brightness[0])*100)/510))
flatfield_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        debug=debug,
                                        accept_alpha=True,
                                        func_on_success=guess_alpha)
flatfield_thumb.grid(import_row,import_col+1, rowspan=4)
GUI.add_widget("flatfield_thumb", flatfield_thumb)

def show_flatfield() -> None:
  # resizeing
  image: Image.Image = flatfield_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing image for projection...")
    flatfield_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  debug.info("Showing flatfield image")
  GUI.proj.show(flatfield_thumb.temp_image)

flatfield_button: Button = Button(
  GUI.root,
  text = 'Show flatfield',
  command = show_flatfield)
flatfield_button.grid(
  row = import_row+4,
  column = import_col+1,
  sticky='nesw')
GUI.add_widget("flatfield_button", flatfield_button)

#endregion

#region: Red Focus
red_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                        thumb_size=THUMBNAIL_SIZE,
                                        debug=debug)
red_focus_thumb.grid(import_row+5,import_col, rowspan=4)
GUI.add_widget("red_focus_thumb", red_focus_thumb)

def show_red_focus() -> None:
  # posterizeing
  image: Image.Image = red_focus_thumb.temp_image
  if(posterize_toggle.state and (image.mode != 'L' or post_strength_intput.changed())):
    debug.info("Posterizing image...")
    red_focus_thumb.temp_image = posterize(red_focus_thumb.temp_image, round((post_strength_intput.get()*255)/100))
    red_focus_thumb.update_thumbnail(red_focus_thumb.temp_image)
  elif(not posterize_toggle.state and image.mode == 'L'):
    debug.info("Resetting image...")
    red_focus_thumb.temp_image = red_focus_thumb.image
    red_focus_thumb.update_thumbnail(red_focus_thumb.temp_image)
  # resizeing
  image: Image.Image = red_focus_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing image for projection...")
    red_focus_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  debug.info("Showing red focus image")
  GUI.proj.show(red_focus_thumb.temp_image)
red_focus_button: Button = Button(
  GUI.root,
  text = 'Show Red Focus',
  command = show_red_focus)
red_focus_button.grid(
  row = import_row+9,
  column = import_col,
  sticky='nesw')
GUI.add_widget("red_focus_button", red_focus_button)
#endregion

#region: UV Focus
uv_focus_thumb: Thumbnail = Thumbnail(root=GUI.root,
                                      thumb_size=THUMBNAIL_SIZE,
                                      debug=debug)
uv_focus_thumb.grid(import_row+5,import_col+1, rowspan=4)
GUI.add_widget("uv_focus_thumb", uv_focus_thumb)

def show_uv_focus() -> None:
  # resizeing
  image: Image.Image = uv_focus_thumb.temp_image
  if(image.size != fit_image(image, GUI.proj.size())):
    debug.info("Resizing image for projection...")
    uv_focus_thumb.temp_image = image.resize(fit_image(image, GUI.proj.size()), Image.Resampling.LANCZOS)
  debug.info("Showing uv focus image")
  GUI.proj.show(uv_focus_thumb.temp_image)

uv_focus_button: Button = Button(
  GUI.root,
  text = 'Show UV Focus',
  command = show_uv_focus)
uv_focus_button.grid(
  row = import_row+9,
  column = import_col+1,
  sticky='nesw')
GUI.add_widget("uv_focus_button", uv_focus_button)
#endregion

#endregion

GUI.root.grid_columnconfigure(2, minsize=SPACER_SIZE)

#region: Stage Control Area
stage_row: int = 3
stage_col: int = 3

stage: Stage_Controller = Stage_Controller(
debug=debug,
verbosity=3)
def step_update(axis: Literal['-x','+x','-y','+y','-z','+z']):
  # first check if the step size has changed
  if(x_step_intput.changed() or y_step_intput.changed() or z_step_intput.changed()):
    stage.step_size = (x_step_intput.get(), y_step_intput.get(), z_step_intput.get())
  stage.step(axis)
  
#region: Stage Position

stage_position_text: Label = Label(
  GUI.root,
  text = "Stage Position",
  justify = 'center',
  anchor = 'center'
)
stage_position_text.grid(
  row = stage_row,
  column = stage_col,
  columnspan = 3,
  sticky='nesw'
)
GUI.add_widget("stage_position_text", stage_position_text)

set_coords_button: Button = Button(
  GUI.root,
  text = 'Set Stage Position',
  command = lambda : stage.set(x_intput.get(), y_intput.get(), z_intput.get())
  )
set_coords_button.grid(
  row = stage_row+3,
  column = stage_col,
  columnspan = 3,
  sticky='nesw')
  
x_intput = Intput(
  root=GUI.root,
  name="X",
  default=stage.x(),
  debug=debug)
x_intput.grid(stage_row+1,stage_col,rowspan=2)
GUI.add_widget("x_intput", x_intput)
stage.update_funcs["x"]["x intput"] = lambda: x_intput.set(stage.x())

y_intput = Intput(
  root=GUI.root,
  name="Y",
  default=stage.y(),
  debug=debug)
y_intput.grid(stage_row+1,stage_col+1,rowspan=2)
GUI.add_widget("y_intput", y_intput)
stage.update_funcs["y"]["y intput"] = lambda: y_intput.set(stage.y())

z_intput = Intput(
  root=GUI.root,
  name="Z",
  default=stage.z(),
  debug=debug)
z_intput.grid(stage_row+1,stage_col+2,rowspan=2)
GUI.add_widget("z_intput", z_intput)
stage.update_funcs["z"]["z intput"] = lambda: z_intput.set(stage.z())

#endregion

#region: Stage Step size
step_size_row: int = 5

step_size_text: Label = Label(
  GUI.root,
  text = "Step Size",
  justify = 'center',
  anchor = 'center'
)
step_size_text.grid(
  row = stage_row+step_size_row,
  column = stage_col,
  columnspan = 3,
  sticky='nesw'
)
GUI.add_widget("step_size_text", step_size_text)

x_step_intput = Intput(
  root=GUI.root,
  name="X",
  default=1,
  debug=debug)
x_step_intput.grid(stage_row+step_size_row+1,stage_col)
GUI.add_widget("x_step_intput", x_step_intput)

y_step_intput = Intput(
  root=GUI.root,
  name="Y",
  default=1,
  debug=debug)
y_step_intput.grid(stage_row+step_size_row+1,stage_col+1)
GUI.add_widget("y_step_intput", y_step_intput)

z_step_intput = Intput(
  root=GUI.root,
  name="Z",
  default=1,
  debug=debug)
z_step_intput.grid(stage_row+step_size_row+1,stage_col+2)
GUI.add_widget("z_step_intput", z_step_intput)

#endregion

#region: stepping buttons
step_button_row = 7
### X axis ###
up_x_button: Button = Button(
  GUI.root,
  text = '+x',
  command = lambda : step_update('+x')
  )
up_x_button.grid(
  row = stage_row+step_button_row,
  column = stage_col,
  sticky='nesw')
GUI.add_widget("up_button", up_x_button)

down_x_button: Button = Button(
  GUI.root,
  text = '-x',
  command = lambda : step_update('-x')
  )
down_x_button.grid(
  row = stage_row+step_button_row+1,
  column = stage_col,
  sticky='nesw')
GUI.add_widget("down_button", down_x_button)

### Y axis ###
up_y_button: Button = Button(
  GUI.root,
  text = '+y',
  command = lambda : step_update('+y')
  )
up_y_button.grid(
  row = stage_row+step_button_row,
  column = stage_col+1,
  sticky='nesw')
GUI.add_widget("up_button", up_y_button)

down_y_button: Button = Button(
  GUI.root,
  text = '-y',
  command = lambda : step_update('-y')
  )
down_y_button.grid(
  row = stage_row+step_button_row+1,
  column = stage_col+1,
  sticky='nesw')
GUI.add_widget("down_button", down_y_button)

### Z axis ###
up_z_button: Button = Button(
  GUI.root,
  text = '+z',
  command = lambda : step_update('+z')
  )
up_z_button.grid(
  row = stage_row+step_button_row,
  column = stage_col+2,
  sticky='nesw')
GUI.add_widget("up_button", up_z_button)

down_z_button: Button = Button(
  GUI.root,
  text = '-z',
  command = lambda : step_update('-z')
  )
down_z_button.grid(
  row = stage_row+step_button_row+1,
  column = stage_col+2,
  sticky='nesw')
GUI.add_widget("down_button", down_z_button)

#endregion

#region: keyboard input

GUI.root.bind('<Up>', lambda event: step_update('+y'))
GUI.root.bind('<Down>', lambda event: step_update('-y'))
GUI.root.bind('<Left>', lambda event: step_update('-x'))
GUI.root.bind('<Right>', lambda event: step_update('+x'))
GUI.root.bind('<Control-Up>', lambda event: step_update('+z'))
GUI.root.bind('<Control-Down>', lambda event: step_update('-z'))
GUI.root.bind('<Shift-Up>', lambda event: step_update('+z'))
GUI.root.bind('<Shift-Down>', lambda event: step_update('-z'))

#endregion

#endregion

GUI.root.grid_columnconfigure(6, minsize=SPACER_SIZE)

#region: Patterning Area
pattern_row: int = 3
pattern_col: int = 7

#region: Options
options_row: int = 0
options_col: int = 0

options_text: Label = Label(
  GUI.root,
  text = "Options",
  justify = 'center',
  anchor = 'center'
)
options_text.grid(
  row = pattern_row+options_row,
  column = pattern_col+options_col,
  columnspan = 3,
  sticky='nesw'
)
GUI.add_widget("options_text", options_text)

#region: duration
duration_text: Label = Label(
  GUI.root,
  text = "Exposure Time (ms)",
  justify = 'center',
  anchor = 'center'
)
duration_text.grid(
  row = pattern_row+options_row+1,
  column = pattern_col+options_col,
  sticky='nesw'
)
GUI.add_widget("duration_text", duration_text)

duration_intput: Intput = Intput(
  root=GUI.root,
  name="Pattern Duration",
  default=1000,
  min = 0,
  debug=debug)
duration_intput.grid(pattern_row+options_row+1,pattern_col+options_col+1, colspan=2)
GUI.add_widget("duration_intput", duration_intput)

#endregion

#region: slicer settings

slicer_horiz_text: Label = Label(
  GUI.root,
  text = "Tiles (horiz, vert)"
)
slicer_horiz_text.grid(
  row = pattern_row+options_row+2,
  column = pattern_col+options_col,
  sticky='nesw'
)
GUI.add_widget("slicer_horiz_text", slicer_horiz_text)

slicer_horiz_intput: Intput = Intput(
  root=GUI.root,
  name="Slicer Horiz",
  default=1,
  min=1,
  debug=debug
)
slicer_horiz_intput.grid(pattern_row+options_row+2,pattern_col+options_col+1)
GUI.add_widget("slicer_horiz_intput", slicer_horiz_intput)

slicer_vert_intput: Intput = Intput(
  root=GUI.root,
  name="Slicer Vert",
  default=1,
  min=1,
  debug=debug
)
slicer_vert_intput.grid(pattern_row+options_row+2,pattern_col+options_col+2)
GUI.add_widget("slicer_vert_intput", slicer_vert_intput)
#endregion

#region: flatfield
FF_strength_text: Label = Label(
  GUI.root,
  text = "Flatfield Strength (%)",
  justify = 'center',
  anchor = 'center'
)
FF_strength_text.grid(
  row = pattern_row+options_row+3,
  column = pattern_col+options_col,
  sticky='nesw'
)
GUI.add_widget("FF_strength_text", FF_strength_text)

FF_strength_intput: Intput = Intput(
  root=GUI.root,
  name="FF Strength",
  default=0,
  min = 0,
  max = 100,
  debug=debug)
FF_strength_intput.grid(pattern_row+options_row+3,pattern_col+options_col+1)
GUI.add_widget("FF_strength_intput", FF_strength_intput)

flatfield_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Using Flatfield","NOT Using Flatfield"),
                                  debug=debug)
flatfield_toggle.grid(pattern_row+options_row+3,pattern_col+options_col+2)
#endregion

#region: posterize
post_strength_text: Label = Label(
  GUI.root,
  text = "Posterize Cutoff (%)",
  justify = 'center',
  anchor = 'center'
)
post_strength_text.grid(
  row = pattern_row+options_row+4,
  column = pattern_col+options_col,
  sticky='nesw'
)
GUI.add_widget("post_strength_text", post_strength_text)

post_strength_intput: Intput = Intput(
  root=GUI.root,
  name="Post Strength",
  default=50,
  min=0,
  max=100,
  debug=debug
)
post_strength_intput.grid(pattern_row+options_row+4,pattern_col+options_col+1)
GUI.add_widget("post_strength_intput", post_strength_intput)

posterize_toggle: Toggle = Toggle(root=GUI.root,
                                  text=("Now Posterizing","NOT Posterizing"),
                                  debug=debug)
posterize_toggle.grid(pattern_row+options_row+4,pattern_col+options_col+2)
#endregion

#endregion

#region: Current Tile
current_tile_row = 5
current_tile_col = 0

Current_tile_text: Label = Label(
  GUI.root,
  text = "Current Tile",
  
)
Current_tile_text.grid(
  row = pattern_row+current_tile_row,
  column = pattern_col+current_tile_col,
  columnspan = 2,
  sticky='nesw'
)
GUI.add_widget("Current_tile_text", Current_tile_text)

tile_placeholder = rasterize(Image.new('RGB', THUMBNAIL_SIZE, (0,0,0)))
current_tile_image: Label = Label(
  GUI.root,
  image = tile_placeholder,
  justify = 'center',
  anchor = 'center'
)
current_tile_image.grid(
  row = pattern_row+current_tile_row+1,
  column = pattern_col+current_tile_col,
  rowspan=4,
  columnspan=2,
  sticky='nesw'
)

#endregion

# region: Danger Buttons
buttons_row = 5
buttons_col = 2

pattern_status: Literal['idle','patterning', 'aborting'] = 'idle'
def change_patterning_status(new_status: Literal['idle','patterning', 'aborting']) -> None:
  global pattern_status
  match pattern_status:
    case 'idle':
      match new_status:
        case 'patterning':
          # change clear button to abort button
          clear_button.config(
            text='Abort',
            bg='red',
            fg='white',
            command=lambda: change_patterning_status('aborting'))
          clear_button.grid(rowspan=5)
          # disable pattern button
          pattern_button_timed.config(
            command=lambda: None)
          pattern_status = 'patterning'
        case 'aborting':
          debug.warn("invalid state transition: idle -> aborting")
        case 'idle':
          debug.warn("invalid state transition: idle -> idle")
    case 'patterning':
      match new_status:
        case 'idle':
          # normal transition, reset changes
          clear_button.config(
            text='Clear',
            bg='black',
            fg='white',
            command=GUI.proj.clear)
          clear_button.grid(rowspan=1)
          # re-enable pattern button
          pattern_button_timed.config(
            command=begin_patterning)
          pattern_status = 'idle'
        case 'aborting':
          # abort button was pressed while patterning, change global status and print warn
          pattern_status = 'aborting'
          GUI.proj.clear()
          debug.warn("aborting patterning...")
        case 'patterning':
          debug.warn("invalid state transition: patterning -> patterning")
    case 'aborting':
      match new_status:
        case 'idle':
          # abort resolved, reset changes
          clear_button.config(
            text='Clear',
            bg='black',
            fg='white',
            command=GUI.proj.clear)
          clear_button.grid(rowspan=1)
          # re-enable pattern button
          pattern_button_timed.config(
            command=begin_patterning)
          pattern_status = 'idle'
        case 'patterning':
          debug.warn("invalid state transition: aborting -> patterning")
        case 'aborting':
          debug.warn("invalid state transition: aborting -> aborting")

# big red danger button
tile_number: int = 0
def begin_patterning():
  global pattern_status
  debug.info("Slicing pattern...")
  slicer.update(image=pattern_thumb.image,
                horizontal_tiles=slicer_horiz_intput.get(),
                vertical_tiles=slicer_vert_intput.get(),
                output_resolution=GUI.proj.size())
  pattern_progress['value'] = 0
  pattern_progress['maximum'] = slicer.tile_count()
  debug.info("Patterning "+str(slicer.tile_count())+" tiles for "+str(duration_intput.get())+"ms \n  Total time: "+str(round((slicer.tile_count()*duration_intput.get())/1000))+"s")
  change_patterning_status('patterning')
  while True:
    # get patterning image
    image: Image.Image
    if(slicer.tile_count() == 1):
      image = prep_pattern(pattern_thumb.temp_image, thumb=pattern_thumb)
    else:
      image = prep_pattern(slicer.image())
    # set preview image
    preview_image = rasterize(image.resize(THUMBNAIL_SIZE, Image.Resampling.LANCZOS))
    current_tile_image.config(image=preview_image)
    current_tile_image.image = preview_image
    # TODO remove once camera is implemented
    camera_image_preview = rasterize(image.resize((GUI.window_size[0],(GUI.window_size[0]*9)//16), Image.Resampling.LANCZOS))
    camera.config(image=camera_image_preview)
    camera.image = camera_image_preview
    stage.lock()
    #pattern
    result = GUI.proj.show(image, duration=duration_intput.get())
    if(result):
      stage.unlock()
    # repeat
    if(pattern_status == 'aborting'):
      pattern_progress['value'] = 0
      debug.warn("Patterning aborted")
      break
    if(slicer.next()):
      pattern_progress['value'] += 1
      debug.info("Finished tile")
    else:
      pattern_progress['value'] = 0
      debug.info("Done")
      break
  change_patterning_status('idle')
  # clear preview image
  current_tile_image.config(image=tile_placeholder)
  current_tile_image.image = tile_placeholder
  # TODO remove once camera is implemented
  camera.config(image=camera_placeholder)
  camera.image = camera_placeholder
    
pattern_button_timed: Button = Button(
  GUI.root,
  text = 'Begin\nPatterning',
  command = begin_patterning,
  bg = 'red',
  fg = 'white')
pattern_button_timed.grid(
  row = pattern_row+buttons_row+1,
  column = pattern_col+buttons_col,
  rowspan=4,
  sticky='nesw')
GUI.add_widget("pattern_button_timed", pattern_button_timed)

# clear button has to come after to show ontop, annoying but inevitable
clear_button: Button = Button(
  GUI.root,
  text = 'Clear',
  bg='black',
  fg='white',
  command = GUI.proj.clear)
clear_button.grid(
  row = pattern_row+buttons_row,
  column = pattern_col+buttons_col,
  rowspan=1,
  sticky='nesw')
GUI.add_widget("clear_button", clear_button)

#endregion

#endregion

GUI.debug.info("Debug info will appear here")
GUI.mainloop()




