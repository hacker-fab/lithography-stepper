from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ImageOps import invert
from math import ceil
from random import randint

# return max image size that will fit in [win_size] without cropping
def fit_image(image: Image.Image, win_size: tuple[int,int]) -> tuple[int,int]:
  # for easier access
  img_size: tuple[int,int] = (image.width, image.height)
  # determine orientation to fit to
  if (win_size[0] / win_size[1]) > (img_size[0] / img_size[1]):
    # window wider than image: fit to height
    return (round(img_size[0] * (win_size[1] / img_size[1])), win_size[1])
  elif (win_size[0] / win_size[1]) < (img_size[0] / img_size[1]):
    # image wider than window: fit to width
    return (win_size[0], round(img_size[1] * (win_size[0] / img_size[0])))
  else:
    # same ratio
    return win_size
  

# return min image size that will fill in window
def fill_image(image: Image.Image, win_size: tuple[int,int]) -> tuple[int,int]:
  # for easier access
  img_size: tuple[int,int] = (image.width, image.height)
  # determine orientation to fit to
  if (win_size[0] / win_size[1]) > (img_size[0] / img_size[1]):
    # window wider than image: fit to width
    return (win_size[0], round(img_size[1] * (win_size[0] / img_size[0])))
  elif (win_size[0] / win_size[1]) < (img_size[0] / img_size[1]):
    # image wider than window: fit to height
    return (round(img_size[0] * (win_size[1] / img_size[1])), win_size[1])
  else:
    # same ratio
    return win_size


# convert a value on one scale to the same location on another scale
def rescale_value(old_scale: tuple[int,int], new_scale: tuple[int,int], value: int) -> int:
    if(old_scale[0] == old_scale[1]):
      value = old_scale[0]
    assert(old_scale[0] <= old_scale[1])
    if(new_scale[0] == new_scale[1]):
      return new_scale[0]
    assert(new_scale[0] < new_scale[1])
    # get % into the scale
    d = (value - old_scale[0]) / (old_scale[1] - old_scale[0])
    # convert to second scale
    return round((d * (new_scale[1]-new_scale[0])) + new_scale[0])


# return a center cropped version of image at desired resolution
# example: if size == window then this will fill and crop image to window
def center_crop(image: Image.Image, crop_size: tuple[int,int]) -> Image.Image:
  # copy image
  cropped: Image.Image = image.copy()
  
  assert(crop_size[0]>0 and crop_size[1]>0)
  
  
  # resample image to fill desired size
  cropped = cropped.resize(fill_image(image, crop_size), resample=Image.Resampling.LANCZOS)
  
  # determine which orientation needs cropping
  assert(cropped.width == crop_size[0] or cropped.height == crop_size[1])
  if   (cropped.width == crop_size[0]):
    # width matches, crop height
    diff:  int = cropped.height - crop_size[1]
    top:  int = (diff//2)
    bottom: int = cropped.height - top
    # if odd, we're adding an extra row, so subtract one from bottom to correct
    if(diff % 2 == 1):
      bottom -= 1
    cropped = cropped.crop((0, top, cropped.width, bottom))
  elif (cropped.height == crop_size[1]):
    # height matches, crop width
    diff:  int = cropped.width - crop_size[0]
    left:  int = (diff//2)
    right: int = cropped.width - left
    # if odd, we're adding an extra column, so subtract one from right to correct
    if(diff % 2 == 1):
      right -= 1
    cropped = cropped.crop((left, 0, right, cropped.height))
  
  # done
  return cropped


# return the max and min brightness values of an image
# optionally specify downsampling target
def get_brightness_range(image: Image.Image,
                         downsample_target: int = 0) -> tuple[int,int]:
  img_copy: Image.Image = image.copy()
  # first make sure image is single channel
  if(img_copy.mode != "L"):
    img_copy = img_copy.convert("L")
  # downsample if specified
  if(downsample_target > 0):
    while img_copy.width > downsample_target or img_copy.height > downsample_target:
      img_copy = img_copy.resize((img_copy.width//2, img_copy.height//2), resample=Image.Resampling.LANCZOS)
  # get brightness range
  brightness: list[int] = [255,0]
  for col in range(img_copy.width):
    for row in range(img_copy.height):
      # get single-value brightness since it's grayscale
      pixel = img_copy.getpixel((col, row))
      if pixel < brightness[0]:
        brightness[0] = pixel
      if pixel > brightness[1]:
        brightness[1] = pixel
  return (brightness[0], brightness[1])  


# returns a rescaled copy of an alpha mask
# can be slow on larger images, only accepts L format images
def rescale(image: Image.Image, new_scale: tuple[int,int]) -> Image.Image:
  assert(image.mode == "L")
  mask: Image.Image = image.copy()
  # first step is getting brightest and darkest pixel values
  brightness: tuple[int,int] = get_brightness_range(mask)
  # now rescale each pixel
  lut: dict = {}
  for col in range(mask.width):
    for row in range(mask.height):
      # get pixel and lookup
      pixel: int = mask.getpixel((col,row))
      lookup: int = lut.get(pixel, -1)
      if (lookup == -1):
        lookup = rescale_value((brightness[0],brightness[1]), new_scale, pixel)
      mask.putpixel((col,row), lookup)
  return mask


# returns an alpha channel mask equivalent from source image
# optionally specify new scale
# optionally specify new cropped size
def convert_to_alpha_channel(input_image: Image.Image,
                             new_scale: tuple[int,int] | None = None,
                             target_size: tuple[int,int] = (0,0),
                             downsample_target: int = 1080) -> Image.Image:
  # copy the image
  mask: Image.Image = input_image.copy()
  # convert it to grayscale to normalize all values
  if(mask.mode != "L"):
    mask = mask.convert("L")
  # Invert all colors since we want the mask, not the image itself
  mask = invert(mask)
  if (new_scale!=None):
    # if no target, save current size
    if (target_size == (0,0)):
      target_size = mask.size
    # downsample
    while mask.width > downsample_target or mask.height > downsample_target:
      mask = mask.resize((mask.width//2, mask.height//2), resample=Image.Resampling.LANCZOS)
    # rescale
    mask = rescale(mask, new_scale)
    # resample to desired dimentions
    mask = center_crop(mask, target_size)
  elif (target_size != (0,0)):
    mask = center_crop(mask, target_size)
  # done
  return mask

# return an alpha mask image applied to another image
def apply_mask(input_image: Image.Image,
               mask_image: Image.Image,
               new_scale: tuple[int,int] = (0,255)) -> Image.Image:
  # setup
  input_img_copy: Image.Image = input_image.copy()
  target_size: tuple[int,int] = input_image.size
  # create mask and apply
  alpha_mask: Image.Image = convert_to_alpha_channel(mask_image, new_scale=new_scale, target_size=target_size)
  input_img_copy.putalpha(alpha_mask)
  # flatten image
  background: Image.Image = Image.new("RGB", target_size)
  background.paste(input_img_copy, (0,0), input_img_copy)
  # return image
  return background


# actually posterize an image since pil.posterize doesn't work
# optionally specify threashold
def posterize(Input_image: Image.Image, threashold: int = 127) -> Image.Image:
  output_image: Image.Image = Input_image.copy()
  output_image = output_image.convert("L")
  output_image = output_image.point( lambda p: 255 if p > threashold else 0 )
  return output_image


# returns a copy of the input image without alpha channel
def RGBA_to_RGB(image: Image.Image) -> Image.Image:
  assert(image.mode == "RGBA")
  channels: tuple[Image.Image,...] = image.split()
  assert(len(channels)==4)
  return Image.merge("RGB", channels[0:3])


# returns a copy of the input image without alpha channel
def LA_to_L(image: Image.Image) -> Image.Image:
  assert(image.mode == "LA")
  channels: tuple[Image.Image,...] = image.split()
  assert(len(channels)==2)
  return Image.merge("L", [channels[0]])


# This function is just a wrapper for ImageTk.PhotoImage() because of a bug
# for whatever reason, photoimage removes the alpha channel from LA images
# so this converts inputted LA images to RGBA before passing to PhotoImage
def rasterize(image: Image.Image) -> ImageTk.PhotoImage:
  if(image.mode == "LA"):
    return ImageTk.PhotoImage(image.convert("RGBA"))
  else:
    return ImageTk.PhotoImage(image)


# convert from 0 to 100 intensity scale to tuple values
# 0   = (255, 255)
# 50  = (0,   255)
# 100 = (0,   0)
def dec_to_alpha(dec: int) -> tuple[int,int]:
  if(dec < 0):
    return (255,255)
  if(dec <= 50):
    return (255-ceil((255*dec)/50),255)
  if(dec <= 100):
    return (0,255-ceil((255*(dec-50))/50))
  return (0,0)
def alpha_to_dec(alpha: tuple[int,int]) -> int:
  return int(((510-alpha[0]-alpha[1])*100)/510)


# automated test suite
def __run_tests():
  # will print a and b on fail
  def print_assert(a, b, name: str = ""):
    if(a==b):
      assert(True)
    if(a!=b): 
      print(name,a,"!=",b)
      assert(False)
  dim0 = (50,200)
  dim1 = (150,100)
  dim2 = (177,377)
  dim3 = (277,77)
  img0 = Image.new("RGBA", dim0)
  img1 = Image.new("RGBA", dim1)
  img2 = Image.new("RGBA", dim2)
  img3 = Image.new("RGBA", dim3)
  
  # fit to height
  print_assert(fit_image(img0, dim1), (25,100))
  # fit to width
  print_assert(fit_image(img1, dim0), (50,33))
  # fill to width
  print_assert(fill_image(img0, dim1), (150,600))
  # fill to height
  print_assert(fill_image(img1, dim0), (300,200))
  
  old_scale = (10,110)
  new_scale = (5,15)
  # min value check
  print_assert(rescale_value(old_scale, new_scale, 10), 5)
  # max value check
  print_assert(rescale_value(old_scale, new_scale, 110), 15)
  # 7%
  print_assert(rescale_value(old_scale, new_scale, 7+10), 1+5)
  # 70%
  print_assert(rescale_value(old_scale, new_scale, 70+10), 7+5)
  
  # check both width and height crops for...
  # ...even...
  print_assert(center_crop(img0, dim1).size, dim1)
  print_assert(center_crop(img1, dim0).size, dim0)
  # ...odd...
  print_assert(center_crop(img2, dim3).size, dim3)
  print_assert(center_crop(img3, dim2).size, dim2)
  # ...mixed...
  print_assert(center_crop(img0, dim3).size, dim3)
  print_assert(center_crop(img1, dim2).size, dim2)
  print_assert(center_crop(img2, dim1).size, dim1)
  print_assert(center_crop(img3, dim0).size, dim0)
  # ...same
  print_assert(center_crop(img0, dim0).size, dim0)
  print_assert(center_crop(img2, dim2).size, dim2)
  
  # inputs for visual tests
  # image: Image.Image = Image.open(filedialog.askopenfilename(title ='Test Image')).copy()
  # mask: Image.Image  = Image.open(filedialog.askopenfilename(title ='Test mask')).copy()
  
  # apply_mask(image, mask).show()
  
  # (0,127) is incorrect, but should still work
  alphas = [(0,0), (0, 127), (0, 255), (127, 255), (255,255)]
  # correct conversions
  decs = [100, 75, 50, 25, 0]
  for i in range(len(alphas)):
    print_assert(alpha_to_dec(alphas[i]), decs[i], str(i)+":0")
    print_assert(dec_to_alpha(decs[i]), alphas[i], str(i)+":1")
    print_assert(dec_to_alpha(alpha_to_dec(alphas[i])), alphas[i], str(i)+":2")
    print_assert(alpha_to_dec(dec_to_alpha(decs[i])), decs[i], str(i)+":3")
  # test every number, why not
  for i in range(100):
    print_assert(alpha_to_dec(dec_to_alpha(i)), i, str(i)+":4")
    
  print("all tests passed")
__run_tests()


