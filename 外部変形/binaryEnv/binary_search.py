import math
from components.point import Point
from components.frame import Frame
import binary_calc as Calc
import draw_dxf


def get_side_parcel(search_frame, load_frame, target_area, move_line, count):
    """探索領域を直線ABで区切り,区画と残りの探索領域を取得する

    Args:
        search_frame (frame): _探索領域
        load_frame (list[Point]): _道路と接する選
        target_area (int): _目標面積
        move_line(Point): _奥行ベクトル
        count (int): _住戸確保回数

    Returns:
        parcel_frame(Frame): _2分探索で確保した区画
        remain_frame(Frame): _残りの区画
    """

    # 探索軸の決定
    # TODO: 2本より多い道路の場合の決定方法について検討&実装
    search_line_start_point = load_frame.points[0]
    search_line_end_point = load_frame.points[1]
    search_line = [search_line_start_point, search_line_end_point]

    # 探索範囲の取得
    max, min = get_search_range(search_frame, search_line, count)
    search_line_range = [min, max]

    # 一時的なポイント処理
    parcel_frame, remain_frame = binary_search(
        search_frame, search_line_range, move_line, target_area, count
    )
    return parcel_frame, remain_frame


# 探索軸の最大最小の取得
def get_search_range(search_frame, search_line, count):
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
    # TODO: minとmaxの初期化
    max, min = search_line_start_point, search_line_end_point

    point_list_on_line = []

    # 判定軸上の座標取得
    for i in range(len(search_frame)):
        point = Calc.Get_vertical_intersection(
            search_line_start_point, search_line_end_point, search_frame[i]
        )
        point_list_on_line.append(point)

    distance_max_A = 0
    for i in range(len(point_list_on_line)):
        distance = point_list_on_line[i].distance(point_list_on_line[0])
        if distance > distance_max_A:
            distance_max_A = distance
            point_A = point_list_on_line[i]

    distance_max_B = 0
    for i in range(len(point_list_on_line)):
        distance = point_list_on_line[i].distance(point_A)
        if distance > distance_max_B:
            distance_max_B = distance
            point_B = point_list_on_line[i]

    search_line_vec = Point.sub(search_line_end_point, search_line_start_point)
    edge_line_AB_vec = Point.sub(point_B, point_A)

    if search_line_vec.dot(edge_line_AB_vec) < 0:
        max = point_A
        min = point_B
    else:
        max = point_B
        min = point_A

    return max, min


# 2分探索をするよ
# 探索領域のArr
# 奥行ベクトル
# 目標面積
def binary_search(search_frame, search_range, move_line, target_area, count):
    """二分探索を行う関数

    Args:
      search_frame (Frame): _探索領域のArray
      search_range (list): 探索軸の最大最小
      move_line (Point): _奥行ベクトル
      target_area (int): _その時点の目標面積
      count (int): _住戸確保回数

    Returns:
      binary_point (Frame): _二分探索結果の座標
    """
    first_min = search_range[0]
    first_max = search_range[1]
    min = first_min
    max = first_max
    tmp_point = Point.get_middle_point(max, min)
    calc_count = 0

    # TODO: 小さすぎると反映されない
    inc_point = Point(max.x - min.x, max.y - min.y).unit()
    dec_point = Point(min.x - max.x, min.y - max.y).unit()

    # 2分探索で適切な点を決定する
    while first_min.distance(min) < first_min.distance(max):
        # 中央値取得
        tmp_point = Point.get_middle_point(max, min)
        tmp_frame = Frame.get_tmp_frame(
            search_frame, move_line, tmp_point, first_min, first_max, count, calc_count
        )[0]

        # プラス側
        tmp_inc_point = tmp_point.add(inc_point)
        tmp_inc_frame = Frame.get_tmp_frame(
            search_frame,
            move_line,
            tmp_inc_point,
            first_min,
            first_max,
            count,
            calc_count,
        )[0]

        # マイナス側
        tmp_dec_point = tmp_point.add(dec_point)
        tmp_dec_frame = Frame.get_tmp_frame(
            search_frame,
            move_line,
            tmp_dec_point,
            first_min,
            first_max,
            count,
            calc_count,
        )[0]

        # それぞれの目標値との差分を取得
        tmp_point_diff = math.fabs(target_area - tmp_frame.area)
        tmp_inc_point_diff = math.fabs(target_area - tmp_inc_frame.area)
        tmp_dec_point_diff = math.fabs(target_area - tmp_dec_frame.area)

        calc_count += 1
        if tmp_point_diff > tmp_inc_point_diff:
            min = tmp_point
        elif tmp_point_diff > tmp_dec_point_diff:
            max = tmp_point
        else:
            break

        if calc_count > 50:
            print("計算回数過多")
            break

    # 決定した点で取得できるFrame取得
    parcel_frame, remain_frame = Frame.get_tmp_frame(
        search_frame, move_line, tmp_point, first_min, first_max, count, calc_count
    )

    print(
        f"探索終了 計算回数:{calc_count}回 比率：{math.floor(int(parcel_frame.area) / int (target_area)*1000) / 1000}  面積:{math.floor(int(parcel_frame.area)/1000000*1000)/1000}㎡ / 目標面積：{int (target_area)/1000000}㎡"
    )
    return parcel_frame, remain_frame


# デバッグ用メイン関数
def debug_main():
    """2分探索デバッグ用メイン関数

    Returns:
        Frame[]: 2分探索した結果の区画のリスト
    """

    binary_parcel_list = []

    move_line = Point(0, 50)
    search_frame = Frame(
        [
            Point(0, 0),
            Point(300, 0),
            Point(500, 100),
            Point(100, 100),
        ]
    )
    load_frame = [search_frame.points[0], search_frame.points[1]]

    # DEX準備
    draw_dxf.clear_dxf()
    draw_dxf.draw_line_by_point(search_frame.points)

    target_area = 9000
    count = 0

    print(f"search_frame : {search_frame.get_points_str()}")

    # 探索領域が目標面積取れなくなるまで区画割
    while True:
        print(f"\n{count} 回目")
        parcel_frame, remain_frame = get_side_parcel(
            search_frame, load_frame, target_area, move_line
        )

        count += 1
        binary_parcel_list.append(parcel_frame)

        if target_area > remain_frame.area:
            print(f"探索終了 残り面積{remain_frame.area}")
            break

        if count > 30:
            # 念のため
            break

        search_frame = remain_frame

    # draw_dxf.draw_line_by_frame_list_color(binary_parcel_list, 1)
    return binary_parcel_list


# debug_main()
