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
import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import cv2
import requests
import json

# debug_corners = False
debug_corners = True
server_url = 'http://localhost:5000/'

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect

def four_point_transform(image, pts, grid):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)


    if grid == 'native':
        (tl, tr, br, bl) = rect
        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
    else:
        maxWidth = grid[0]
        maxHeight = grid[1]

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped

def get_corners(zed,runtime_parameters,N):
    i = 0
    image = sl.Mat()
    out = np.zeros([N,4,2])
    while i < N:
        # A new image is available if grab() returns SUCCESS
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT)
            # Retrieve depth map. Depth is aligned on the left image
            #zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
            # Retrieve colored point cloud. Point cloud is aligned on the left image.
            #zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

            im = image.get_data()
            if debug_corners:
                # cv2.imshow('frame',im)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                    # break
                plt.imsave('frame.png',im)
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV) # Convert BGR to HSV

            # define range of corner color in HSV (currently ORANGE for some reason)
            lower_orange = np.array([15,200,100])
            upper_orange = np.array([20,255,255])

            # Threshold the HSV image to get only orange colors
            mask = cv2.inRange(hsv, lower_orange, upper_orange)

            # Bitwise-AND mask and original image
            res = cv2.bitwise_and(im,im, mask= mask)

            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts = sorted(contours, key=cv2.contourArea)

            these_corners = np.zeros([4,2])
            print('Found ' + str(len(cnts)) + ' possible corners')
            for j in range(4):
                cnt = cnts[-1-j]
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                if debug_corners: im = cv2.circle(mask, (cx,cy), 10, (255,0,0), 3)
                these_corners[j] = [cx,cy]
            #these_corners_sorted = sorted(these_corners)#, key=lambda x: these_corners[x,0]**2 + these_corners[x,1]**2)
            these_corners_sorted = order_points(these_corners)
            out[i] = these_corners_sorted

            if debug_corners:
                # cv2.imshow('frame',im)
                cv2.imshow('mask',mask)
                # cv2.imshow('res',res)
                if cv2.waitKey(1) & 0xFF == ord('q'):
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

    averaged_corners = np.mean(np.array(out),axis=0)
    #print(averaged_corners)
    #np.savetxt('corners.txt',averaged_corners)
    return averaged_corners

def get_lego_bricks(image,depths,pts,grid):
    colour = four_point_transform(image.get_data(), pts, grid)
    depths = four_point_transform(depths.get_data(), pts, grid)

def initialise_camera():
    zed = sl.Camera() # Create a Camera object

    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
    init_params.camera_resolution = sl.RESOLUTION.HD2K
    # init_params.camera_resolution = sl.RESOLUTION.HD720

    err = zed.open(init_params) # Open the camera

    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)
    else: print('Zed camera is alive')

    runtime_parameters = sl.RuntimeParameters()
    # runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD  # Use STANDARD sensing mode
    runtime_parameters.sensing_mode = sl.SENSING_MODE.FILL # fill all holes in depth sensing
    # Setting the depth confidence parameters
    runtime_parameters.confidence_threshold = 100 # NOT SURE WHAT THIS DOES
    runtime_parameters.textureness_confidence_threshold = 100 # NOT SURE WHAT THIS DOES

    return zed, runtime_parameters

def get_zed_frame(image,depth):
    # A new image is available if grab() returns SUCCESS
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        # Retrieve left image
        zed.retrieve_image(image, sl.VIEW.LEFT)
        # Retrieve depth map. Depth is aligned on the left image
        zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
        # Retrieve colored point cloud. Point cloud is aligned on the left image.
        #zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
        try:
            colours,heights = get_lego_bricks(image,depth,corners,grid)
        except:
            print('Failed to find lego bricks')
            print(sys.exc_info()[0])
            zed.close()
            exit(1)
        # r = requests.post(url = server_url + '/post_zed_data_to_server', data = {'depths': json.dumps(heights.tolist()),'colours': json.dumps(colours.tolist()) })
        # print("The server responded with: " + r.text)

        if debug_lego_bricks:
            d = cv2.normalize(heights, None, 255,0, cv2.NORM_MINMAX, cv2.CV_8UC1) # just for visualisation
            # print(depths)}
            cv2.imshow("Heights", d)
            cv2.imshow("Colours", colours)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # break
                exit(1)
        return colours, heights
    else:
        print('ZED CAMERA FAILED TO GET A FRAME')
        return -1, -1


def main():
    zed, runtime_parameters = initialise_camera()

    # grid = [25,25] # how many lego studs are available in horizontal and vertical direction
    grid = 'native' # get the best image possible

    image = sl.Mat()
    depth = sl.Mat()

    try:
        corners = get_corners(zed,runtime_parameters,10)
    except Exception as e:
        print('Failed to find corners, quitting gracefully. Got the exception:')
        print(e)
        zed.close()
        exit(1)
    # sending post request and saving response as response object
    # r = requests.post(url = server_url + '/post_corners_to_server', data = { 'corners': json.dumps(corners.tolist()) })
    # print("The server responded with: " + r.text)

    while True:
        heights, colours = get_zed_frame(image,depth)
    # Close the camera
    zed.close()

if __name__ == "__main__":
    main()
