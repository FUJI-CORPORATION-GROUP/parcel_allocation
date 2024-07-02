import datetime
import math
import random
from components.point import Point
from components.frame import Frame
from components.plan import Plan
import binary_search
import draw_dxf
import json
import shapely
from shapely.geometry import Polygon, MultiPolygon


def get_plan(
    target_max_area,
    target_min_area,
    binary_parcel_list,
    search_frame,
    count,
    road_frame,
    move_line,
):
    # frameListを作成して，Planを返す
    # 探索領域が目標面積取れなくなるまで区画割
    while True:
        if search_frame.area > target_max_area:
            target_area = random.randint(target_min_area, target_max_area)
            print(f"\n{count} 回目 探索開始 ランダム目標面積：{target_area}")
        else:
            target_area = target_max_area
            print(f"\n{count} 回目 探索開始 最小目標面積：{target_area}")

        parcel_frame, remain_frame = binary_search.get_side_parcel(
            search_frame, road_frame, target_area, move_line, count
        )

        count += 1
        binary_parcel_list.append(parcel_frame)

        if target_min_area > remain_frame.area:
            print(f"探索終了 残り面積{  math.floor(remain_frame.area/1000000)}㎡")
            break

        if count > 30:
            # 念のため
            break

        search_frame = remain_frame

    plan = Plan(binary_parcel_list)

    last_remain_frame = remain_frame if remain_frame is not None else None

    return plan, last_remain_frame


def get_remain_search_frame(last_remain_frame: Frame, remain_site_frame: Frame):
    """remain_search_frameを取得する

    Args:
        last_remain_frame (Frame): 前回の探索領域の残り
        remain_site_frame (Frame): 残りの敷地
    """

    # Polygon正規化の許容範囲
    tolerance = 100

    if remain_site_frame is None:
        remain_search_frame = None

    elif last_remain_frame is None:
        remain_search_frame = remain_site_frame

    else:
        # last_remain_frameをPolygon型に変換
        last_remain_polygon = Polygon(Point.to_np_array_list(last_remain_frame.points))

        # remain_site_frameをPolygon型に変換
        remain_site_polygon = Polygon(Point.to_np_array_list(remain_site_frame.points))

        # shapelyのunary_unionを使ってremain_search_frameを取得
        buffer_distance = 10
        last_remain_polygon = last_remain_polygon.buffer(buffer_distance)
        remain_site_polygon = remain_site_polygon.buffer(buffer_distance)
        # remain_search_polygon = shapely.unary_union([last_remain_polygon, remain_site_polygon])
        remain_search_polygon = remain_site_polygon.union(last_remain_polygon)
        remain_search_polygon = remain_search_polygon.normalize().simplify(tolerance)

        # unionの返り血判定
        print(type(remain_search_polygon))
        if isinstance(remain_search_polygon, Polygon):
            print("Polygon")
        elif isinstance(remain_search_polygon, MultiPolygon):
            print("MultiPolygon")
            print("Multi is valid:" + str(remain_search_polygon.is_valid))
        else:
            print("Un expected type:" + str(type(remain_search_polygon)))

        try:
            remain_search_frame = Frame(
                [
                    Point(
                        remain_search_polygon.exterior.coords[i][0],
                        remain_search_polygon.exterior.coords[i][1],
                    )
                    for i in range(len(remain_search_polygon.exterior.coords))
                ]
            )

            # 適切に残り領域が取得できるかどうかの描写

            return remain_search_frame
        except Exception as e:
            # マルチポリゴン発生時
            print("error:" + str(e))
            polygons = list(remain_search_polygon.geoms)
            multi_frame = []
            for polygon in polygons:
                multi_frame.append(
                    Frame(
                        [
                            Point(polygon.exterior.coords[i][0], polygon.exterior.coords[i][1])
                            for i in range(len(polygon.exterior.coords))
                        ]
                    )
                )

            # multi_frameの描写
            for frame in multi_frame:
                draw_dxf.debug_png_by_frame_list([frame])
            print("polygons:" + str(polygons))


def main():
    # メインプログラム#
    # 読み込み用のファイルを展開
    print("================================")
    print("メインプログラム split.py")
    print("================================")

    # # 変数宣言
    site_frame = []
    road_edge = []

    # Json形式で取得する
    # TODO: pathの指定を変更 変数に入れる，相対パス？
    road_data_open = open("./data/road_input_data.json", "r")
    frame_data_open = open("./data/frame_input_data.json", "r")
    road_data = json.load(road_data_open)
    frame_data = json.load(frame_data_open)

    road_edge_point_list = road_data["road_edge_point_list"]
    target_min_area = road_data["target_min_area"]
    target_max_area = road_data["target_max_area"]
    min_maguchi = road_data["min_maguchi"]
    max_maguchi = road_data["max_maguchi"]
    site_frame = frame_data["frame"]

    # ふたつずつ座標をまとめる：road_edge
    # TODO: この処理はun_road_make.pyで行ってJsonに入れてもいいかも？
    for i in range(int(len(road_edge_point_list) / 2)):
        road_edge.append([road_edge_point_list[i * 2], road_edge_point_list[i * 2 + 1]])

    # classの変更
    for i in range(len(site_frame)):
        site_frame[i] = Point(site_frame[i][0], site_frame[i][1])
    road_frame_list = []
    print("site_frame:" + str(site_frame))
    site_frame = Frame(site_frame)
    print("site_frame:" + str(site_frame))
    for i in range(len(road_edge)):
        road_start_point_list = Point(road_edge[i][0][0], road_edge[i][0][1])
        road_end_point_list = Point(road_edge[i][1][0], road_edge[i][1][1])
        road_frame = Frame([road_start_point_list, road_end_point_list])
        road_frame_list.append(road_frame)

    # 区画・道路を原点に移動
    site_frame, road_frame_list = Frame.move_frame_and_road(site_frame, road_frame_list)

    if len(road_frame_list) == 0:
        print("道路がありません")
        exit()

    draw_dxf.clear_dxf()
    tmp_site_frame = site_frame
    for i in range(len(road_frame_list)):
        target_road_frame = road_frame_list[i]

        # 奥行の距離
        maguchi_distance = random.randint(min_maguchi, max_maguchi)
        search_depth_distance = get_depth_distance(maguchi_distance, (target_min_area + target_max_area) / 2)

        road_start_point = target_road_frame.points[0]
        road_end_point = target_road_frame.points[1]
        search_frame, remain_site_frame = tmp_site_frame.Get_search_frame(
            tmp_site_frame, search_depth_distance, road_start_point, road_end_point
        )

        # デバッグ用に描写
        # draw_dxf.draw_line_by_frame_list([search_frame])
        # draw_dxf.draw_line_by_frame_list([remain_site_frame])

        # 道路方向ベクトル取得
        road_vec = road_end_point.sub(road_start_point)

        # 道路方向ベクトルを回転させてMoveLineを取得
        move_line = Point(-1 * road_vec.y, road_vec.x)

        # 参照しているDXFファイルをリセット
        binary_parcel_list = []
        count = 0

        # TODO:30回実行
        plan_list = []
        for executions in range(1):
            # frameListを作成して，Planを返す
            plan, last_remain_frame = get_plan(
                target_max_area,
                target_min_area,
                binary_parcel_list,
                search_frame,
                count,
                target_road_frame,
                move_line,
            )
            plan_list.append(plan)

        # デバッグ用に描画
        draw_dxf.debug_png_by_plan_list(plan_list)

        if i != len(road_frame_list) - 1:
            remain_search_frame = get_remain_search_frame(last_remain_frame, remain_site_frame)
            # draw_dxf.draw_line_by_frame_list([remain_search_frame], 1)
            tmp_site_frame = remain_search_frame

        # 描写開始(描画毎に位置変え)

        # for i in range(len(plan_list)):
        #   point_shift = Point((i % 5) * 100000, (i // 5) * 80000)
        #   plan_list[i] = plan_list[i].move_plan(point_shift)
        #   # draw_dxf.draw_dxf_by_plan(plan_list[i].move_plan(point_shift), 1)
        #   # draw_dxf.draw_dxf_by_plan(plan_list[i], 1)
        # print("plan_list" + str(plan_list))

        # draw_dxf.draw_dxf_by_plan_list(plan_list, 2)


def get_depth_distance(maguchi_distance, target_area):
    # 奥行の距離の取得
    depth_distance = target_area / maguchi_distance
    return depth_distance


main()
draw_dxf.convert_dxf_to_png()
