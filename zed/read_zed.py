########################################################################
#
# Copyright (c) 2020, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

import pyzed.sl as sl
import numpy as np
import matplotlib.pyplot as plt
# import scipy.ndimage
import sys
import cv2
import requests
import json5
import traceback
import time


p = json5.loads(open("params.json5").read())
debug = False
# debug = True
# server_url = "http://localhost:5000/"


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype=np.float32)
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect


def four_point_transform(image, pts, grid, debug=True):
    # obtain a consistent order of the points and unpack them
    # individually
    # rect = order_points(pts)
    rect = np.float32(pts)
    
    # if grid == "native":
    #     (tl, tr, br, bl) = rect
    #     # compute the width of the new image, which will be the
    #     # maximum distance between bottom-right and bottom-left
    #     # x-coordiates or the top-right and top-left x-coordinates
    #     widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    #     widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    #     # compute the height of the new image, which will be the
    #     # maximum distance between the top-right and bottom-right
    #     # y-coordinates or the top-left and bottom-left y-coordinates
    #     heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    #     heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    #     maxWidth = max(int(widthA), int(widthB))
    #     maxHeight = max(int(heightA), int(heightB))
    # else:
    maxWidth = grid[0]
    maxHeight = grid[1]

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.float32(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]]
    )
    # compute the perspective transform matrix and then apply it
    
    
    # Assuming rect and dst are defined somewhere in your code
    rect = np.array(rect, dtype=np.float32)
    dst = np.array(dst, dtype=np.float32)

    # Ensure the arrays are contiguous
    # rect = np.ascontiguousarray(rect)
    # dst = np.ascontiguousarray(dst)

    # Convert to UMat
    # rect_umat = cv2.UMat(rect)
    # dst_umat = cv2.UMat(dst)


    # try:
    #     M = cv2.getPerspectiveTransform(rect, dst)
    #     print("Transformation matrix M:", M)
    # except cv2.error as e:
    #     print("OpenCV error:", e)
    # except Exception as e:
    #     print("Error:", e)


    #M = cv2.getPerspectiveTransform(rect, dst)
    #warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    im = np.array(image)
    crop = im[p["corners"][0][0]:p["corners"][2][0], p["corners"][0][1]:p["corners"][1][1]]
    dx = crop.shape[1] / p["W"]
    dy = crop.shape[0] / p["H"]

    if len(crop.shape) == 2:
        colours = np.zeros([maxWidth, maxHeight])
    else:
        colours = np.zeros([maxWidth, maxHeight, crop.shape[2]])
    for i in range(maxWidth):
        for j in range(maxHeight):
            x = int(i * dx)
            y = int(j * dy)
            colours[i, j] = np.median(crop[y:y+int(dy), x:x+int(dx)], axis=(0, 1))
    if debug:
        plt.imsave(f"crop_{len(crop.shape)}.png", crop)

    return colours


def get_corners(zed, runtime_parameters, N, p, debug=False):
    i = 0
    image = sl.Mat()
    out = np.zeros([N, 4, 2])
    while i < N:
        # A new image is available if grab() returns SUCCESS
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT)
            # Retrieve depth map. Depth is aligned on the left image
            # zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
            # Retrieve colored point cloud. Point cloud is aligned on the left image.
            # zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

            im = image.get_data()
            if debug:
                # cv2.imshow('frame',im)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                # break
                plt.imsave("frame.png", im)
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)  # Convert BGR to HSV

            # Threshold the HSV image to get only orange colors
            mask = cv2.inRange(
                hsv,
                np.array(p["colours"][p["corner_colour"]]["lower"]),
                np.array(p["colours"][p["corner_colour"]]["upper"]),
            )

            # Bitwise-AND mask and original image
            res = cv2.bitwise_and(im, im, mask=mask)

            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts = sorted(contours, key=cv2.contourArea)

            these_corners = np.zeros([4, 2])
            print("Found " + str(len(cnts)) + " possible corners")
            for j in range(4):
                cnt = cnts[-1 - j]
                M = cv2.moments(cnt)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                if debug:
                    im = cv2.circle(mask, (cx, cy), 10, (255, 0, 0), 3)
                these_corners[j] = [cx, cy]
            # these_corners_sorted = sorted(these_corners)#, key=lambda x: these_corners[x,0]**2 + these_corners[x,1]**2)
            these_corners_sorted = order_points(these_corners)
            out[i] = these_corners_sorted

            if debug:
                # cv2.imshow('frame',im)
                cv2.imshow("mask", mask)
                # cv2.imshow('res',res)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            # # Get and print distance value in mm at the center of the image
            # # We measure the distance camera - object using Euclidean distance
            # #x = round(image.get_width() / 2)
            # #y = round(image.get_height() / 2)
            # err, point_cloud_value = point_cloud.get_value(x, y)
            #
            # distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
            #                      point_cloud_value[1] * point_cloud_value[1] +
            #                      point_cloud_value[2] * point_cloud_value[2])
            #
            # point_cloud_np = point_cloud.get_data()
            # point_cloud_np.dot(tr_np)
            #
            # if not np.isnan(distance) and not np.isinf(distance):
            #     print("Distance to Camera at ({}, {}) (image center): {:1.3} m".format(x, y, distance), end="\r")
            #     # Increment the loop
            i = i + 1
            # else:
            #     print("Can't estimate distance at this position.")
            #     print("Your camera is probably too close to the scene, please move it backwards.\n")
            # sys.stdout.flush()

    averaged_corners = np.mean(np.array(out), axis=0)
    # print(averaged_corners)
    # np.savetxt('corners.txt',averaged_corners)
    return averaged_corners

def get_corners_hardcoded(zed, runtime_parameters, N, p, debug=False):
    if debug:
        image = sl.Mat()
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT)
            im = np.array(image.get_data())
            print(im.shape)
            print(im.dtype)

            # Draw markers for each corner in p["corners"]
            for corner in p["corners"]:
                # Assuming each corner is a tuple or list with (x, y) coordinates
                # x, y = corner
                # print(x,y)
                im[corner[0]-2:corner[0]+3,corner[1]-2:corner[1]+3,:] = 255
                # Draw a red circle at each corner (radius 5 pixels)
                # cv2.circle(im[:,:,:3], (int(x), int(y)), 5, (0, 0, 255), -1)
            plt.imsave("corners.png", im[:,:,:3])

            # Display the image with markers
            # cv2.imshow('frame with corners', im)

    return p["corners"]


def get_warped_data(image, depths, pts, grid, colour, height):
    new_colour = four_point_transform(image.get_data(), pts, grid)
    new_height = four_point_transform(depths.get_data(), pts, grid)

    alpha = 0.7
    colour = alpha * colour + (1 - alpha) * new_colour
    height = alpha * height + (1 - alpha) * new_height

    return colour, height


def map_colours_to_brick_types(im, p):
    # WARNING: UNTESTED. JUST FOR ILLUSTRATION PURPOSES.
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)  # Convert BGR to HSV
    brick_types = np.zeros([im.shape[0], im.shape[1]])

    for c in p["colours"]:  # go through each colour
        # Threshold the HSV image to get only orange colors
        mask = cv2.inRange(hsv, p["colours"][c]["lower"], p["colours"][c]["upper"])
        brick_types[mask == 255] = p["colours"][c]["index"]

    return brick_types


def initialise_camera():
    zed = sl.Camera()  # Create a Camera object

    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD2K
    # init_params.camera_resolution = sl.RESOLUTION.HD720

    err = zed.open(init_params)  # Open the camera

    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)
    else:
        print("Zed camera is alive")

    runtime_parameters = sl.RuntimeParameters()
    # runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
    # runtime_parameters.sensing_mode = sl.SENSING_MODE.FILL # fill all holes in depth sensing
    runtime_parameters.enable_fill_mode = True
    # Setting the depth confidence parameters
    runtime_parameters.confidence_threshold = 95  # NOT SURE WHAT THIS DOES
    runtime_parameters.texture_confidence_threshold = 100  # NOT SURE WHAT THIS DOES
    # runtime_parameters.depth_minimum_distance = 1.5  #; // Set the minimum depth perception distance to 15cm
    # runtime_parameters.depth_maximum_distance = 3.0

    return zed, runtime_parameters


def get_zed_frame(zed, runtime_parameters, image, depth, corners, grid, colours, heights):
    # A new image is available if grab() returns SUCCESS
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # Retrieve left image
        zed.retrieve_image(image, sl.VIEW.LEFT)
        # Retrieve depth map. Depth is aligned on the left image
        zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
        # Retrieve colored point cloud. Point cloud is aligned on the left image.
        # zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
        try:
            colours, heights = get_warped_data(image, depth, corners, grid, colours, heights)
        except:
            print("Failed to find lego bricks")
            traceback.print_exc(file=sys.stdout)
            zed.close()
            exit(1)
        # r = requests.post(url = server_url + '/post_zed_data_to_server', data = {'depths': json5.dumps(heights.tolist()),'colours': json5.dumps(colours.tolist()) })
        # print("The server responded with: " + r.text)

        # if debug:
        #     d = cv2.normalize(heights, None, 255,0, cv2.NORM_MINMAX, cv2.CV_8UC1) # just for visualisation
        #     # print(depths)}
        #     cv2.imshow("Heights", d)
        #     cv2.imshow("Colours", colours)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         # break
        #         exit(1)
        return colours, heights
    else:
        print("ZED CAMERA FAILED TO GET A FRAME")
        return -1, -1


def main():
    zed, runtime_parameters = initialise_camera()

    p = json5.loads(open("params.json5").read())

    grid = [
        p["W"],
        p["H"],
    ]  # how many lego studs are available in horizontal and vertical direction
    # grid = 'native' # get the best image possible

    heights = np.zeros(grid)
    colours = np.zeros([grid[0], grid[1], 4])
    image = sl.Mat()
    depth = sl.Mat()

    try:
        # corners = get_corners(zed, runtime_parameters, 3, p)
        corners = get_corners_hardcoded(zed, runtime_parameters, 3, p)
    except Exception as e:
        print("Failed to find corners, quitting gracefully. Got the exception:")
        traceback.print_exc(file=sys.stdout)
        zed.close()
        exit(1)

    smoothed = False
    while True:
        try:
            time.sleep(1)  # wait 1 second
            colours, heights = get_zed_frame(
                zed, runtime_parameters, image, depth, corners, grid, colours, heights
            )

            # print(heights.mean())

            # remove offset to plane from heights and convert to studs
            # base_offset = (height[0,0] + height[0,-1] + height[-1,0] + height[-1,-1])/4. + 8e-3
            lego = np.median(heights, axis=(0, 1)) - heights
            lego /= p["brick_height"] * 1e-3  # 9.6 mm per stud
            # print(np.around(lego))
            lego[~np.isfinite(lego)] = 0.0
            lego[lego < 0] = 0.0
            lego[lego > 5] = 5.0
            lego = lego.astype(np.int64)

            if isinstance(smoothed, np.ndarray):
                smoothed = lego
            else:
                smoothed = (1-p["exp_smooth"]) * smoothed + p["exp_smooth"] * lego

            # print(lego.tolist()[0])
            # sending post request and saving response as response object
            r = requests.post(
                url=p["imac_url"] + "/post_zed_data_to_server",
                data={
                    "depths": json5.dumps(lego.tolist()),
                    "colours": json5.dumps(colours.astype(np.int64).tolist()),
                },
            )
            print("The server responded with: " + r.text)
        except Exception as e:
            print("Failed to get frame, quitting gracefully. Got the exception:")
            traceback.print_exc(file=sys.stdout)
            # zed.close()
            # exit(1)

    # Close the camera
    zed.close()


if __name__ == "__main__":
    main()
