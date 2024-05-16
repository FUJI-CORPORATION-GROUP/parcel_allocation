import Calc
import numpy as np
import math
import copy


# 有効宅地面積の計算
def yuko_calc(pt, frame):
    # 有効宅地面積
    yuko_menseki = 0
    # 合計面積
    all_area = 0

    # すべての区画の面積を合算
    for i in range(len(pt)):
        # 面積を計算
        cp_pt = copy.deepcopy(pt[i])
        area = Calc.main_calc(cp_pt)
        # 合算
        all_area += area

    # 全体面積の計算
    frame_menseki = Calc.main_calc(frame)

    # 有効宅地面積割合の算出
    yuko_menseki = all_area / frame_menseki * 100

    # 値の返還
    return yuko_menseki


# 旗竿地の判定
def hatazao_judge(p1, p2, qx, qy, pts, road_width):
    cp_pts = copy.deepcopy(pts)
    p1x, p1y = p1
    p2x, p2y = p2
    u = np.array([p2x - p1x, p2y - p1y])
    v = np.array([qx - p1x, qy - p1y])
    # 面積・竿の長さの計算
    distance = abs(np.cross(u, v) / np.linalg.norm(u))
    print("debaggu:" + str(cp_pts))
    summation = Calc.main_calc(cp_pts)
    # 法により竿部分は基本的に15m以下と定められている
    if distance <= 15000:
        # 法により竿部分は2m以上と定められている
        if road_width >= 2000:
            # 旗部分に十分な宅地面積を確保するための処理
            if 0.4 * summation >= distance * 2:
                return True
    return False


# 点と直線の距離
def Calc_distance(p1, p2, qx, qy):
    p1x, p1y = p1
    p2x, p2y = p2
    u = np.array([p2x - p1x, p2y - p1y])
    v = np.array([qx - p1x, qy - p1y])
    distance = abs(np.cross(u, v) / np.linalg.norm(u))
    # 点qが線分上にあればTrueを返す
    if ((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x)):
        if ((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y)):
            if distance <= 100:
                # print("                   ")
                # print("debug:" + str([p1, p2, qx, qy]))
                # print("True")
                # print("                   ")
                return True
    return False


# 面積スコアの算出
def area_rate_calc(pt, goal_area):
    # 面積スコアを70点満点で計算(素点40点)
    area_score = 40
    # 面積を計算
    cp_pt = copy.deepcopy(pt)
    print("面積計算に使うリスト" + str(cp_pt))
    area = Calc.main_calc(cp_pt)
    if area >= goal_area:
        # 宅地二つ分を最大値(30点)に設定し，一次関数で得点計算
        tilt = 30 / (goal_area * 2)
        # 得点計算
        area_score += tilt * area
    # 算出結果を返却
    return area_score


# marginを用意した面積スコアの算出
def area_rate_calc_margin(pt, goal_area):
    # 面積スコアを70点満点で計算(素点40点)
    area_score = 40
    # 面積を計算
    cp_pt = copy.deepcopy(pt)
    print("面積計算に使うリスト" + str(cp_pt))
    area = Calc.main_calc(cp_pt)
    if area >= (goal_area - 5000000):
        # 宅地二つ分を最大値(30点)に設定し，一次関数で得点計算
        tilt = 30 / (goal_area * 2)
        # 得点計算
        area_score += tilt * area
    # 算出結果を返却
    return area_score


# 接道率の算出
def accessibility_calc(data, pt, road_width):
    # 返還用のスコアを定義
    access_score = 0
    # 間口座標用配列
    maguchi_list = []
    # 道路に面している辺と各区画を見比べる
    # 辺上にある区画のカウント
    on_line = 0
    for k in range(len(pt)):
        for i in range(len(data)):
            # 線上判定関数
            if Calc_distance(data[i][0], data[i][1], pt[k][0], pt[k][1]):
                # 線上の点の個数をカウント
                on_line += 1
                # 最初の点が接道している場合は場合分け
                if k == 0:
                    print("最初の区画が接道")
                # 二番目の点が接道している場合
                elif k == 1:
                    # すでに接道点がある場合は二点追加
                    if on_line == 2:
                        maguchi_list.append(pt[0])
                        maguchi_list.append(pt[1])
                    elif on_line == 1:
                        maguchi_list.append(pt[1])
                # 最後の点が接道している場合
                elif k == (len(pt) - 1):
                    # 間口リストに中身がない場合は二点追加
                    if len(maguchi_list) == 0:
                        maguchi_list.append(pt[-1])
                        maguchi_list.append(pt[0])
                    # リストに中身がある場合は普通に追加
                    elif len(maguchi_list) == 1:
                        maguchi_list.append(pt[-1])
                # それ以外の場合は普通に追加
                else:
                    maguchi_list.append(pt[k])
            # 旗竿地の判定
            elif hatazao_judge(
                data[i][0], data[i][1], pt[k][0], pt[k][1], pt, road_width
            ):
                access_score = 0.7
        # 二つ以上線上の点があれば接道
        if len(maguchi_list) == 2:
            access_score = 1
            # print("現在の接道点 数：" + str(on_line))
            break
    if len(maguchi_list) == 1:
        print(pt)
    # 接道区画と総区画数を比べて率を計算
    return access_score, maguchi_list


# 宅地の向きの指標の得点計算
def build_direction(maguchi_list):
    # 宅地が道路に面している辺がどの方角を向いているかで点数分け
    # スコア定義
    direct_score = 0
    # 旗竿地作成のケースでは最低点で計算
    # 旗竿地判定
    if len(maguchi_list) == 2:
        # x座標とy座標に応じて場合分け
        dis_x = maguchi_list[1][0] - maguchi_list[0][0]
        dis_y = maguchi_list[1][1] - maguchi_list[0][1]
        # xの方が大きい場合は南向きか北向き
        if abs(dis_x) >= abs(dis_y):
            # xの値が正なら南向き，そうでないなら北向き
            if dis_x >= 0:
                direct_score = 20
            else:
                direct_score = 10
        # yの方が大きい場合は東向きか西向き
        else:
            # yの値が正なら東向き，そうでないなら西向き
            if dis_y >= 0:
                direct_score = 15
            else:
                direct_score = 5
    else:
        direct_score = 5
    # 結果スコアの返却
    return direct_score


# 間口の広さの指標による得点計算
def maguchi_breadth(maguchi_list):
    # 広さに応じて加点(最大10点)
    breadth_score = 5
    # 旗竿地は最低点で評価
    # 旗竿地の判定
    if len(maguchi_list) == 2:
        # 二点間の距離を算出
        a = np.array(maguchi_list[0])
        b = np.array(maguchi_list[1])
        # 計算用の長さ計算
        maguchi_distance = np.linalg.norm(b - a) / 1000
        maguchi_distance -= 7
        # 間口が9ｍ以上の区画は満点扱いに変更
        if maguchi_distance >= 2:
            maguchi_distance = 2
        # 間口9mで最大値5を取るように1/2乗のグラフに当てはめる
        breadth_score += math.sqrt((abs(maguchi_distance) * 25 / 2))
    # 間口の広さ評価結果の返却
    return breadth_score


def eval(road_frame, section, road_width, goal_area):
    # 結果記入用配列・総合得点
    result = []
    total_score = 0
    total_score_margin = 0

    # 区画の戸数分ループ
    for i in range(len(section)):
        # 個別結果記入用配列
        ind_result = []

        # 接道スコア・間口計算用配列
        maguchi_list = []
        accses_score = 0

        # 接道率を0，1，0.7の三段階で評価
        accses_score, maguchi_list = accessibility_calc(
            road_frame, section[i], road_width
        )
        ind_result.append(accses_score)

        # 宅地の向きを20点満点で評価
        ind_result.append(build_direction(maguchi_list))

        # 間口の広さを10点満点で評価
        ind_result.append(maguchi_breadth(maguchi_list))

        # 各宅地の敷地面積を70点満点で評価
        ind_result.append(area_rate_calc(section[i], goal_area))

        # 5平米の余裕を持たせた面積の評価
        ind_result.append(area_rate_calc_margin(section[i], goal_area))

        # 点数計算([間口+向き+面積] * 接道スコア)
        total_score += (ind_result[1] + ind_result[2] + ind_result[3]) * ind_result[0]

        # 点数計算([間口+向き+面積] * 接道スコア)
        total_score_margin += (
            ind_result[1] + ind_result[2] + ind_result[4]
        ) * ind_result[0]

        # 個別結果を全体結果配列に格納
        result.append(ind_result)

    # 評価結果・合計得点を返却
    return result, total_score, total_score_margin


# 道を作成しない場合の面積スコア
def unload_area_rate(pt, goal_area):
    # 面積スコアを100点満点で計算(素点50点)
    area_score = 50
    # 面積を計算
    cp_pt = copy.deepcopy(pt)
    print("\t\t面積計算に使うリスト" + str(cp_pt))
    area = Calc.main_calc(cp_pt)
    if area >= goal_area:
        # 宅地二つ分を最大値(50点)に設定し，一次関数で得点計算
        tilt = 50 / (goal_area * 2)
        # 得点計算
        area_score += tilt * area
    # 算出結果を返却
    return area_score


# 道を作成しない場合の評価関数
def unload_eval(section, goal_area):
    # 結果記入用配列・総合得点
    result = []
    # total_score = 0
    # 区画の戸数分ループ
    for i in range(len(section)):
        # 個別結果記入用配列
        # ind_result = []

        # 各宅地の敷地面積を70点満点で評価
        result.append(unload_area_rate(section[i], goal_area))

    # 合計得点を返却
    return result
