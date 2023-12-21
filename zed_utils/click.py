#######################################################################
# Click
import pyzed.sl as sl
import cv2
import numpy as np

class Click:
    def __init__(self, grid_map):
        self.grid_map = grid_map
        self.background_color = 'white'
        self.current_color = 'purple'
    
    def click_grid_cell(self, x, y):
        """
        Finds which grid cell the point belongs to in a grid defined by a NumPy array.

        Parameters:
        coordinate_map (numpy.ndarray): A NumPy array of shape (num_grids_y, num_grids_x, 4), 
                                        where each element contains the top-left and bottom-right 
                                        coordinates of a grid cell.
        point (tuple): The (x, y) coordinates of the point.

        Returns:
        tuple: The (row, column) of the grid cell that the point belongs to, or (-1, -1) if the point is not in any grid cell.
        """
        flag = 0
        for row in range(self.grid_map.coordinate_map.shape[0]):
            for col in range(self.grid_map.coordinate_map.shape[1]):
                top_left_x, top_left_y, bottom_right_x, bottom_right_y = self.grid_map.coordinate_map[row, col]
                if top_left_x <= x <= bottom_right_x and top_left_y <= y <= bottom_right_y:
                    flag = 1
                    if flag == 1:
                        break
            if flag == 1:
                break
        return row, col
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            row, col = self.click_grid_cell(x, y)
            self.grid_map.add_color(col, row, self.current_color)

    # def click_draw(self):
    #     # grid_image = cv2.cvtColor(grid_image, cv2.COLOR_BGR2RGB)
    #     for y in range(self.grid_map.num_grids_y):
    #         for x in range(self.grid_map.num_grids_x):
    #             # draw the color
    #             if self.grid_map.color_map[y,x] == 0:
    #                 grid_color = (255,255,255)   # white
    #             elif self.grid_map.color_map[y,x] == 1:
    #                 grid_color = (50,127,205)   # brown
    #             elif self.grid_map.color_map[y,x] == 2:
    #                 grid_color = (128,0,128)   # purple
    #             elif self.grid_map.color_map[y,x] == 3:
    #                 grid_color = (50,205,50)   # green
    #             elif self.grid_map.color_map[y,x] == 4:
    #                 grid_color = (0,191,255)   # yellow
    #             elif self.grid_map.color_map[y,x] == 5:
    #                 grid_color = (0,0,0)   # black
    #             elif self.grid_map.color_map[y,x] == 10:
    #                 grid_color = (32,0,128)   # red
    #             else:
    #                 grid_color = (255,255,255)   # unknow->blue
    #             # print(self.coordinate_map[y,x])
    #             # BGR format
    #             cv2.rectangle(self.grid_map.grid_image, 
    #                         (int(self.grid_map.coordinate_map[y,x,0]),int(self.grid_map.coordinate_map[y,x,1])), 
    #                         (int(self.grid_map.coordinate_map[y,x,2]), int(self.grid_map.coordinate_map[y,x,3])), 
    #                         grid_color, -1)