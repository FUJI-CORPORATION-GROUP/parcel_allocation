from components.point import Point


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
    d = AB.x * CD.y - CD.x * AB.y
    if d == 0:
        # 並行の場合
        return None
    # 交点計算
    sn = CD.y * (C.x - A.x) - CD.x * (C.y - A.y)
    x = A.x + AB.x * sn / d
    y = A.y + AB.y * sn / d
    P = Point(x, y)
    # 線分上判定
    if (
        (A.x <= P.x <= B.x and A.y <= P.y <= B.y)
        or (A.x >= P.x >= B.x and A.y >= P.y >= B.y)
        or (A.x <= P.x <= B.x and A.y >= P.y >= B.y)
        or (A.x >= P.x >= B.x and A.y <= P.y <= B.y)
    ):
        return P
    else:
        return None


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
        area += (
            (frame[i].x * frame[0].y - frame[i].y * frame[0].x) / 2
            if i == len(frame) - 1
            else (frame[i].x * frame[i + 1].y - frame[i].y * frame[i + 1].x) / 2
        )
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
    point_on_judge_line = Point(OH.x + A.x, OH.y + A.y)
    return point_on_judge_line


# frameと奥行ベクトルから，探索領域を求める
def Get_search_frame(
    target_frame, search_depth_distance, road_start_point, road_end_point
):
    # 道路方向ベクトル取得
    # TODO:0番目しかないと仮定．今後の入力形態に入力形態によって変更
    road_vec = road_start_point.sub(road_end_point)

    # 奥行ベクトル
    search_depth_vec = Point(-1 * road_vec.y, road_vec.x).mul(search_depth_distance)

    # 切り出すための直線の始点と終点
    A = road_start_point.add(search_depth_vec)
    B = road_end_point.add(search_depth_vec)

    get_search_frame_flag = True
    search_point_list = []

    for i in range(len(target_frame.points)):
        # 直線ABとtarget_frameの辺の交点を求める
        the_point = target_frame.points[i]
        the_next_point = target_frame.points[(i + 1) % len(target_frame.points)]
        cross_point = line_cross_point(A, B, the_point, the_next_point, 0, 0)

        if get_search_frame_flag:
            search_point_list.append(the_point)

        if cross_point is not None:
            search_point_list.append(cross_point)
            get_search_frame_flag = False

        search_frame = Frame(search_point_list)
    return search_frame
