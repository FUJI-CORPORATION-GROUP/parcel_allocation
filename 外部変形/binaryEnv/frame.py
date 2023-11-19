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
      """探索領域を直線ABで区切り,区画と残りの探索領域を取得する

      Args:
          point_A (Point): _description_
          point_B (Point): _description_

      Returns:
          parcel_frame (Frame): _区画_
          remain_frame (Frame): _残りの探索領域_
      """

      parcel_points = []
      remain_frame_points = []
      
      point_B = Point((point_A.x + point_B.x),(point_A.y + point_B.y))
      get_frame_flag = True
      for i in range(len(self.points)):
        point_s = self.points[i]
        point_e = self.points[i + 1] if(i+1<len(self.points)) else self.points[0]
        line_cross = Calc.line_cross_point(point_s, point_e, point_A, point_B)
        
        if(get_frame_flag):
          parcel_points.append(point_s)
        else:
          remain_frame_points.append(point_s)
        
        if (line_cross != None):
          parcel_points.append(line_cross)
          remain_frame_points.append(line_cross)
          get_frame_flag = not get_frame_flag
      
      parcel_frame = Frame(parcel_points)
      remain_frame = Frame(remain_frame_points)
      
      return parcel_frame, remain_frame
    
    def move_frame(self, point):
      for i in range(len(self.points)):
        self.points[i] = self.points[i].add(point)
      return self

    def get_points_str(self):
      str = ""
      for i in range(len(self.points)):
        str = f"{str} {self.points[i].get_str()}"
      return str


# search_frame = [
#   Point(0,0),
#   Point(300,0),
#   Point(500,100),
#   Point(100,100),
# ]
# search_frame = Frame(search_frame)
# print(search_frame.area)