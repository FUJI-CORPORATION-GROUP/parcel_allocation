import numpy as np
from point import Point
import Calc
import draw_dxf

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
    def get_tmp_frame(self, point_A, point_B, min_point, count,calc_count):
    # def get_tmp_frame(self, point_A, point_B):
      """探索領域を直線ABで区切り,区画と残りの探索領域を取得する

      Args:
          point_A (Point): _description_
          point_B (Point): _description_
          min_point (Point): _探索範囲の最小値_

      Returns:
          parcel_frame (Frame): _区画_
          remain_frame (Frame): _残りの探索領域_
      """
      point_list_A = []
      point_list_B = []
      point_A = Point((point_A.x + point_B.x),(point_A.y + point_B.y))

      get_frame_flag = True
      for i in range(len(self.points)):
        point_s = self.points[i]
        point_e = self.points[i + 1] if(i+1<len(self.points)) else self.points[0]
        line_cross = Calc.line_cross_point(point_s, point_e, point_A, point_B, count,calc_count)
        
        if(get_frame_flag):
          point_list_A.append(point_s)
        else:
          point_list_B.append(point_s)
        
        if (line_cross != None):
          point_list_A.append(line_cross)
          point_list_B.append(line_cross)
          get_frame_flag = not get_frame_flag
      
      
      tmp_frame_A = Frame(point_list_A)
      tmp_frame_B = Frame(point_list_B)
      
      # どっちのFrameを採用するかの判定
      tmp_barycenter_A = tmp_frame_A.get_barycenter()
      tmp_barycenter_B = tmp_frame_B.get_barycenter()
      tmp_distance_A = tmp_barycenter_A.distance(min_point)
      tmp_distance_B = tmp_barycenter_B.distance(min_point)
      if(tmp_distance_A < tmp_distance_B):
        parcel_frame = tmp_frame_A
        remain_frame = tmp_frame_B
      else:
        parcel_frame = tmp_frame_B
        remain_frame = tmp_frame_A
      
      
      return parcel_frame, remain_frame
    
    def move_frame(self, point):
      for i in range(len(self.points)):
        self.points[i] = self.points[i].add(point)
      return self

    def debug_move_frame(self, point):
      debug_points = []
      for i in range(len(self.points)):
        debug_points.append(self.points[i].add(point))
      return Frame(debug_points)

    def get_points_str(self):
      str = ""
      for i in range(len(self.points)):
        str = f"{str} {self.points[i].get_str()}"
      return str
    
    def get_list_xy(self):
      list_x , list_y = [], []
      for i in range(len(self.points)):
        list_x.append(self.points[i].x)
        list_y.append(self.points[i].y)
      return list_x,list_y
    
    def move_positive(self):
      list_x, list_y = self.get_list_xy()
      min_x = abs(min(list_x)) if (min(list_x) < 0) else 0
      min_y = abs(min(list_y)) if (min(list_y) < 0) else 0
      
      move_positive_point = Point(min_x, min_y) 
      self = self.move_frame(move_positive_point)
    
    def move_zero(self):
      list_x, list_y = self.get_list_xy()
      min_x,min_y = min(list_x),min(list_y)
      move_zero_point = Point(-1 * min_x, -1 * min_y) 
      self = self.move_frame(move_zero_point)
    
    def get_barycenter(self):
      num_points = len(self.points)

      if num_points == 0:
          raise ValueError("pointsないよ")

      sum_x = sum(point.x for point in self.points)
      sum_y = sum(point.y for point in self.points)

      barycenter = Point(sum_x / num_points, sum_y / num_points)

      return barycenter