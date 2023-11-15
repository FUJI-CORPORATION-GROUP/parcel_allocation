import numpy as np
from point import Point
import Calc

class Frame:
    """区画を扱うクラス

    functions:
        distance (list, list): _距離同士の距離を求める
        point_to_line_distance (list, list, list): _点と直線の距離公式

    """
    points = []
    area = 0

    def __init__(self, points):
      self.points = points
      self.area = Calc.calc_area(self)

    # 直線ABで区切られる区画を返す
    def get_tmp_frame(self, point_A, point_B):
      tmp_points = []
      
      point_B = Point((point_A.x + point_B.x),(point_A.y + point_B.y))
      get_frame_flag = True
      for i in range(len(self.points)):
        point_s = self.points[i]
        point_e = self.points[i + 1] if(i+1<len(self.points)) else self.points[0]
        line_cross = Calc.line_cross_point(point_s, point_e, point_A, point_B)
        
        if(get_frame_flag):
          tmp_points.append(point_s)
        
        if (line_cross != None):
          tmp_points.append(line_cross)
          get_frame_flag = not get_frame_flag
      
      tmp_frame = Frame(tmp_points)
      
      return tmp_frame


# search_frame = [
#   Point(0,0),
#   Point(300,0),
#   Point(500,100),
#   Point(100,100),
# ]
# search_frame = Frame(search_frame)
# print(search_frame.area)