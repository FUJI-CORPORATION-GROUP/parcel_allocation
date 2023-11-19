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

# 渡されたframeの面積を計算する関数
def calc_area(frame):
    frame = frame.points
    area = 0
    for i in range(len(frame)):
        area += (frame[i].x * frame[0].y - frame[i].y * frame[0].x) / 2 if i == len(frame) - 1 else (frame[i].x * frame[i + 1].y - frame[i].y * frame[i + 1].x) / 2
    return abs(area)