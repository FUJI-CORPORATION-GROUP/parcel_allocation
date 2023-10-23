# -*- coding: utf-8 -*-
import numpy as np
from numpy import linalg as LA
import Calc
import random
from scipy.spatial import distance
import copy
import evaluate_calc


def getclossvecs(vecs, point):
    """ベクトルと点の格子点を返す関数

    Args:
                    vecs (list): _枠のarray
                    point (int): _点

    Returns:
                    array: _交点の二点
    """
    arrayList_clossvecs = []
    targetareaflag = True

    # ベクトルのリストと点を受け取り、その点がどのベクトルと交差するかを返す
    for i in range(len(vecs)):
        start = vecs[i]
        end = vecs[i + 1] if i + 1 < len(vecs) else vecs[0]
        if (targetareaflag):
            arrayList_clossvecs.append(start)

        if (start[0] < point and point < end[0]) or (end[0] < point and point < start[0]):
            y = (end[1] - start[1]) / (end[0] - start[0]) * \
                (point - start[0]) + start[1]
            arrayList_clossvecs.append([point, y])
            targetareaflag = not targetareaflag

    # print(np.array(arrayList_clossvecs))
    return np.array(arrayList_clossvecs)


def binarysearch(vecs, targetarea):
    """二分探索を実行する関数

    Args:
                    vecs (list): _枠のarray
                    targetarea (int): _目標面積

    Returns:
                    temp_x: _目標面積を満たす二点
    """
    min_x, max_x = 0, 0

    # 二分探索範囲としての最大最小を決める所
    # 基準線からの垂線が接する最初と最後をそれに定義する
    for i in range(len(vecs)):
        if i == 0:
            min_x = vecs[i][0]
            max_x = vecs[i][0]
        else:
            if vecs[i][0] < min_x:
                min_x = vecs[i][0]
            if vecs[i][0] > max_x:
                max_x = vecs[i][0]
    print("min_x", min_x, "max_x", max_x)

    closet_x = 0
    min_diff = targetarea

    while min_x < max_x:
        # 中央値を求める
        temp_x = ((min_x + max_x) / 2)

        # 図形の取得 個々の処理を関数化したい（むずそう）
        temp_vec = getclossvecs(vecs, temp_x)

        # 面積を求める
        temp_area = Calc.calc(temp_vec)

        # 　中心の左右の値と比較
        temp_x_right = temp_x + 1
        temp_vec_right = getclossvecs(vecs, temp_x_right)
        temp_area_right = Calc.calc(temp_vec_right)
        min_diff_right = abs(targetarea - temp_area_right)

        temp_x_left = temp_x - 1
        temp_vec_left = getclossvecs(vecs, temp_x_left)
        temp_area_left = Calc.calc(temp_vec_left)
        min_diff_left = abs(targetarea - temp_area_left)

        if min_diff_right < min_diff_left:
            min_diff = min_diff_left
            closet_x = temp_x_right
        else:
            min_diff = min_diff_right
            closet_x = temp_x_left

        # 2分探索
        if temp_area > targetarea:
            max_x = temp_x - 1
        elif temp_area < targetarea:
            min_x = temp_x + 1
        else:
            return temp_x

    return temp_x


def paramas_calc(count, road_edge, maguti, least_maguti, goal_area):
    """今後の計算で使用する値を算出する関数

    Args:
                    count (int): _計算のカウント
                    road_edge (list): _街区が道路に接している辺のリスト
                    maguti (int): _間口の広さ
                    least_maguti (int): _間口の下限(上限)値
                    goal_area (int): _目標面積

    Returns:
                    road_distance: _長辺の長さ
                    use_maguti: _使用する間口
                    home_cnt: _建てる家の戸数
                    home_depth: _使用する奥行き
                    maguti_vector: _間口単位ベクトル
                    depth_vector: _奥行き単位ベクトル
    """
    # 指定街区の辺の長さ
    a = np.array(road_edge[count][0])
    b = np.array(road_edge[count][1])

    # 関数に使用する変数の計算
    road_distance = np.linalg.norm(b-a)  # 長辺の長さ
    use_maguti = random.randrange(maguti, least_maguti) if least_maguti >= maguti else random.randrange(
        least_maguti, maguti)  # 使用する間口
    home_cnt = int(road_distance / use_maguti)  # 辺に建てる戸数
    home_depth = goal_area / use_maguti  # 奥行き

    # 区画に使うベクトルの計算
    maguti_vector = [(road_edge[count][1][0] - road_edge[count][0][0]) / road_distance,
                     (road_edge[count][1][1] - road_edge[count][0][1]) / road_distance]  # 間口単位ベクトル
    depth_vector = [-maguti_vector[1] * home_depth,
                    maguti_vector[0] * home_depth]  # 奥行き単位ベクトル

    print(maguti_vector, depth_vector)
    return road_distance, use_maguti, home_cnt, home_depth, maguti_vector, depth_vector


def end_area_calc(goal_area, home_depth, maguti_vector, depth_vector, frame):
    """端の区画を計算する関数

    Args:
                    goal_area (int): _目標面積
                    home_depth (int): _奥行きの長さ
                    maguti_vector (list): _間口単位ベクトル
                    depth_vector (list): _奥行き単位ベクトル
                    frame (list): _街区リスト

    Returns:
                    area_list: _端区画の座標群
    """
    area_list = []

    # 間口の長さとベクトルからビンの底辺を算出する
    # 街区を二分探索用に切った図形を算出する
    # 二分探索を実行する

    return area_list


#### 道を作成しないケースの区画割の実行####
def unload_parcel_allocation(frame, road_edge, maguti, least_maguti, goal_area):
    """進入経路を確保しない際の区画割実行関数

    Returns:
                    result: _結果の座標リスト jwへの描画用に[[A, B], [B, C]]の形式で記述
                    point_list: _評価結果得点の集合リスト [向き, 広さ, 面積]の順に格納
                    total_score: _各結果の合計スコア
                    evaluation: _評価用に加工した二次元配列座標群
    """
    print("道を作成しない区画割+二分探索")
    result = 0
    point_list = []
    total_score = []
    evaluation = []
    maguti_vector = []
    depth_vector = []

    # 道路に隣接している辺の数だけ区画を作成
    for k in range(len(road_edge)):

        # 計算に使う値を算出   →もうちょい小分けにしてもいい気もする
        road_distance, use_maguti, home_cnt, home_depth, maguti_vector, depth_vector = paramas_calc(
            k, road_edge, maguti, least_maguti, goal_area)
        print("road_distance:" + str(road_distance))
        print("use_maguti:" + str(use_maguti))
        print("home_cnt:" + str(home_cnt))
        print("home_depth:" + str(home_depth))
        print("maguti_vector:" + str(maguti_vector))
        print("depth_vector:" + str(depth_vector))

        # 端区画を計算
        frame_array = np.array(frame)
        temp_x = binarysearch(frame_array, goal_area)
        print("##############")
        print("temp_x:" + str(temp_x))
        temp_y = (temp_x/maguti_vector[0]) * maguti_vector[1]
        print("temp_y:" + str(temp_y))
        # temp2_x, temp2_y = temp_x + \
        #     (frame[1][0]-frame[2][0]), temp_y+(frame[1][1]-frame[2][1])
        # result.append([[temp_x, temp_y], [temp2_x, temp2_y]])
        # print(str(result))
        print("###finish###")
        # unload_parcel_allocation(goal_area, home_depth, maguti_vector, depth_vector, frame)

    return result, point_list, total_score, evaluation
