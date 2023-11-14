import numpy as np
from point import Point

# 線分ABと直線CDの交点
def line_cross_point(A, B, C, D):
  AB = Point((B.x - A.x), (B.y - A.y))
  CD = Point((D.x - C.x), (D.y - C.y))
  d = AB.x*CD.y - CD.x*AB.y
  if d == 0:
    # 並行の場合
    return None
  # 交点計算
  sn = CD.y * (C.x-A.x) - CD.x * (C.y-A.y)
  x = A.x + AB.x*sn/d
  y = A.y + AB.y*sn/d
  P = Point(x,y)
  if(A.distance(B) ==  (P.distance(A) + P.distance(B))):
    return P


class Frame:
    """区画を扱うクラス

    functions:
        distance (list, list): _距離同士の距離を求める
        point_to_line_distance (list, list, list): _点と直線の距離公式

    """
    points = []

    def __init__(self, points):
      self.points = points

    def get_cross_points(self, point_A, point_B):
      tmp_points = []
      point_B = Point((point_A.x + point_B.x),(point_A.y + point_B.y))
      for i in range(len(self.points)):
        point_s = self.points[i]
        point_e = self.points[i + 1] if(i+1<len(self.points)) else self.points[0]
        line_cross = line_cross_point(point_s, point_e, point_A, point_B)
        if (line_cross != None):
          tmp_points.append(line_cross)
      
      return tmp_points