#######################################################################
# Grid Map
import math
import cv2
import numpy as np
import random
import os
from sklearn.cluster import DBSCAN
import open3d as o3d


def create_cuboid(bottom_corners, height):
    vertices = np.vstack([bottom_corners, bottom_corners + np.array([0, 0, height])])
    
    faces = np.array([
        [0, 2, 1], [0, 3, 2], # 底面
        [4, 5, 6], [4, 6, 7], # 顶面
        [0, 4, 7], [0, 7, 3], # 前侧面
        [1, 2, 6], [1, 6, 5], # 后侧面
        [2, 3, 7], [2, 7, 6], # 右侧面
        [0, 1, 5], [0, 5, 4]  # 左侧面
    ])
    
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    
    return mesh


def distanc_cal(x, y, point_cloud, depth):
    err_depth, depth_value = depth.get_value(x, y)
    print(depth_value)
    return (depth_value)


class GridMap:
    '''
    generate the color map with depth
    '''
    def __init__(self, num_grids_x, num_grids_y, baseplate, color_range, color_dict, color_persentage, bg_width, bg_length):
        self.num_grids_x = num_grids_x
        self.num_grids_y = num_grids_y
        self.color_map = np.zeros((self.num_grids_y,self.num_grids_x), dtype = int)
        self.coordinate_map = np.zeros((self.num_grids_y,self.num_grids_x,4), dtype = int)
        self.baseplate = baseplate
        self.depth_info = np.zeros((self.num_grids_y, self.num_grids_x), dtype = int)
        self.building_clusters = 0
        self.road_clusters = 0
        self.grid_image = np.zeros((bg_length, bg_width, 3), dtype = "uint8")
        # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 6->red, 7->unknow
        self.color_range = color_range
        self.color_dict = color_dict
        self.color_persentage = color_persentage
        
    def file_initialization(self,root):
        if not os.path.exists(root):
            os.makedirs(root)
        return root + '/path.txt'
    
    # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 10->red, -1->unknow
    def add_color(self, grid_x, grid_y, color):
        if color == 'white':
            self.color_map[grid_y,grid_x] = 0
        elif color == 'brown':
            self.color_map[grid_y,grid_x] = 1
        elif color == 'purple':
            self.color_map[grid_y,grid_x] = 2
        elif color == 'green':
            self.color_map[grid_y,grid_x] = 3
        elif color == 'yellow':
            self.color_map[grid_y,grid_x] = 4
        elif color == 'black':
            self.color_map[grid_y,grid_x] = 5
        elif color == 'red':
            self.color_map[grid_y,grid_x] = 10
        elif color == 'unknow':
            self.color_map[grid_y,grid_x] = -1
    
    def init_coordinate(self, grid_width, grid_length):
        grid_tl_x = self.baseplate[0]
        grid_tl_y = self.baseplate[1]

        for y in range(self.num_grids_x):
            for x in range(self.num_grids_y):
                self.add_coordinate(x, y, grid_tl_x, grid_tl_y, grid_width[y], grid_length[x])
                grid_tl_y += grid_length[x]
            grid_tl_x += grid_width[y]
            # print(grid_tl_y)
            grid_tl_y = self.baseplate[1]

    # tl_x, tl_y, br_x, br_y
    def add_coordinate(self, grid_x, grid_y, tl_x, tl_y, width, length):
        self.coordinate_map[grid_y,grid_x,0] = tl_x
        self.coordinate_map[grid_y,grid_x,1] = tl_y
        self.coordinate_map[grid_y,grid_x,2] = tl_x + width
        self.coordinate_map[grid_y,grid_x,3] = tl_y + length

    # cv2 version
    def color_detector(self, hsv, blur, tl_x, tl_y, br_x, br_y):
        total = (br_x - tl_x) * (br_y - tl_y)
        unknow_flag = -1
        for index in range(len(self.color_persentage)):
            # mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
            # mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
            # mask = cv2.bitwise_or(mask1, mask2)
            mask = cv2.inRange(hsv, self.color_range[index * 2], self.color_range[index * 2 + 1])
            res = cv2.bitwise_and(blur, blur, mask = mask)
            # print(res[tl_y:br_y, tl_x:br_x])
            # color_num = np.count_nonzero(res[tl_y:br_y + 1, tl_x:br_x + 1])
            if (np.count_nonzero(res[tl_y:br_y, tl_x:br_x]) / 3) >= (self.color_persentage[index] * total):  
                unknow_flag = index
                break
        return self.color_dict[unknow_flag]

    # read new frame
    def reload_image(self, image):
        blurred_image = cv2.GaussianBlur(image, (1,1), cv2.BORDER_DEFAULT)
        hsv_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)
        for y in range(self.num_grids_y):
            for x in range(self.num_grids_x):
                color = self.color_detector(hsv_image, blurred_image, 
                                            self.coordinate_map[y,x,0],
                                            self.coordinate_map[y,x,1], self.coordinate_map[y,x,2],
                                            self.coordinate_map[y,x,3])
                self.add_color(x, y, color)

    # generate margin with a width equals 1
    def margin_detector(self, grid_x, grid_y):
        grid_up = grid_right = grid_bottom = grid_left = -1
        # top-left grid (2 by 2 grids for calibration)
        if self.color_map[grid_y, grid_y] == 2:
            pass
        else:
            if grid_x - 1 < 0 and grid_y - 1 < 0:
                # self.color_map[grid_y, grid_x] = 1
                grid_bottom = self.color_map[grid_y + 1, grid_x]
                grid_right = self.color_map[grid_y, grid_x + 1]

            # top-right grid (2 by 2 grids for calibration)
            elif grid_x + 2 > self.num_grids_x and grid_y - 1 < 0:
                # self.color_map[grid_y, grid_x] = 1
                grid_bottom = self.color_map[grid_y + 1, grid_x]
                grid_left = self.color_map[grid_y, grid_x - 1]

            # bottom-right grid (2 by 2 grids for calibration)
            elif grid_x + 2 > self.num_grids_x and grid_y + 2 > self.num_grids_y:
                # self.color_map[grid_y, grid_x] = 1
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_left = self.color_map[grid_y, grid_x - 1]

            # bottom-left grid (2 by 2 grids for calibration)
            elif grid_x - 1 < 0 and grid_y + 2 > self.num_grids_y:
                # self.color_map[grid_y,grid_x] = 1
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_right = self.color_map[grid_y, grid_x + 1]

            # if the grid in on the edge of the board
            # left edge
            elif grid_y - 1 < 0:
                grid_bottom = self.color_map[grid_y + 1, grid_x]
                grid_left = self.color_map[grid_y, grid_x - 1]
                grid_right = self.color_map[grid_y, grid_x + 1]
            # up edge
            elif grid_x - 1 < 0:
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_right = self.color_map[grid_y, grid_x + 1]
                grid_bottom = self.color_map[grid_y + 1, grid_x]
            # right edge
            elif grid_x + 1 >= self.num_grids_x:
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_left = self.color_map[grid_y, grid_x - 1]
                grid_bottom = self.color_map[grid_y + 1, grid_x]
            # bottom edge
            elif grid_y + 1 >= self.num_grids_y:
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_right = self.color_map[grid_y, grid_x + 1]
                grid_left = self.color_map[grid_y, grid_x - 1]
            else:
                grid_up = self.color_map[grid_y - 1, grid_x]
                grid_bottom = self.color_map[grid_y + 1, grid_x]
                grid_left = self.color_map[grid_y, grid_x - 1]
                grid_right = self.color_map[grid_y, grid_x + 1]
            # print(grid_up, grid_right, grid_bottom, grid_left)
        return grid_up, grid_right, grid_bottom, grid_left

    def soft_margin(self, grid_x, grid_y):
        up, right, bottom, left = self.margin_detector(int(grid_x), int(grid_y))
        if up == -1 and right == -1 and bottom == -1 and left == -1:
            pass
        elif up == right and up != (-1 or 0) and right != (-1 or 0):
            # if self.color_map[grid_y - 1, grid_x] != 2:
            self.color_map[grid_y, grid_x] = self.color_map[grid_y - 1, grid_x]
        elif right == bottom and right != (-1 or 0) and bottom != (-1 or 0):
            # if self.color_map[grid_y, grid_x + 1] != 2:
            self.color_map[grid_y, grid_x] = self.color_map[grid_y, grid_x + 1]
        elif bottom == left and bottom != (-1 or 0) and left != (-1 or 0):
            # if self.color_map[grid_y + 1, grid_x] != 2:
            self.color_map[grid_y, grid_x] = self.color_map[grid_y + 1, grid_x]
        elif left == up and left != (-1 or 0) and up != (-1 or 0):
            # if self.color_map[grid_y, grid_x - 1] != 2:
            self.color_map[grid_y, grid_x] = self.color_map[grid_y, grid_x - 1]
        # if islated by white block
        elif (up and right and bottom == 0) or (up and right and left == 0) or \
        (up and bottom and left == 0) or (right and bottom and left == 0):
            self.color_map[grid_y, grid_x] = 0
        else:
            pass
    
    # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 10->red, -1->unknow
    def building_clustering(self):
        backup = np.empty((self.num_grids_y, self.num_grids_x, 3), dtype = int)
        for x in range(self.num_grids_x):
            for y in range(self.num_grids_y):
                backup[y, x, 0:2] = y, x
        backup[...,2] = self.color_map
        # delete background color, road color, and calibration color
        no_background = backup[backup[...,2] > 2]
        # DBSCAN clustering
        dbscan = DBSCAN(eps = 1, min_samples = 2)
        building_labels = dbscan.fit_predict(no_background)
        self.building_clusters = max(building_labels) + 1
        for cluster_num in range(self.building_clusters):
            # print('cluster_num', cluster_num)
            origin_building_cluster = np.empty((1,3), dtype = int)
            for index in range(len(building_labels)):
                if building_labels[index] == cluster_num:
                    origin_building_cluster = np.append(origin_building_cluster, 
                                                        np.array(no_background[index]).reshape(1,3), axis = 0)
            # delete the first row generated by np.empty
            building_cluster = np.delete(origin_building_cluster, 0, 0)
            # print('cluster', cluster)
            y_min = min(building_cluster[:,0])
            y_max = max(building_cluster[:,0])
            x_min = min(building_cluster[:,1])
            x_max = max(building_cluster[:,1])
            color_tag = building_cluster[0,2]
            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    # print('x_coor, y_coor', x, y)
                    # print('color_tag', color_tag)
                    self.color_map[y,x] = color_tag
        print('all constructures are auto-constructed (road and background excluded)')
    
#     # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 10->red, -1->unknow
#     def road_vertex_detector(self, grid_x, grid_y):
#         # check top, right, bottom, and right
#         if (self.color_map[grid_y - 1, grid_x] > 2) or (self.color_map[grid_y, grid_x + 1] > 2) or \
#         (self.color_map[grid_y + 1, grid_x] > 2) or (self.color_map[grid_y, grid_x - 1] > 2):
#             return True
        
#     def lane_number_detector(self, r_v):
#         l_n = 1
#         for index in range(1, r_v.shape[0]):
#             if (r_v[index, 0] == r_v[0, 0] and abs(r_v[index, 1] - r_v[0, 1]) <= 3) or \
#             (r_v[index, 1] == r_v[index, 1] and abs(r_v[index, 0] - r_v[0, 0]) <= 3):
#                 l_n += 1
#         return int(l_n / 2)
    
#     def inflection_detector(self, grid_x, grid_y):
#         turn_number = 0
#         # check top, right, bottom, and right
#         if self.color_map[grid_y - 1, grid_x] == 2:
#             turn_number += 1
#         if self.color_map[grid_y, grid_x + 1] == 2:
#             turn_number += 1
#         if self.color_map[grid_y + 1, grid_x] == 2:
#             turn_number += 1
#         if self.color_map[grid_y, grid_x - 1] == 2:
#             turn_number += 1
#         if turn_number == 2 or turn_number == 4:
#             return True
    
#     def lane_render(self, default_width=1):
#         # default_width = 1 means 
#         backup = np.empty((self.num_grids_y, self.num_grids_x, 3), dtype = int)
#         for x in range(self.num_grids_x):
#             for y in range(self.num_grids_y):
#                 backup[y, x, 0:2] = y, x
#         backup[...,2] = self.color_map
#         no_background = backup[backup[...,2] == 2]
#         for x in range(self.num_grids_x-default_width):
#             least_check_time = default_width - 1
#             start_grid = end_grid = 0
#             while end_grid != num_grids_y - 1:
                
                
            
    
#     def inflection_expension(self, grid_x, grid_y):
    
#     # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 10->red, -1->unknow
#     # only clustering the road
#     def road_clustering(self):
#         backup = np.empty((self.num_grids_y, self.num_grids_x, 3), dtype = int)
#         for x in range(self.num_grids_x):
#             for y in range(self.num_grids_y):
#                 backup[y, x, 0:2] = y, x
#         backup[...,2] = self.color_map
#         # delete background color, road color, and calibration color
#         no_background = backup[backup[...,2] == 2]
#         # DBSCAN clustering
#         dbscan = DBSCAN(eps = 1, min_samples = 2)
#         road_labels = dbscan.fit_predict(no_background)
#         self.road_clusters = max(road_labels) + 1
#         for cluster_num in range(self.road_clusters):
#             # print('cluster_num', cluster_num)
#             origin_road_cluster = np.empty((1,3), dtype = int)
#             for index in range(len(road_labels)):
#                 if road_labels[index] == cluster_num:
#                     origin_road_cluster = np.append(origin_road_cluster, 
#                                                     np.array(no_background[index]).reshape(1,3), 
#                                                     axis = 0)
#             # each road cluster
#             # delete the first row generated by np.empty
#             road_cluster = np.delete(origin_road_cluster, 0, 0)
            
#             # find road vertex and inflection
#             origin_road_vertex = np.empty((1,2), dtype = int)
#             origin_road_inflection = np.empty((1,2), dtype = int)
#             for index in range(road_cluster.shape[0]):
#                 if self.road_vertex_detector(road_cluster[index,1], road_cluster[index,0]) == True:
#                     origin_road_vertex = np.append(origin_road_vertex, 
#                                                    np.array((road_cluster[index,0],
#                                                              road_cluster[index,1])).reshape(1,2), axis = 0)
#                 elif self.inflection_detector(road_cluster[index,1], road_cluster[index,0]) == True:
#                     origin_road_inflection = np.append(origin_road_inflection, 
#                                                    np.array((road_cluster[index,0],
#                                                              road_cluster[index,1])).reshape(1,2), axis = 0)
#                 else:
#                     pass
#             # delete the first row generated by np.empty
#             road_vertex = np.delete(origin_road_vertex, 0, 0)
#             road_inflection = np.delete(origin_road_inflection, 0, 0)
#             # print('road vertx', road_vertex)
#             # print('road inflection', road_inflection)
#             # road_point = (np.append(road_vertex, road_inflection)).reshape((-1,2))
            
#             # lane number
#             # one-way lane-based
#             ow_lane_number = self.lane_number_detector(road_vertex)
#             # two-way lane-based
#             total_lane_number = 2 * self.lane_number_detector(road_vertex)
            
#             # find the path from vertex to inflection
#             # create a path dict
#             # path_number = (road_vertex.shape[0]/total_lane_number) * ((road_vertex.shape[0]/total_lane_number) - 1) * ow_lane_number
#             path_number = int((road_vertex.shape[0]/2) * ((road_vertex.shape[0]/total_lane_number) - 1))

#             # path format - start -> inflection -> end
            
#             with open(self.path,'w+') as f:
#                 for path_index in range(path_number):
#                     # only support 1-lane right now
#                     # add origin-point of road
#                     temp_path = np.full((1,2),-1)
#                     # type flag
#                     # left-right format -> 0
#                     # up-bottom format -> 1
#                     type_flag = 0
#                     for lane_index in range(ow_lane_number):
#                         # left-right format
#                         index = path_index * 2 + lane_index
#                         if road_vertex[index, 1] == road_vertex[index + ow_lane_number, 1]:
#                             temp_path[0,:] = [max(road_vertex[index, 0],
#                                                   road_vertex[index + ow_lane_number, 0]), road_vertex[index, 1]]
#                         # up-bottom format
#                         elif road_vertex[index, 0] == road_vertex[index + ow_lane_number, 0]:
#                             temp_path[0,:] = [road_vertex[index, 0], 
#                                               max(road_vertex[index, 1],road_vertex[index + ow_lane_number, 1])]
#                             type_flag = 1
#                         else:
#                             pass
#                     # extend path from origin-point
#                     # no inflection
#                     if len(road_inflection) == 0:
#                         for connection in road_vertex:
#                             match = temp_path[-1,:] == connection
#                             if np.any(match):
#                                 if connection[0] == temp_path[0,0] and connection[1] == temp_path[0,1]:
#                                     pass
#                                 elif type_flag == 0 and connection[1] == temp_path[0,1] and first_match == 0:
#                                     pass
#                                 elif type_flag == 1 and connection[0] == temp_path[0,0] and first_match == 0:
#                                     pass
#                                 else:
#                                     temp_path = (np.append(temp_path, connection)).reshape(-1,2)
#                     # has inflections
#                     else:
#                         break_flag = 0
#                         temp_inflection = road_inflection
#                         while break_flag == 0:
#                             break_flag = 1
#                             for index in range(temp_inflection.shape[0]):
#                                 match = temp_path[-1,:] == temp_inflection[index,:]
#                                 if np.any(match):
#                                     if temp_inflection[index][0] == temp_path[0,0] and temp_inflection[index][1] == temp_path[0,1]:
#                                         pass
#                                     elif type_flag == 0 and temp_inflection[index][1] == temp_path[0,1] and first_match == 0:
#                                         pass
#                                     elif type_flag == 1 and temp_inflection[index][0] == temp_path[0,0] and first_match == 0:
#                                         pass
#                                     else:
#                                         temp_path = (np.append(temp_path, temp_inflection[index,:])).reshape(-1,2)
#                                         temp_inflection = np.delete(temp_inflection, index, 0)
#                                         break_flag = 0
#                                         break
#                         for connection in road_vertex:
#                             # print('last one', temp_path[-1,:])
#                             match = temp_path[-1,:] == connection
#                             if np.any(match):
#                                 if connection[0] == temp_path[0,0] and connection[1] == temp_path[0,1]:
#                                     pass
#                                 elif type_flag == 0 and connection[1] == temp_path[0,1] and first_match == 0:
#                                     pass
#                                 elif type_flag == 1 and connection[0] == temp_path[0,0] and first_match == 0:
#                                     pass
#                                 else:
#                                     temp_path = (np.append(temp_path, connection)).reshape(-1,2)
#                                     break
#                     for index in range(len(temp_path)):
#                         print('%d %d' % (temp_path[index,0], temp_path[index,1]), file = f)
#                     print('%d %d' % (-1, -1), file = f)
#                     print('path:', temp_path)
        
    # draw the urban structure including buildings and road links, which are extinguished by color and capacity
    # capacity is specified by the building type and size/depth
    
    def urban(self):
        # transfer BGR to RGB
        self.grid_image = cv2.cvtColor(self.grid_image, cv2.COLOR_BGR2RGB)
        # cv2.rectangle(grid_image, (0,0), (bg_width,bg_length), (220,220,220), -1)
        # cv2.rectangle(grid_image, (0,0), (bg_width,bg_length), (0,0,0), -1)
        cv2.rectangle(self.grid_image, (self.baseplate[0], self.baseplate[1]), 
                      (self.baseplate[0] + self.baseplate[2], self.baseplate[1] + self.baseplate[3]), 
                      (255,255,255), -1)
        
        for y in range(self.num_grids_y):
            for x in range(self.num_grids_x):
                # adopte soft margin detector
                self.soft_margin(x, y)
        
        self.building_clustering()
    
    def urban_pure(self):
        # transfer BGR to RGB
        self.grid_image = cv2.cvtColor(self.grid_image, cv2.COLOR_BGR2RGB)
        # cv2.rectangle(grid_image, (0,0), (bg_width,bg_length), (220,220,220), -1)
        # cv2.rectangle(grid_image, (0,0), (bg_width,bg_length), (0,0,0), -1)
        cv2.rectangle(self.grid_image, (self.baseplate[0], self.baseplate[1]), 
                      (self.baseplate[0] + self.baseplate[2], self.baseplate[1] + self.baseplate[3]), 
                      (255,255,255), -1)

    def draw(self):
        # grid_image = cv2.cvtColor(grid_image, cv2.COLOR_BGR2RGB)
        for y in range(self.num_grids_y):
            for x in range(self.num_grids_x):
                # draw the color
                if self.color_map[y,x] == 0:
                    grid_color = (255,255,255)   # white
                elif self.color_map[y,x] == 1:
                    grid_color = (50,127,205)   # brown
                elif self.color_map[y,x] == 2:
                    grid_color = (128,0,128)   # purple
                elif self.color_map[y,x] == 3:
                    grid_color = (50,205,50)   # green
                elif self.color_map[y,x] == 4:
                    grid_color = (0,191,255)   # yellow
                elif self.color_map[y,x] == 5:
                    grid_color = (0,0,0)   # black
                elif self.color_map[y,x] == 10:
                    grid_color = (32,0,128)   # red
                else:
                    grid_color = (255,255,255)   # unknow->blue
                # print(self.coordinate_map[y,x])
                # BGR format
                cv2.rectangle(self.grid_image, 
                            (int(self.coordinate_map[y,x,0]),int(self.coordinate_map[y,x,1])), 
                            (int(self.coordinate_map[y,x,2]), int(self.coordinate_map[y,x,3])), 
                            grid_color, -1)
                # draw the scratch of rectangles
                # cv2.rectangle(grid_image, (int(self.coordinate_map[y,x,0]),int(self.coordinate_map[y,x,1])), 
                        # (int(self.coordinate_map[y,x,2]), int(self.coordinate_map[y,x,3])), grid_color, 1)         
        
    def color_accumulate(self, previous_color_map):
        for y in range(self.num_grids_y):
            for x in range(self.num_grids_x):
                # draw the color
                # 0->white, 1->brown, 2->purple, 3->green, 4->yellow, 5->black, 6->red, 7->unknow
                if previous_color_map[y,x] != 0 and previous_color_map[y,x] != 2:
                    if self.color_map[y,x] == 0:
                        self.color_map[y,x] = previous_color_map[y,x]
    
    def add_mesh(self, point_cloud, depth):
        mesh_list = []

        for x in range(self.num_grids_x):
            for y in range(self.num_grids_y):
                if self.color_map[y,x] == 2:
                    height = 1
                    color = [0.5, 0, 0.5]
                elif self.color_map[y,x] == 3:
                    height = distanc_cal(x+2, y+2, point_cloud, depth)
                    color = [0, 1, 0]
                elif self.color_map[y,x] == 4:
                    height = distanc_cal(x+2, y+2, point_cloud, depth)
                    color = [1, 1, 0]
                elif self.color_map[y,x] == 1:
                    height = distanc_cal(x+2, y+2, point_cloud, depth)
                    color = [0.6, 0.3, 0]
                elif self.color_map[y,x] == 10:
                    height = distanc_cal(x+2, y+2, point_cloud, depth)
                    color = [1,0,0]
                else:
                    height = 1
                    color = [0.9, 0.9, 0.9]
                tl = [self.coordinate_map[y,x,0],self.coordinate_map[y,x,1],0]
                tr = [self.coordinate_map[y,x,0],self.coordinate_map[y,x,3],0]
                br = [self.coordinate_map[y,x,2],self.coordinate_map[y,x,3],0]
                bl = [self.coordinate_map[y,x,2],self.coordinate_map[y,x,1],0]
                bottom_corners = np.array([tl,tr,br,bl])
                
                cuboid = create_cuboid(bottom_corners, height)
                cuboid.paint_uniform_color(color)
                mesh_list.append(cuboid)
        return mesh_list