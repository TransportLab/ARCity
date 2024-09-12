#######################################################################
# Useful Tools
import cv2
import math
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import cv2
import numpy as np
import random
import open3d as o3d



def draw_roi(rect, image, frame_width, frame_length):

    x = (frame_width - rect) // 2
    y = (frame_length - rect) // 2

    # Draw the rectangle
    cv2.rectangle(image, (x, y), (x + rect, y + rect), (0, 0, 255), 2)
    # cv2.rectangle(image, (x, y), (x + rect_width, y + rect_length), (0, 0, 255), 2)

    return image


def distanc_cal(x, y, point_cloud, depth):
    err_pcd, point_cloud_value = point_cloud.get_value(x, y)
    err_depth, depth_value = depth.get_value(x, y)
    # if math.isfinite(point_cloud_value[2]):
    #     distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0]
    #                          + point_cloud_value[1] * point_cloud_value[1]
    #                          + point_cloud_value[2] * point_cloud_value[2])
    #     print(f'Point cloud distance to Camera at {{{x};{y}}}: {distance}')
    #     print(f'Depth distance to Camera at {{{x};{y}}}: {depth_value}')
    # else :
        # print(f'The distance can not be computed at {{{x};{y}}}')
    # return distance
    return (depth_value - 50)

def blend_images(front_image, back_image, alpha):
    """
    Blends two images with a given alpha for the front image.
    :param front_image: The image to be displayed in front.
    :param back_image: The image to be displayed in the background.
    :param alpha: The alpha value for the front image (0 to 1).
    :return: Blended image.
    """
    # Resize images to match if they are different sizes
    if front_image.shape != back_image.shape:
        back_image = cv2.resize(back_image, (front_image.shape[1], front_image.shape[0]))

    # Blend the images
    blended = cv2.addWeighted(front_image, alpha, back_image, 1 - alpha, 0)

    return blended


def vertex_bbox(frame_width, frame_length, side_length):
    
    x = (frame_width - side_length) // 2
    y = (frame_length - side_length) // 2
    
    return x, y, (x + side_length), (y + side_length)


def segmentation(checkpoint, image):
    
    model_type = "vit_b"
    device = "cuda"

    sam = sam_model_registry[model_type](checkpoint=checkpoint)
    sam.to(device=device)

    mask_generator = SamAutomaticMaskGenerator(sam)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.GaussianBlur(image, (3,3), 0)
    masks = mask_generator.generate(image)

    return masks


def detect_roi(masks, iou_threshold, frame_width, frame_length, side_length):

    bg_tl_x, bg_tl_y, bg_br_x, bg_br_y = vertex_bbox(frame_width, frame_length, side_length)

    white_image = np.zeros((frame_length, frame_width, 3), dtype="uint8")
    baseplate = np.array([-1, -1, -1, -1], dtype=int)

    for num in range(len(masks)):
        x,y,w,h = masks[num]['bbox']
        try:
            if x < bg_tl_x or x > bg_br_x or y < bg_tl_y or y > bg_br_y:
                continue
            elif (w * h) > ((bg_br_x - bg_tl_x) * (bg_br_y - bg_tl_y)):
                continue
            elif (w * h) < (iou_threshold * ((bg_br_x - bg_tl_x) * (bg_br_y - bg_tl_y))):
                continue
            else:
                # feathering for 1 pixel
                if baseplate[-1] == -1:
                    baseplate[0:4] = x, y, w, h
                else:
                    baseplate = np.append(baseplate, [x, y, w, h], axis = 0)
                rect_color = (0,random.randint(0, 255),random.randint(0, 255))
                cv2.rectangle(white_image, (x, y), ((x + w), (y + h)), rect_color, 1, 1)
        except:
            print('Baseplate is not found')
            continue
    
    return white_image, baseplate


def grid_eastablish(baseplate, stud_num_x, stud_num_y):
    
    baseplate_width = baseplate[2]
    baseplate_length = baseplate[3]
    stud_width_original = baseplate_width / stud_num_x
    stud_length_original = baseplate_length /  stud_num_y
    stud_width = int(math.floor(stud_width_original))
    stud_length = int(math.floor(stud_length_original))

    if stud_width == stud_length:
        stud_size = stud_width
    else:
        stud_size = int(math.floor((stud_width + stud_length)/2))
        print('Stud size is aligned')
    
    return stud_size


def baseplate_aligned(baseplate, stud_num_x, stud_num_y, distortion_coefficient):

    # Calculate the index and position of the middle stud
    middle_x = stud_num_x // 2
    middle_y = stud_num_y // 2

    # Initialize arrays for stud sizes
    grid_width = np.zeros(stud_num_x, dtype=int)
    grid_length = np.zeros(stud_num_y, dtype=int)

    # Simple sum
    # if (baseplate[2] % stud_num_x != 0) or (baseplate[3] % stud_num_y != 0):
    #     grid_width[0,:] = stud_size
    #     grid_length[0,:] = stud_size
    #     remainder_x = baseplate[2] % stud_num_x
    #     remainder_y = baseplate[3] % stud_num_y
    #     if remainder_x != 0:
    #         grid_width[0, stud_num_x - remainder_x : stud_num_x] += 1
    #     if remainder_y != 0:
    #         grid_length[0, stud_num_y - remainder_y : stud_num_y] += 1

    # Calculate the size of studs with distortion, except for the middle one
    for i in range(stud_num_x):
        distance_to_center = abs(i - middle_x)
        distorted_size = (baseplate[2] // stud_num_x) * (1 + distortion_coefficient * distance_to_center)
        grid_width[i] = int(distorted_size)

    for j in range(stud_num_y):
        distance_to_center = abs(j - middle_y)
        distorted_size = (baseplate[3] // stud_num_y) * (1 + distortion_coefficient * distance_to_center)
        grid_length[j] = int(distorted_size)

    # Adjust the size of the middle stud to ensure the canvas is fully filled
    grid_width[middle_x] = baseplate[2] - sum(grid_width) + grid_width[middle_x]
    grid_length[middle_y] = baseplate[3] - sum(grid_length) + grid_length[middle_y]

    return grid_width, grid_length


def draw_grid(image, baseplate, grid_width, grid_length):
    
    # Draw the studs
    x_start = baseplate[0]
    for width in grid_width:
        y_start = baseplate[1]
        for height in grid_length:
            cv2.rectangle(image, (x_start, y_start), (x_start + width, y_start + height), (255, 0, 0), 1)
            y_start += height
        x_start += width
    
    return image


