#######################################################################
# Color setting
import numpy as np


def color_init():
    lower_white = np.array([0, 0, 254])
    upper_white = np.array([180, 1, 255])
    lower_purple = np.array([120,25,120])
    upper_purple = np.array([170,255,255])
    lower_green = np.array([40, 40, 75])
    upper_green = np.array([80,255, 255])
    lower_yellow = np.array([25, 0, 254])
    upper_yellow = np.array([40, 255, 255])
    lower_brown = np.array([150, 0, 0])
    upper_brown = np.array([180, 145, 245])
    lower_red_1 = np.array([0, 25, 200])
    upper_red_1 = np.array([40, 255, 255])

    color_range = (np.concatenate((lower_white, upper_white,
                                   lower_purple, upper_purple,
                                   lower_green, upper_green,
                                   lower_yellow, upper_yellow,
                                   lower_brown, upper_brown,
                                   lower_red_1, upper_red_1))).reshape((-1,3))

    color_dict = [ 'white', 'purple', 'green', 'yellow', 'black', 'red', 'unknow']
    
    color_persentage = np.array([0.55, 0.5, 0.5, 0.5, 0.5, 0.5])

    return color_range, color_dict, color_persentage