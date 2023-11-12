import numpy as np
from point import Point
import drowdxf


frame = [
  [34262, 19199],
  [-40496, 19256],
  [-40505, -2442],
  [34262, 19199]
  ]

search_frame = [
  Point(0,0),
  Point(300,0),
  Point(300,100),
  Point(0,100),
]

target_area = 100


def debug_main():
  # 判定領域

  drowdxf.drowLine_by_point(search_frame)


debug_main()

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
    search_frame (list): _探索領域のArray
    search_line (list): _探索対象の線分

  Returns:
    max (float): _最大値
    min (float): _最小値
  """
  max = Point(10,10)
  min = Point(0,0)

  # 判定軸上の座標取得
  # Get_vertical_intersection()

  return max, min


# 2分探索をするよ
# 探索領域のArr
# 奥行ベクトル
# 目標面積
def binary_search(search_frame, search_range ,move_line, target_area):
  """二分探索を行う関数

  Args:
    search_frame (list): _探索領域のArray
    search_range (list): 探索軸の最大最小
    move_line (vector): _奥行ベクトル
    target_area (int): _その時点の目標面積

  Returns:
    binary_point (list): _二分探索結果の座標
  """
  print("binary_search")
  return 


# 判定軸上指定した点から，奥行ベクトルを伸ばし，一時的な区画を取得する
def get_tmp_parcel(search_frame,move_line,point):
  """判定軸上指定した点から，奥行ベクトルを伸ばし，一時的な区画を取得する

  Args:
    search_frame (list): _探索領域のArray
    move_line (list): _探索対象の線分
    point (Point): _判定軸上の指定した点

  Returns:
    pointlist (Pointlist): _作成した図形の集合
  """
  # TODO: search_frameと，pointから引いたmove_lineの交点求める

  # TODO: 取得した交点を使って，区画のPoint配列取得
  # return pointlist

# 直線AB上の点Pから垂直に落とした点を求める
def Get_vertical_intersection(O, A, B):
  """直線AB上の点Pから垂直に落とした点を求める

  Args:
    O (list): _AとBの二点のリスト
    A (list): _奥行ベクトル
    B (list): _奥行ベクトル

  Returns:
    point_on_judge_line (Point): _判定軸上の点
  """
  print("Get_vertical_intersection")
  OA = Point(A.x - O.x, A.y - O.y)
  OB = Point(B.x - O.x, B.y - O.y)

  k = np.dot(OA, OB) / (np.linalg.norm(OA) ** 2)
  OP = k * OA
  point_on_judge_line =  Point(OP.x + O.x, OP.y + O.y)
  return point_on_judge_line