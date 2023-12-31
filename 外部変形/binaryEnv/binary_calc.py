from point import Point

def line_cross_point(A, B, C, D, count, calc_count):
  """線分ABと直線CDの交点を返す

  Args:
      A (Point): 点Aの座標
      B (Point): 点Bの座標
      C (Point): 点Cの座標
      D (Point): 点Dの座標
      count (int): 交点計算回数
      calc_count (int): 2分探索探索回数

  Returns:
      _type_: _description_
  """
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
  if(A.x <= P.x <= B.x and A.y <= P.y <= B.y) or (A.x >= P.x >= B.x and A.y >= P.y >= B.y) or (A.x <= P.x <= B.x and A.y >= P.y >= B.y) or (A.x >= P.x >= B.x and A.y <= P.y <= B.y):
    return P

# 渡されたframeの面積を計算する関数
def calc_area(frame):
  """渡されたframeの面積を計算する関数

  Args:
      frame (Frame): 面積を計算するframe

  Returns:
      float: frameの面積
  """
  frame = frame.points
  area = 0
  for i in range(len(frame)):
      area += (frame[i].x * frame[0].y - frame[i].y * frame[0].x) / 2 if i == len(frame) - 1 else (frame[i].x * frame[i + 1].y - frame[i].y * frame[i + 1].x) / 2
  return abs(area)

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