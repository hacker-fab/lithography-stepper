from tkinter import filedialog
from PIL import Image
from PIL.ImageOps import invert

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


def rescale_value(old_scale: tuple[int,int], new_scale: tuple[int,int], value: int) -> int:
    if(old_scale[0] == old_scale[1]):
      if(value == old_scale[0]):
        return new_scale[0]
      else:
        assert(value == old_scale[0])
    assert(old_scale[0] > old_scale[1])
    assert(new_scale[0] > new_scale[1])
    # get % into the scale
    d = (value - old_scale[1]) / (old_scale[0] - old_scale[1])
    # convert to float in second scale
    return round((d * (new_scale[0]-new_scale[1])) + new_scale[1])


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



# returns a rescaled copy of an alpha mask
# can be slow on larger images, only accepts L format images
def rescale(image: Image.Image, new_scale: tuple[int,int]) -> Image.Image:
  mask: Image.Image = image.copy()
  assert(mask.mode == "L")
  # first step is getting brightest and darkest pixel values
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
                             new_scale: tuple[int,int] = (0,0),
                             target_size: tuple[int,int] = (0,0)) -> Image.Image:
  # copy the image
  mask: Image.Image = input_image.copy()
  # convert it to grayscale to normalize all values
  mask = mask.convert("L")
  # Invert all colors since we want the mask, not the image itself
  mask = invert(mask)
  if (new_scale!=(0,0)):
    # if no target, save current size
    if (target_size == (0,0)):
      target_size = mask.size
    # downsample
    target: int = 1080
    while mask.width > target or mask.height > target:
      mask = mask.resize((mask.width//2, mask.height//2), resample=Image.Resampling.LANCZOS)
    # rescale
    mask = rescale(mask, new_scale)
    # resample to desired dimentions
    mask = center_crop(mask, target_size)
  elif (target_size != (0,0)):
    mask = center_crop(mask, target_size)
  # done
  return mask


def __run_tests():
  def print_assert(a, b):
    if(a==b):
      assert(True)
    if(a!=b): 
      print(a,"!=",b)
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
  
  old_scale = (110,10)
  new_scale = (15,5)
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
  
  # visual check of alpha mask
  # image: Image.Image = Image.open(filedialog.askopenfilename(title ='Test Image')).copy()
  # mask: Image.Image  = Image.open(filedialog.askopenfilename(title ='Test mask')).copy()
  print("all tests passed")
__run_tests()