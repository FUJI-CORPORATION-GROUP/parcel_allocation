import math
import numpy as np
from point import Point
from frame import Frame
import drowdxf


frame = [
  [34262, 19199],
  [-40496, 19256],
  [-40505, -2442],
  [34262, 19199]
  ]

search_frame = Frame([
  Point(0,0),
  Point(300,0),
  Point(500,100),
  Point(100,100),
])

load_frame = [
  search_frame.points[0],
  search_frame.points[1]
]
target_area = 28000


def get_side_parcel():
  """端の区画割を行う関数

  Args:
    vecs (list): _枠のarray
    point (int): _点

  Returns:
    array: _交点の二点
  """

  # Point型への変換

  # 2分探索の探索軸の最大最小を種痘
  # search_range = get_search_range()

  # 2分探索で範囲取得
  # binary_search()

  # return 


# 探索軸の最大最小の取得
def get_search_range(search_frame, search_line):
  """探索軸の最大最小の取得

  Args:
    search_frame (frame): _探索領域のArray
    search_line (list): _探索対象の線分

  Returns:
    max (float): _最大値
    min (float): _最小値
  """
  search_frame = search_frame.points
  search_line_start_point = search_line[0]
  search_line_end_point = search_line[1]
  min = search_line_start_point
  max = search_line_end_point
  # 判定軸上の座標取得
  for i in range(len(search_frame)):
    point = Get_vertical_intersection(search_line_start_point,search_line_end_point,search_frame[i])
    
    default_distance = max.distance(min)
    
    max_distance = max.distance(point)
    min_distance = min.distance(point)
    
    if(default_distance != max_distance + min_distance):
      if(max_distance > min_distance):
        min = point
      else:
        max = point    
  
  return max, min


# 2分探索をするよ
# 探索領域のArr
# 奥行ベクトル
# 目標面積
def binary_search(search_frame, search_range ,move_line, target_area):
  """二分探索を行う関数

  Args:
    search_frame (Frame): _探索領域のArray
    search_range (list): 探索軸の最大最小
    move_line (Point): _奥行ベクトル
    target_area (int): _その時点の目標面積

  Returns:
    binary_point (Frame): _二分探索結果の座標
  """  
  first_min = search_range[0]
  farst_max = search_range[1]
  min = first_min
  max = farst_max
  tmp_point = Point.get_middle_point(max,min)
  calc_count = 0
  
  inc_point = Point(max.x - min.x, max.y - min.y).unit()
  dec_point = Point(min.x - max.x, min.y - max.y).unit()
  
  # 2分探索で適切な点を決定する
  while (first_min.distance(min) < first_min.distance(max)):
    # 中央値取得
    tmp_point = Point.get_middle_point(max,min)
    tmp_frame = get_tmp_parcel(search_frame, move_line, tmp_point)
    
    # プラス側
    tmp_inc_point = tmp_point.add(inc_point)
    tmp_inc_frame = get_tmp_parcel(search_frame, move_line, tmp_inc_point)
    
    # マイナス側
    tmp_dec_point = tmp_point.add(dec_point)
    tmp_dec_frame = get_tmp_parcel(search_frame, move_line, tmp_dec_point)
    
    # それぞれの目標値との差分を取得
    tmp_point_diff = math.fabs(target_area - tmp_frame.area)
    tmp_inc_point_diff = math.fabs(target_area - tmp_inc_frame.area)
    tmp_dec_point_diff = math.fabs(target_area - tmp_dec_frame.area)
    
    if(tmp_point_diff > tmp_inc_point_diff):
      min = tmp_point
    elif(tmp_point_diff > tmp_dec_point_diff):
      max = tmp_point
    else:
      break
    calc_count += 1
    
    if(calc_count > 50):
      print("計算回数過多")
      break
  
  # 決定した点で取得できるFrame取得
  final_frame = get_tmp_parcel(search_frame, move_line,tmp_point)
  
  print(f"2分探索酋長 計算回数:{calc_count} 回 面積:{final_frame.area} / 目標面積：{target_area}")
  return final_frame


# 判定軸上指定した点から，奥行ベクトルを伸ばし，一時的な区画を取得する
def get_tmp_parcel(search_frame, move_line, point):
  """判定軸上指定した点から，奥行ベクトルを伸ばし，一時的な区画を取得する

  Args:
    search_frame (list): _探索領域のArray
    move_line (list): _奥行を示す単位ベクトル
    point (Point): _判定軸上の指定した点

  Returns:
    pointlist (Pointlist): _作成した図形の集合
  """
  
  
  point_list = search_frame.get_tmp_frame(point, move_line)
  
  return point_list

# 直線AB上の点Pから垂直に落とした点Hを求める
def Get_vertical_intersection(A, B, P):
  """直線AB上の点Pから垂直に落とした点を求める

  Args:
    A (Point): _探索軸の始点
    B (Point): _探索軸の終点
    P (Point): _AとBの二点のリスト

  Returns:
    point_on_judge_line (Point): _判定軸上の点
  """
  AB = Point(B.x - A.x, B.y - A.y)
  AP = Point(P.x - A.x, P.y - A.y)

  k = Point.dot(AB, AP) / (AB.magnitude() ** 2)
  OH = Point(k * AB.x, k * AB.y)
  point_on_judge_line =  Point(OH.x + A.x, OH.y + A.y)
  return point_on_judge_line

def debug_main():
  # 判定領域
  # 探索軸の決定
  # search_frame = Frame(search_frame)
  search_line_start_point = load_frame[0]
  search_line_end_point = load_frame[1]
  search_line = [search_line_start_point,search_line_end_point]
  
  # 探索範囲の取得
  max, min = get_search_range(search_frame,search_line)
  search_line_range = [min, max]
    
  # 一時的なポイント処理
  # tmp_point = Point((min.x + max.x) / 2,(min.y + max.y) / 2)
  tmp_move_line = Point(0,50)
  tmp_parcel = binary_search(search_frame, search_line_range ,tmp_move_line, target_area)
  
  drowdxf.cleardxf()
  drowdxf.drowLine_by_point(search_frame.points)
  drowdxf.drowLine_by_point(search_line_range)
  drowdxf.drowLine_by_point_color(tmp_parcel.points,1)


debug_main()