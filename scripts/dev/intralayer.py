#from pyspin import PySpin
import sys
import cv2
import numpy as np

#region: CAMERA FUNCTIONS --------------------------------------------------------------------------------------

def capture_image(camera_info):
    # [REDACTED]
    return None


def initialize_camera():
    # [REDACTED]
    return None


def release_camera(camera_system, camera_info):
    # [REDACTED]
    return None
    

#endregion: CAMERA FUNCTIONS ----------------------------------------------------------------------------------------
#region: INTRALAYER ALIGNMENT FUNCTIONS ------------------------------------------------------------------------

alignment_reference_image = None
camera_system = None
camera_info = None


def set_reference_image(image=None):
    input("Capturing reference image")

    global alignment_reference_image
    global camera_info
    global camera_system

    if image != None:
        alignment_reference_image = image
    else:
        if camera_info == None:
            # releases camera_system if it's still active 
            release_camera(camera_system, camera_info)
            result = initialize_camera()

            if result == None:
                print("Failed to initialize camera.")
                return False
            
            camera_info = result["camera_info"]
            camera_system = result["camera_system"]

        result = capture_image(camera_info)

        if type(result) is np.ndarray:
            alignment_reference_image = result
            return True
        else:
            return False


# takes numpy arrays as input
def calculate_displacement(current_image, reference_image=None):
    global alignment_reference_image

    if isinstance(reference_image, type(None)):
        reference_image = alignment_reference_image

    if isinstance(reference_image, type(None)):
        return None

    # Resize image2 to match the size of image1, for test only, no need to have this in real application
    current_image = cv2.resize(current_image, (reference_image.shape[1], reference_image.shape[0]))

    # Detect and extract key points
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(reference_image, None)
    keypoints2, descriptors2 = orb.detectAndCompute(current_image, None)

    # Create a matcher (Brute Force)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match feature points
    matches = bf.match(descriptors1, descriptors2)

    # Sort the matches by distance (shortest distance first)
    # TODO: Optimize the match region by region
    matches = sorted(matches, key=lambda x: x.distance)

    # Keep only the top N matches (ideally 3 is ok, but for testing I used 10 instead)
    N = 10
    good_matches = matches[:N]

    # Extract the matching feature points
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # make sure that enough feature points were found
    if len(src_pts) < 4:
        print("Not enough feature points detected.")
        # return None
        # bypass for demo
        return [0, 0, 0]

    # Calculate the transformation matrix using RANSAC
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # Extract the translation
    dx = M[0, 2]
    dy = M[1, 2]

    # Calculate theta
    theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

    # Draw feature points on both images
    image1_with_keypoints = cv2.drawKeypoints(reference_image, keypoints1, None, color=(0, 255, 0), flags=0)
    image2_with_keypoints = cv2.drawKeypoints(current_image, keypoints2, None, color=(0, 255, 0), flags=0)

    # Draw lines between matching points pairs
    matching_image = cv2.drawMatches(reference_image, keypoints1, current_image, keypoints2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Show the images with feature points and matching lines
    #cv2.imshow('Reference image with Keypoints', cv2.resize(image1_with_keypoints, (600, 400), interpolation=cv2.INTER_LINEAR))
    #cv2.imshow('Current image with Keypoints', cv2.resize(image2_with_keypoints, (600, 400), interpolation=cv2.INTER_LINEAR))
    cv2.imshow('Matching Points', cv2.resize(matching_image, (1800, 600), interpolation=cv2.INTER_LINEAR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Display the displacement and rotation angle
    print(f"Displacement (dx, dy): ({dx}, {dy})")
    print(f"Rotation angle (theta): {theta} degrees")
    input('')

    return [dx, dy, theta]
    

def expose(pattern, time, dx=0, dy=0, theta=0):
    input(f"Exposing {pattern} under transformation ({dx}, {dy}, {theta}) for {time} milliseconds")


def move_by(x, y, theta):
    input(f"Moving by ({x}, {y}, {theta})")


def intralayer_align(num_tiles_x, num_tiles_y, tile_width, tile_height, pattern_tiles_to_expose, exposure_time, is_first_layer=False):
    global alignment_reference_image
    global camera_info

    num_tiles = num_tiles_x * num_tiles_y
    tile_num = 0
    tile_x = 0
    tile_y = 0

    move_x = [0] * num_tiles
    move_y = [0] * num_tiles
    move_theta = [0] * num_tiles
    down = True

    # calculate path
    for tx in range(0, num_tiles_x):
        if down:
            for ty in range(0, num_tiles_y - 1):
                move_y[tx * num_tiles_y + ty] = tile_height
                move_x[tx * num_tiles_y + ty] = 0

            move_y[tx * num_tiles_y + num_tiles_y - 1] = 0
            move_x[tx * num_tiles_y + num_tiles_y - 1] = tile_width
            down = False
            
        else:
            for ty in range(num_tiles_y - 1, 0, -1):
                move_y[tx * num_tiles_y + (num_tiles_y - ty - 1)] = -tile_height
                move_x[tx * num_tiles_y + (num_tiles_y - ty - 1)] = 0

            move_y[tx * num_tiles_y + (num_tiles_y - 1)] = 0
            move_x[tx * num_tiles_y + (num_tiles_y - 1)] = tile_width
            down = True

    # calculated path currently does not use nonfunctional reference tile; add it in
    # (reference tile is placed above top left corner tile)
    move_x.insert(0, 0)
    move_y.insert(0, tile_height)
    move_theta.insert(0, 0)
    # in the main loop, movement from the final tile is unnecessary and thus is ignored

    print("move_x: " + str(move_x))
    print("move_y: " + str(move_y))

    if is_first_layer:
        expose(pattern_tiles_to_expose[tile_num], exposure_time)
    else:
        pass # maybe auto-align to alignment tile here

    # layer N
    while tile_num < num_tiles:
        # 1. capture reference image to align to
        if not set_reference_image():
            return False
        cv2.imshow('Reference Image', cv2.resize(alignment_reference_image, (600, 400), interpolation=cv2.INTER_LINEAR))
        cv2.waitKey(0)

        # 2. open loop align to next tile
        move_by(move_x[tile_num], move_y[tile_num], move_theta[tile_num])

        # 3. calculate displacement from reference image
        current_image = capture_image(camera_info)
        if isinstance(current_image, type(None)):
            return False
        cv2.imshow('Current Image', cv2.resize(current_image, (600, 400), interpolation=cv2.INTER_LINEAR))
        cv2.waitKey(0)

        displacement = calculate_displacement(current_image)
        if displacement == None:
            return False

        # error is equal to visual displacement minus the amount we were supposed to move
        displacement[0] -= move_x[tile_num]
        displacement[1] -= move_y[tile_num]
        displacement[2] -= move_theta[tile_num]

        # avoid error accumulation by incorporating it in movements list
        tile_num += 1     
        move_x[tile_num] += displacement[0] 
        move_y[tile_num] += displacement[1]
        move_theta[tile_num] += displacement[2]

        # 4. Use error to transform and expose next pattern tile
        expose(pattern_tiles_to_expose[tile_num], exposure_time, -displacement[0], -displacement[1], -displacement[2])

    return True



#endregion: INTRALAYER ALIGNMENT FUNCTIONS --------------------------------------------------------------------------

if __name__ == '__main__':
    num_tiles_x = 2
    num_tiles_y = 3
    tile_width = 1920
    tile_height = 1080
    pattern_tiles_to_expose = ["Alignment reference tile", "tile (0, 0)", "tile (0, 1)", "tile (0, 2)",
        "tile (1, 2)", "tile (1, 1)", "tile (1, 0)"]
    exposure_time = 5000
    is_first_layer = True

    print("Performing intralayer alignment. Press Enter to move to next state.")
    if not intralayer_align(num_tiles_x, num_tiles_y, tile_width, tile_height, pattern_tiles_to_expose, exposure_time, is_first_layer):
        print("An error has occurred.")
    else:
        print("Intralayer alignment successful.")

    release_camera(camera_system, camera_info)
