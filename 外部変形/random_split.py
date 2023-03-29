# -*- coding: utf-8 -*-
from audioop import reverse
import importlib
import math
from operator import rshift
import sys
import re
import os
import math
from turtle import right, width
from cv2 import RETR_CCOMP
import ezdxf
import random
import copy
import numpy as np
from numpy import linalg as LA
from scipy.spatial import distance
import Calc
import evaluate_calc
# from 外部変形.evaluate_calc import area_rate_calc

#点が図形内部あるかどうかの判定
def inside_polygon(p0, qs):
  # print("p0:" + str(p0))
  # print("qs:" + str(qs))
  cnt = 0
  L = len(qs)
  x, y = p0
  #判定
  for i in range(L):
      x0, y0 = qs[i-1]; x1, y1 = qs[i]
      x0 -= x; y0 -= y
      x1 -= x; y1 -= y

      cv = x0*x1 + y0*y1
      sv = x0*y1 - x1*y0
      if sv == 0 and cv <= 0:
          # a point is on a segment
          return True

      if not y0 < y1:
          x0, x1 = x1, x0
          y0, y1 = y1, y0

      if y0 <= 0 < y1 and x0*(y1 - y0) > y0*(x1 - x0):
          cnt += 1
  return (cnt % 2 == 1)

#点が線分上にあるどうかを判定
def line_judge(p1, p2, qx, qy):
  print("p1:" + str(p1))
  print("p2:" + str(p2))
  print("qx:" + str(qx))
  print("qy:" + str(qy))
  #渡された点をそれぞれ代入
  p1x, p1y = p1
  p2x, p2y = p2
  print((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x))
  print((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y))
  print("線上判定：" + str((qy * (p1x - p2x)) + (p1y * (p2x - qx)) + (p2y * (qx - p1x))))
#点qが線分上にあればTrueを返す
  if ((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x)):
    if ((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y)):
      #if ((qy * (p1x - p2x)) + (p1y * (p2x - qx)) + (p2y * (qx - p1x)) == 0):
      # 点Pが線分AB上にある
      return True
  #線上になかったのでFalseを返す
  return False

#式の傾き・切片の計算
def line_formula(xy1, xy2):
  #計算しやすいように代入
  x1,y1 = xy1
  x2,y2 = xy2
  #座標からの算出
  a = (y1 - y2) / (x1 - x2)
  b = y1 - a * x1
  return (a, b)

#直線同士の交点の計算
def line_cross_point(P0, P1, Q0, Q1):
  x0, y0 = P0; x1, y1 = P1
  x2, y2 = Q0; x3, y3 = Q1
  a0 = x1 - x0; b0 = y1 - y0
  a2 = x3 - x2; b2 = y3 - y2

  d = a0*b2 - a2*b0
  if d == 0:
      # 並行の場合
      return None

  # 交点計算
  sn = b2 * (x2-x0) - a2 * (y2-y0)
  x = x0 + a0*sn/d
  y = y0 + b0*sn/d

  #交点が線上に存在する場合のみ描画
  if (x0 <= x <= x1 and y0 <= y <= y1) or (x0 >= x >= x1 and y0 >= y >= y1) or (x0 <= x <= x1 and y0 >= y >= y1) or (x0 >= x >= x1 and y0 <= y <= y1):
    return x, y
  else:
    return None

def parcel_allocation(make_road_edge, parcel_frame, road_width, road_edge, maguti, goal_area):
  inter_coor = []
  cp_inter_coor = []
  result = []
  instant_coor = []
  road_inter_coor = []
  instant_coor_a = []
  instant_coor_b = []
  instant_result = []
  start_road = []
  road_mid_line = []
  late_parcel = []
  evaluation = []
  eva_coor = []
  inside_flag = False
  inside_flag_1 = False
  inside_flag_2 = False
  road_frame_flag = False
  inside_parcel_flag = False
  exist_flag = False

  #道の角度を決定する(道作成辺に対して垂直，他の接道辺に平行) 今は90度だけでとりあえず
  angle_list = []
  angle_list.append(90)
  #街区の端から区画を決めていく ＜後で＞
  #接道している区画を決定する
  for k in range(2):
    print("----------" + str(k + 1) + "週目----------")
    #指定街区の辺の長さ
    a=np.array(road_edge[k][0])
    b=np.array(road_edge[k][1])
    #長さ計算
    road_distance = np.linalg.norm(b-a)
    #その辺における間口・家の戸数・奥行の計算
    home_cnt = int(road_distance / maguti)
    real_maguti = road_distance / home_cnt
    home_depth = goal_area / real_maguti
    #間口毎のベクトルの算出
    deviation = [(road_edge[k][1][0] - road_edge[k][0][0]) / home_cnt, (road_edge[k][1][1] - road_edge[k][0][1]) / home_cnt]
    tilt, intercept = line_formula(road_edge[k][0], road_edge[k][1])
    #垂直な線の式を算出（傾き・切片の算出）
    untilt = -1 / tilt
    unintercept = untilt * road_edge[k][0][0] - road_edge[k][0][1]
    #距離home_depth，road_edgeに垂直な点を算出（奥行の計算）
    double_multiple = (home_depth * home_depth) / (deviation[0] * deviation[0] + deviation[1] * deviation[1])
    multiple = math.sqrt(double_multiple)
    #奥行座標の格納
    right_coor_x, right_coor_y = road_edge[k][0][0] - deviation[1] * multiple, road_edge[k][0][1] + deviation[0] * multiple
    #奥行座標と間口間ベクトルで構成された直線と枠線の交点（二点）を算出
    for i in range(1, len(parcel_frame)):
      intersection = line_cross_point(parcel_frame[i - 1], parcel_frame[i], [right_coor_x, right_coor_y], [right_coor_x + deviation[0], right_coor_y + deviation[1]])
      print("intersection:" + str(intersection))
      #交点を追加
      if intersection is not None:
        inter_coor.append(intersection)
    if k % 2 == 0:
      #inter_coorを逆順にソート
      inter_coor.reverse()
    #各種数値の出力（デバッグ）
    print("road_distance:" + str(road_distance))
    print("home_cnt:" + str(home_cnt) + " real_maguti:" + str(real_maguti) + " home_depth:" + str(home_depth))
    # print("untilt:" + str(road_edge[k][1][0]) + " deviation:" + str(deviation))
    # print("double_multiple:" + str(double_multiple))
    # print("multiple:" + str(multiple))
    # print("inter_coor:" + str(inter_coor))
    # print("parcel_frame:" + str(parcel_frame))
    # print("right_coor:" + str([right_coor_x, right_coor_y]))
    # print("right_coor + deviation:" + str([right_coor_x + deviation[0], right_coor_y + deviation[1]]))
    #結果リストに格納
    result.append([[inter_coor[0][0], inter_coor[0][1]], [inter_coor[1][0], inter_coor[1][1]]])
    #各家の座標を格納(間口間ベクトル参照)
    for i in range(1, home_cnt):
      cp_inter_coor = copy.deepcopy(inter_coor)
      if line_judge(cp_inter_coor[0], cp_inter_coor[1], cp_inter_coor[0][0] + (i * deviation[0]), cp_inter_coor[0][1] + (i * deviation[1])):
        exist_flag = True
        instant_coor_a.append(road_edge[k][0][0] + (i * deviation[0]))
        instant_coor_a.append(road_edge[k][0][1] + (i * deviation[1]))
        instant_coor_b.append(instant_coor_a[0] - deviation[1] * multiple)
        instant_coor_b.append(instant_coor_a[1] + deviation[0] * multiple)
        instant_coor.append(instant_coor_a)
        instant_coor.append(instant_coor_b)
        instant_result.extend(instant_coor)
        instant_coor_a = []
        instant_coor_b = []
        instant_coor = []
        #まとめた座標を結果に追加
        result.append(instant_result)
        eva_coor.append(instant_result[0])
        eva_coor.append(instant_result[1])
        instant_result = []
        print("eva_coor:" + str(eva_coor))
        print("eva_coor[0]:" + str(eva_coor[0]))
        print("eva_coor[0][0]:" + str(eva_coor[0][0]))
        print("eva_coor[i]:" + str(eva_coor[i]))
      elif line_judge(cp_inter_coor[0], cp_inter_coor[1], cp_inter_coor[1][0] + (i * deviation[0]), cp_inter_coor[1][1] + (i * deviation[1])):
        exist_flag = True
        instant_coor_a.append(road_edge[k][0][0] + (i * deviation[0]))
        instant_coor_a.append(road_edge[k][0][1] + (i * deviation[1]))
        instant_coor_b.append(instant_coor_a[0] - deviation[1] * multiple)
        instant_coor_b.append(instant_coor_a[1] + deviation[0] * multiple)
        instant_coor.append(instant_coor_a)
        instant_coor.append(instant_coor_b)
        instant_result.extend(instant_coor)
        instant_coor_a = []
        instant_coor_b = []
        instant_coor = []
        #まとめた座標を結果に追加
        result.append(instant_result)
        eva_coor.append(instant_result[0])
        eva_coor.append(instant_result[1])
        instant_result = []
        print("eva_coor:" + str(eva_coor))
        print("eva_coor[0]:" + str(eva_coor[0]))
        print("eva_coor[0][0]:" + str(eva_coor[0][0]))
        print("eva_coor[i]:" + str(eva_coor[i]))
      if exist_flag:
        if k % 2 == 0:
          if i == 1:
            evaluation.append([eva_coor[0], eva_coor[1], [inter_coor[0][0], inter_coor[0][1]], parcel_frame[0]])
          elif i == home_cnt - 1:
            evaluation.append([eva_coor[i * 2 - 2], eva_coor[i * 2 - 1], eva_coor[i * 2 - 3], eva_coor[i * 2 - 4]])
            evaluation.append([parcel_frame[1], [inter_coor[1][0], inter_coor[1][1]], eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2]])
            break
          else:
            evaluation.append([eva_coor[i * 2 - 2], eva_coor[i * 2 - 1], eva_coor[i * 2 - 3], eva_coor[i * 2 - 4]])
        else:
          if i == 1:
            evaluation.append([[inter_coor[0][0], inter_coor[0][1]], parcel_frame[2], eva_coor[0], eva_coor[1]])
          elif i == home_cnt - 1:
            evaluation.append([eva_coor[i * 2 - 3], eva_coor[i * 2 - 4], eva_coor[i * 2 - 2], eva_coor[i * 2 - 1]])
            evaluation.append([parcel_frame[3], [inter_coor[1][0], inter_coor[1][1]], eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2]])
            break
          else:
            evaluation.append([eva_coor[i * 2 - 3], eva_coor[i * 2 - 4], eva_coor[i * 2 - 2], eva_coor[i * 2 - 1]])
      else:
        if k % 2 == 0:
          evaluation.append([parcel_frame[1], [inter_coor[1][0], inter_coor[1][1]], eva_coor[(i - 1) * 2 - 2], eva_coor[(i - 1) * 2 - 1]])
          break
        else:
          evaluation.append([eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2 - 2], [inter_coor[1][0], inter_coor[1][1]], parcel_frame[3]])
          break
      exist_flag = False
    eva_coor = []
    #街区を小さくしていく処理
    # print("-----------------")
    # print(parcel_frame)
    # print(road_edge)
    # print(inter_coor)
    # # inter_coor.reverse()
    # print(inter_coor)
    # print("------------------")
    for i in range(len(parcel_frame)):
      for j in range(len(road_edge[k])):
        if parcel_frame[i] == road_edge[k][j]:
          parcel_frame[i] = [inter_coor[j][0], inter_coor[j][1]]
    eva_coor = []
    inter_coor = []
    print("evaluation:" + str(evaluation))
    print("parcel_frame:" + str(parcel_frame))
    print("----------" + str(k + 1) + "週目終わり----------")
  cp_parcel = copy.copy(parcel_frame)
  #狭まった区画における道を作成する辺を算出
  for i in range(0, (len(parcel_frame) - 1), 1):
    #道作成辺を狭めた街区の座標に置き換え
    if line_judge(make_road_edge[0], make_road_edge[1], parcel_frame[i][0], parcel_frame[i][1]):
      if line_judge(make_road_edge[0], make_road_edge[1], parcel_frame[i + 1][0], parcel_frame[i + 1][1]):
        make_road_edge[0] = [parcel_frame[i][0], parcel_frame[i][1]]
        make_road_edge[1] = [parcel_frame[i + 1][0], parcel_frame[i + 1][1]]
        #該当街区のため，置き換え実行
        break
  #道の場所を決定する（道作成辺の半分地点）
  x = make_road_edge[1][0] - make_road_edge[0][0]
  y = make_road_edge[1][1] - make_road_edge[0][1]
  #道作成辺の中点を基準に道の入り口を算出
  start_road = [(make_road_edge[0][0] + make_road_edge[1][0]) / 2, (make_road_edge[0][1] + make_road_edge[1][1]) / 2]
  half_road_width = road_width / 2
  road_tilt, road_intercept = line_formula(make_road_edge[0], make_road_edge[1])
  constant_k = half_road_width / math.sqrt(x * x + y * y)
  #道の長さを決定する(算出した角度の数に応じて*50個ぐらい)
  #道を作成するリスト（0．1狭めた街区の道作成辺．2．道作成辺の中点．3.4道の入り口）
  make_road_edge.append([start_road[0] - y, start_road[1] + x])
  make_road_edge.append([start_road[0] + (x * constant_k), start_road[1] + (y * constant_k)])
  make_road_edge.append([start_road[0] - (x * constant_k), start_road[1] - (y * constant_k)])
  print("make_road_edge:" + str(make_road_edge))
  #道の最大の長さ，最小の長さの決定
  for i in range(1, len(parcel_frame)):
    print("start_road:" + str(start_road))
    print("parcel:" + str([parcel_frame[i - 1], parcel_frame[i]]))
    intersection = line_cross_point(parcel_frame[i - 1], parcel_frame[i], start_road, make_road_edge[2])
    print("intersection:" + str(intersection))
    #交点を追加
    if intersection is not None:
      road_inter_coor.append(intersection)
  #道の最大の長さを格納（ランダム生成の最大値）
  a=np.array(road_inter_coor[0])
  b=np.array(road_inter_coor[1])
  road_inter_distance = np.linalg.norm(b-a)
  #道がはみ出ない範囲で無作為に生成
  while not inside_flag:
    #最大の長さの半分以上でランダムに生成
    road_length=random.uniform(road_inter_distance / 2, road_inter_distance)
    randam_constant_k = road_length / math.sqrt(x * x + y * y)
    print("randam_constant_k:" + str(randam_constant_k))
    #道の端となる二点を生成
    inside_coor_1 = [make_road_edge[3][0] - y * randam_constant_k, make_road_edge[3][1] + x * randam_constant_k]
    if inside_polygon(inside_coor_1, list(parcel_frame[:-1])):
      #内部にある
      inside_flag_1 = True
    #二点目の生成
    inside_coor_2 = [make_road_edge[4][0] - y * randam_constant_k, make_road_edge[4][1] + x * randam_constant_k]
    if inside_polygon(inside_coor_2, list(parcel_frame[:-1])):
      #内部にある
      inside_flag_2 = True
    #両方とも内部にあれば完了
    if inside_flag_1 and inside_flag_2:
      inside_flag = True
  #行き止まりの先に中線を描画
  road_mid_line.append(line_cross_point(inside_coor_1, inside_coor_2, road_inter_coor[0], road_inter_coor[1]))
  road_mid_line.append(road_inter_coor[1])
  #道の入り口，行き止まりの四点を追加
  instant_result = [inside_coor_1, inside_coor_2]
  result.append(instant_result)
  result.append([make_road_edge[4], inside_coor_2])
  result.append([make_road_edge[3], inside_coor_1])
  #道の個数が出力結果の戸数になるため，50パターン*道の種類(とりあえず)
  result.append(road_mid_line)
  #残りの区画を決定する
#####上区画の分割#####
  ###汎用的な記述ではない###
  goal_area_flag = False
  area_calc = []
  #道に沿って間口ベクトルの算出
  deviation = [(parcel_frame[1][0] - make_road_edge[4][0]), (parcel_frame[1][1] - make_road_edge[4][1])]
  parcel_deviation = [(parcel_frame[0][0] - parcel_frame[1][0]), (parcel_frame[0][1] - parcel_frame[1][1])]
  deviation_k = maguti / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
  instant_coor_b = [make_road_edge[4][0] + deviation[1] * deviation_k, make_road_edge[4][1] - deviation[0] * deviation_k]
  instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] - parcel_deviation[1] * 3, instant_coor_b[1] + parcel_deviation[0] * 3])
  #指定座標がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[1]
    instant_coor_b = [instant_coor_a[0] - deviation[0], instant_coor_a[1] - deviation[1]]
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append(make_road_edge[4])
  else:
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append(parcel_frame[1])
    area_calc.append(make_road_edge[4])
  #完成した宅地の面積
  home_area = Calc.calc(area_calc)
  print("home_area:" + str(home_area))
  #目標面積に達していればフラグを建てる
  if home_area >= goal_area:
    goal_area_flag = True
  #面積が足りていない場合は線をずらす
  if not goal_area_flag:
    a=np.array(instant_coor_b)
    b=np.array(instant_coor_a)
    expand_area_distance = np.linalg.norm(b-a)
    expand_distance = (goal_area - home_area) / expand_area_distance
    expand_k = expand_distance / math.sqrt(parcel_deviation[0] * parcel_deviation[0] + parcel_deviation[1] * parcel_deviation[1])
    #角度を変えずに平行移動
    instant_coor_b = [instant_coor_b[0] + parcel_deviation[0] * expand_k, instant_coor_b[1] + parcel_deviation[1] * expand_k]
    instant_coor_a = [instant_coor_a[0] + parcel_deviation[0] * expand_k, instant_coor_a[1] + parcel_deviation[1] * expand_k]
    area_calc[0] = instant_coor_b
    area_calc[1] = instant_coor_a
  else:
    goal_area_flag = False
  evaluation.append(area_calc)
  area_calc = []
  #座標の追加
  result.append([instant_coor_a, instant_coor_b])
  #後に割る区画として定義
  late_parcel.append(instant_coor_a)
  late_parcel.append(instant_coor_b)
  road_frame_flag = False
  inside_parcel_flag = False
  #道の反対側の処理
  instant_coor_b = [road_inter_coor[1][0] - deviation[1] * deviation_k, road_inter_coor[1][1] + deviation[0] * deviation_k]
  #直角の座標を入手
  x = make_road_edge[1][0] - make_road_edge[0][0]
  y = make_road_edge[1][1] - make_road_edge[0][1]
  instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] - x * 2, instant_coor_b[1] - y * 2])
  print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
  #指定の座標（上）がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[0]
    non_in_road = [road_mid_line[0][0] - inside_coor_1[0], road_mid_line[0][1] - inside_coor_1[1]]
    instant_coor_b = [instant_coor_a[0] - deviation[0] - non_in_road[0], instant_coor_a[1] - deviation[1] - non_in_road[1]]
    print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
  else:
    inside_parcel_flag = True
  instant_coor_a = [instant_coor_a[0], instant_coor_a[1]]
  #指定座標（下）が作成した進入経路上にあるかどうか
  if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
    road_frame_flag = True
    instant_coor_b = [instant_coor_b[0] - (x * constant_k), instant_coor_b[1] - (y * constant_k)]
  #4パターンの結果についてそれぞれ面積を求める
  if road_frame_flag and inside_parcel_flag:
    area_calc.append(instant_coor_b)
    area_calc.append(inside_coor_2)
    area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
    area_calc.append(parcel_frame[0])
    area_calc.append(instant_coor_a)
  elif road_frame_flag and not inside_parcel_flag:
    area_calc.append(instant_coor_a)
    area_calc.append(instant_coor_b)
    area_calc.append(inside_coor_2)
    area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
  elif not road_frame_flag and inside_parcel_flag:
    area_calc.append(instant_coor_a)
    area_calc.append(instant_coor_b)
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
    area_calc.append(parcel_frame[0])
  elif not road_frame_flag and not inside_parcel_flag:
    area_calc.append(instant_coor_a)
    area_calc.append(instant_coor_b)
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
  #完成した宅地の面積
  print("area_calc:" + str(area_calc))
  home_area = Calc.calc(area_calc)
  #目標面積に達していればフラグを建てる
  print("home_area:" + str(home_area))
  print("goal_area:" + str(goal_area))
  if (home_area >= goal_area):
    goal_area_flag = True
  #指定面積に満たなかった場合
  if not goal_area_flag:
    a=np.array(instant_coor_a)
    b=np.array(instant_coor_b)
    expand_area_distance = np.linalg.norm(b-a)
    expand_distance = (goal_area - home_area) / expand_area_distance
    expand_k = expand_distance / (deviation[0] * deviation[0] + deviation[1] * deviation[1])
    instant_coor_b = [instant_coor_b[0] + deviation[0] * expand_k, instant_coor_b[1] + deviation[1] * expand_k]
    instant_coor_a = [instant_coor_a[0] + deviation[0] * expand_k, instant_coor_a[1] + deviation[1] * expand_k]
    #平行移動によって指定座標（下）が進入経路に干渉してしまっている場合の処理
    if not road_frame_flag:
      if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
        #指定座標（下）を進入経路上に移動
        area_calc = []
        instant_coor_b = [instant_coor_b[0] - deviation[0] * deviation_k, instant_coor_b[1] - deviation[1] * deviation_k]
        #該当パターン2つについて面積を再度計算
        if road_frame_flag and inside_parcel_flag:
          area_calc.append(instant_coor_b)
          area_calc.append(inside_coor_2)
          area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
          area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
          area_calc.append(parcel_frame[0])
          area_calc.append(instant_coor_a)
        elif not road_frame_flag and inside_parcel_flag:
          area_calc.append(instant_coor_a)
          area_calc.append(instant_coor_b)
          area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
          area_calc.append(parcel_frame[0])
        #再計算された面積
        home_area = Calc.calc(area_calc)
        #目標面積に達していればフラグを建てる
        if home_area >= goal_area:
          goal_area_flag = True
        #面積が満たなければもう一度平行移動させて該当面積に到達させる
        else:
          a=np.array(instant_coor_a)
          b=np.array(instant_coor_b)
          expand_area_distance = np.linalg.norm(b-a)
          expand_distance = (goal_area - home_area) / expand_area_distance
          expand_p = expand_distance / (deviation[0] * deviation[0] + deviation[1] * deviation[1])
          instant_coor_b = [instant_coor_b[0] + deviation[0] * expand_p, instant_coor_b[1] + deviation[1] * expand_p]
          instant_coor_a = [instant_coor_a[0] + deviation[0] * expand_p, instant_coor_a[1] + deviation[1] * expand_p]
          if road_frame_flag and inside_parcel_flag:
            area_calc.append(instant_coor_b)
            area_calc.append(inside_coor_2)
            area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
            area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
            area_calc.append(parcel_frame[0])
            area_calc.append(instant_coor_a)
          elif not road_frame_flag and inside_parcel_flag:
            area_calc.append(instant_coor_a)
            area_calc.append(instant_coor_b)
            area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
            area_calc.append(parcel_frame[0])
  else:
    #フラグは元に戻しておく
    goal_area_flag = False
  evaluation.append(area_calc)
  area_calc = []
  #4パターンの結果についてそれぞれ格納しておく
  if road_frame_flag and inside_parcel_flag:
    late_parcel.append(instant_coor_b)
    late_parcel.append(instant_coor_a)
  elif road_frame_flag and not inside_parcel_flag:
    late_parcel.append(instant_coor_b)
    late_parcel.append(instant_coor_a)
  elif not road_frame_flag and inside_parcel_flag:
    late_parcel.append(inside_coor_2)
    late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
    late_parcel.append(instant_coor_b)
    late_parcel.append(instant_coor_a)
  elif not road_frame_flag and not inside_parcel_flag:
    late_parcel.append(inside_coor_2)
    late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
    late_parcel.append(instant_coor_b)
    late_parcel.append(instant_coor_a)
  road_frame_flag = False
  inside_parcel_flag = False
  area_calc = []
  #計算結果座標の追加
  result.append([instant_coor_a, instant_coor_b])
  #残りの区画を割る
  if len(late_parcel) == 4:
    #指定街区の辺の長さ
    a=np.array(late_parcel[1])
    b=np.array(late_parcel[2])
    road_distance = np.linalg.norm(b-a)
    #辺における間口・家の戸数・奥行の計算
    home_cnt = int(road_distance / maguti)
    late_deviation = [(late_parcel[2][0] - late_parcel[1][0]) / home_cnt, (late_parcel[2][1] - late_parcel[1][1]) / home_cnt]
    for i in range(1, home_cnt):
      instant_coor_a = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
      instant_coor_b = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
      result.append([instant_coor_a, instant_coor_b])
      if i == 1:
        evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
      elif i == home_cnt - 1:
        evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
        evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2], late_parcel[3]])
      else:
        evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
  elif len(late_parcel) == 6:
    #指定街区の辺の長さ
    a=np.array(late_parcel[0])
    b=np.array(late_parcel[5])
    road_distance = np.linalg.norm(b-a)
    #辺における間口・家の戸数・奥行の計算
    home_cnt = int(road_distance / maguti)
    late_deviation = [(late_parcel[5][0] - late_parcel[0][0]) / home_cnt, (late_parcel[5][1] - late_parcel[0][1]) / home_cnt]
    for i in range(1, home_cnt):
      instant_coor_a = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
      instant_coor_b = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
      if line_judge(make_road_edge[4], inside_coor_2, instant_coor_b[0], instant_coor_b[1]):
        result.append([instant_coor_a, instant_coor_b])
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
          evaluation.append([instant_coor_a, instant_coor_b, inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], late_parcel[4], late_parcel[5]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
      else:
        non_in_road = [road_mid_line[0][0] - inside_coor_2[0], road_mid_line[0][1] - inside_coor_2[1]]
        instant_coor_b = [instant_coor_b[0] + non_in_road[0], instant_coor_b[1] + non_in_road[1]]
        result.append([instant_coor_a, instant_coor_b])
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], instant_coor_b, instant_coor_a])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
          evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2], late_parcel[3]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
  ###汎用的な記述ではない###
#####下区画の分割#####
  ###汎用的な記述ではない###
  goal_area_flag = False
  area_calc = []
  #道に沿って間口ベクトルの算出
  deviation = [(parcel_frame[2][0] - make_road_edge[3][0]), (parcel_frame[2][1] - make_road_edge[3][1])]
  parcel_deviation = [(parcel_frame[3][0] - parcel_frame[2][0]), (parcel_frame[3][1] - parcel_frame[2][1])]
  deviation_k = maguti / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
  instant_coor_b = [make_road_edge[3][0] - deviation[1] * deviation_k, make_road_edge[3][1] + deviation[0] * deviation_k]
  instant_coor_a = line_cross_point(parcel_frame[3], parcel_frame[2], instant_coor_b, [instant_coor_b[0] + deviation[0] * 3, instant_coor_b[1] + deviation[1] * 3])
  print("描画するaとb:" + str([instant_coor_a, instant_coor_b]))
  #指定座標がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[2]
    instant_coor_b = [instant_coor_a[0] - deviation[0], instant_coor_a[1] - deviation[1]]
    area_calc.append(instant_coor_a)
    area_calc.append(instant_coor_b)
    area_calc.append(make_road_edge[3])
  else:
    area_calc.append(instant_coor_a)
    area_calc.append(instant_coor_b)
    area_calc.append(make_road_edge[3])
    area_calc.append(parcel_frame[2])
  #完成した宅地の面積
  home_area = Calc.calc(area_calc)
  print("home_area:" + str(home_area))
  #目標面積に達していればフラグを建てる
  if home_area >= goal_area:
    goal_area_flag = True
  #面積が足りていない場合は線をずらす
  if not goal_area_flag:
    a=np.array(instant_coor_b)
    b=np.array(instant_coor_a)
    expand_area_distance = np.linalg.norm(b-a)
    expand_distance = (goal_area - home_area) / expand_area_distance
    expand_k = expand_distance / math.sqrt(parcel_deviation[0] * parcel_deviation[0] + parcel_deviation[1] * parcel_deviation[1])
    #角度を変えずに平行移動
    instant_coor_b = [instant_coor_b[0] + parcel_deviation[0] * expand_k, instant_coor_b[1] + parcel_deviation[1] * expand_k]
    instant_coor_a = [instant_coor_a[0] + parcel_deviation[0] * expand_k, instant_coor_a[1] + parcel_deviation[1] * expand_k]
    area_calc[0] = instant_coor_a
    area_calc[1] = instant_coor_b
  else:
    goal_area_flag = False
  evaluation.append(area_calc)
  print("描画するaとb:" + str([instant_coor_a, instant_coor_b]))
  print("下区画で追加する要素:" + str(area_calc))
  print("この時点の区画:" + str(evaluation))
  area_calc = []
  #座標の追加
  result.append([instant_coor_a, instant_coor_b])
  #後に割る区画として定義
  late_parcel = []
  late_parcel.append(instant_coor_b)
  late_parcel.append(instant_coor_a)
  #フラグの訂正
  road_frame_flag = False
  inside_parcel_flag = False
  #道の反対側の処理
  instant_coor_b = [road_inter_coor[1][0] + deviation[1] * deviation_k, road_inter_coor[1][1] - deviation[0] * deviation_k]
  #直角の座標を入手
  x = make_road_edge[0][0] - make_road_edge[1][0]
  y = make_road_edge[0][1] - make_road_edge[1][1]
  instant_coor_a = line_cross_point(parcel_frame[2], parcel_frame[3], instant_coor_b, [instant_coor_b[0] - x * 2, instant_coor_b[1] - y * 2])
  print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
  #指定の座標（下）がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[3]
    non_in_road = [road_mid_line[0][0] - inside_coor_1[0], road_mid_line[0][1] - inside_coor_1[1]]
    instant_coor_b = [instant_coor_a[0] - deviation[0] - non_in_road[0], instant_coor_a[1] - deviation[1] - non_in_road[1]]
    print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
  else:
    inside_parcel_flag = True
  instant_coor_a = [instant_coor_a[0], instant_coor_a[1]]
  #指定座標（上）が作成した進入経路上にあるかどうか
  if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
    road_frame_flag = True
    instant_coor_b = [instant_coor_b[0] - non_in_road[0], instant_coor_b[1] - non_in_road[1]]
  #4パターンの結果についてそれぞれ面積を求める
  if road_frame_flag and inside_parcel_flag:
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append(parcel_frame[3])
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
    area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
    area_calc.append(inside_coor_1)
  elif road_frame_flag and not inside_parcel_flag:
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
    area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
    area_calc.append(inside_coor_1)
  elif not road_frame_flag and inside_parcel_flag:
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append(parcel_frame[3])
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
  elif not road_frame_flag and not inside_parcel_flag:
    area_calc.append(instant_coor_b)
    area_calc.append(instant_coor_a)
    area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
  #完成した宅地の面積
  print("area_calc:" + str(area_calc))
  home_area = Calc.calc(area_calc)
  #目標面積に達していればフラグを建てる
  print("home_area:" + str(home_area))
  print("goal_area:" + str(goal_area))
  if (home_area >= goal_area):
    goal_area_flag = True
  #指定面積に満たなかった場合
  if not goal_area_flag:
    a=np.array(instant_coor_a)
    b=np.array(instant_coor_b)
    expand_area_distance = np.linalg.norm(b-a)
    expand_distance = (goal_area - home_area) / expand_area_distance
    expand_k = expand_distance / (deviation[0] * deviation[0] + deviation[1] * deviation[1])
    instant_coor_b = [instant_coor_b[0] + deviation[1] * expand_k, instant_coor_b[1] - deviation[0] * expand_k]
    instant_coor_a = [instant_coor_a[0] + deviation[1] * expand_k, instant_coor_a[1] - deviation[0] * expand_k]
    #平行移動によって指定座標（下）が進入経路に干渉してしまっている場合の処理
    if not road_frame_flag:
      if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
        #指定座標（下）を進入経路上に移動
        area_calc = []
        instant_coor_b = [instant_coor_b[0] - deviation[0] * deviation_k, instant_coor_b[1] - deviation[1] * deviation_k]
        #該当パターン2つについて面積を再度計算
        if road_frame_flag and inside_parcel_flag:
          area_calc.append(instant_coor_b)
          area_calc.append(instant_coor_a)
          area_calc.append(parcel_frame[3])
          area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
          area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
          area_calc.append(inside_coor_1)
        elif not road_frame_flag and inside_parcel_flag:
          area_calc.append(instant_coor_b)
          area_calc.append(instant_coor_a)
          area_calc.append(parcel_frame[3])
          area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
        #再計算された面積
        home_area = Calc.calc(area_calc)
        #目標面積に達していればフラグを建てる
        if home_area >= goal_area:
          goal_area_flag = True
        #面積が満たなければもう一度平行移動させて該当面積に到達させる
        else:
          a=np.array(instant_coor_a)
          b=np.array(instant_coor_b)
          expand_area_distance = np.linalg.norm(b-a)
          expand_distance = (goal_area - home_area) / expand_area_distance
          expand_p = expand_distance / (deviation[0] * deviation[0] + deviation[1] * deviation[1])
          instant_coor_b = [instant_coor_b[0] + deviation[1] * expand_p, instant_coor_b[1] - deviation[0] * expand_p]
          instant_coor_a = [instant_coor_a[0] + deviation[1] * expand_p, instant_coor_a[1] - deviation[0] * expand_p]
          if road_frame_flag and inside_parcel_flag:
            area_calc.append(instant_coor_b)
            area_calc.append(instant_coor_a)
            area_calc.append(parcel_frame[3])
            area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
            area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
            area_calc.append(inside_coor_1)
          elif not road_frame_flag and inside_parcel_flag:
            area_calc.append(instant_coor_b)
            area_calc.append(instant_coor_a)
            area_calc.append(parcel_frame[3])
            area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
  else:
    #フラグは元に戻しておく
    goal_area_flag = False
  evaluation.append(area_calc)
  area_calc = []
  #4パターンの結果についてそれぞれ面積を求める
  if road_frame_flag and inside_parcel_flag:
    late_parcel.append(instant_coor_a)
    late_parcel.append(instant_coor_b)
  elif road_frame_flag and not inside_parcel_flag:
    late_parcel.append(instant_coor_a)
    late_parcel.append(instant_coor_b)
  elif not road_frame_flag and inside_parcel_flag:
    late_parcel.append(instant_coor_a)
    late_parcel.append(instant_coor_b)
    late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
    late_parcel.append(inside_coor_2)
  elif not road_frame_flag and not inside_parcel_flag:
    late_parcel.append(instant_coor_a)
    late_parcel.append(instant_coor_b)
    late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
    late_parcel.append(inside_coor_2)
  road_frame_flag = False
  inside_parcel_flag = False
  area_calc = []
  #計算結果座標の追加
  result.append([instant_coor_a, instant_coor_b])
  #残りの区画を割る
  if len(late_parcel) == 4:
    #指定街区の辺の長さ
    a=np.array(late_parcel[0])
    b=np.array(late_parcel[3])
    road_distance = np.linalg.norm(b-a)
    #辺における間口・家の戸数・奥行の計算
    home_cnt = int(road_distance / maguti)
    late_deviation = [(late_parcel[3][0] - late_parcel[0][0]) / home_cnt, (late_parcel[3][1] - late_parcel[0][1]) / home_cnt]
    for i in range(1, home_cnt):
      instant_coor_b = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
      instant_coor_a = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
      result.append([instant_coor_a, instant_coor_b])
      if i == 1:
        evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
      elif i == home_cnt - 1:
        evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
        evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3]])
      else:
        evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
  elif len(late_parcel) == 6:
    #指定街区の辺の長さ
    a=np.array(late_parcel[1])
    b=np.array(late_parcel[2])
    road_distance = np.linalg.norm(b-a)
    #辺における間口・家の戸数・奥行の計算
    home_cnt = int(road_distance / maguti)
    late_deviation = [(late_parcel[1][0] - late_parcel[2][0]) / home_cnt, (late_parcel[1][1] - late_parcel[2][1]) / home_cnt]
    for i in range(1, home_cnt):
      instant_coor_b = [late_parcel[0][0] - late_deviation[0] * i, late_parcel[0][1] - late_deviation[1] * i]
      instant_coor_a = [late_parcel[1][0] - late_deviation[0] * i, late_parcel[1][1] - late_deviation[1] * i]
      if line_judge(make_road_edge[3], inside_coor_1, instant_coor_b[0], instant_coor_b[1]):
        result.append([instant_coor_a, instant_coor_b])
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b, [road_mid_line[0][0], road_mid_line[0][1]], inside_coor_1])
          evaluation.append([instant_coor_b, instant_coor_a, [road_mid_line[0][0], road_mid_line[0][1]], late_parcel[2], late_parcel[3]])
        else:
          evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
      else:
        non_in_road = [road_mid_line[0][0] - inside_coor_1[0], road_mid_line[0][1] - inside_coor_1[1]]
        instant_coor_b = [instant_coor_b[0] + non_in_road[0], instant_coor_b[1] + non_in_road[1]]
        result.append([instant_coor_a, instant_coor_b])
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b, [road_mid_line[0][0], road_mid_line[0][1]], inside_coor_1])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b, [road_mid_line[0][0], road_mid_line[0][1]], inside_coor_1])
          evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3]])
        else:
          evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b, [road_mid_line[0][0], road_mid_line[0][1]], inside_coor_1])
  ###汎用的な記述ではない###

  print("評価要素：" + str(evaluation))
  #面積充足率の計算
  area_rate_score = evaluate_calc.area_rate_calc(evaluation)
  #接道率の計算
  fin_road_edge = []
  for i in range(len(road_edge)):
    fin_road_edge.append(road_edge[i])
  fin_road_edge.append([make_road_edge[4], inside_coor_2])
  fin_road_edge.append([inside_coor_2, inside_coor_1])
  fin_road_edge.append([make_road_edge[3], inside_coor_1])
  accessibility_rate, hatazao_cnt = evaluate_calc.accessibility_calc(fin_road_edge, evaluation, road_width)

  #決まった区画を返却する

  #一旦
  print("デバッグ:" + str(road_mid_line) + " " + str(road_inter_coor))
  print("result:" + str(result))
  return result, area_rate_score, accessibility_rate, hatazao_cnt


#文字列の長さを返す
def size(moji):
	return len(moji.encode("SHIFT-JIS"))
#

#コマンドライン引数（道幅，間口，目標面積）
road_width=4000
maguti = 7600
goal_area = 100000000

#コマンドライン引数の二つ目から読み込み
for i in range(2,len(sys.argv)):
	#aから始まる情報はピッチに代入
	if re.match(r"/a",sys.argv[i]):
		road_width=float(sys.argv[i][2:len(sys.argv[i])])
  #bから始まる情報はkiten(基点)に代入
	elif re.match(r"/b",sys.argv[i]):
		maguti=int(sys.argv[i][2:len(sys.argv[i])])
  #cから始まる情報はgoal_area(面積)に代入
  # elif re.match(r"/c",sys.argv[i]):
	# 	goal_area=int(sys.argv[i][2:len(sys.argv[i])])
	#
#

print(sys.argv)
print(" ")
print("road_width:" + str(road_width))
print("maguti:" + str(maguti))
print("goal_area:" + str(goal_area))
print(" ")

#コマンドライン引数(temp.txt)の受け取り
file = sys.argv[1]

#読み取り専用で代入
f=open(file,mode="r")
print("hd")

#変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
road_edge = []
make_road_edge = []
frame = []
xy = []
datas = []
result = []
cp_frame = []
write_frame = []
area_rate_list = []
accessibility_rate_list = []
hatazao_list = []
hp_count = 0
line_flag_p = False
line_flag_q = False

#tempの中身を取得
for line in f:
	#hq(実行なし)は無視
  if re.match(r"hq",line):
    pass
  #hpの場合は座標取得
  elif re.match(r"hp",line):
    #一行ごとに読み込み
    xy=line.split()
    hp_count += 1
    #最初の二行は道を作成するための座標
    if hp_count == 1 or hp_count == 2:
      make_road_edge.append([float(xy[1]), float(xy[2])])
    #後半は図形の枠
    else:
      frame.append([float(xy[1]), float(xy[2])])
  #空白の場合も座標取得
  elif re.match(r" ",line):
    xy=line.split()
    datas.append([float(xy[0]),float(xy[1])])
    datas.append([float(xy[2]),float(xy[3])])
    #print(line,end="")
for i in range(len(frame)):
  for j in range(1, len(frame[i])):
    print(" " + str(frame[i][j - 1]) + " " + str(frame[i][j]))
f.close()

print("make_road_edge:" + str(make_road_edge))
print("frame:" + str(frame))
print("datas" + str(datas))

#本来の街区と指定した線を照らし合わせる
for i in range(len(frame) - 1):
  for j in range(0, len(datas), 2):
    #両方の点が線上にあればフラグを立てる
    line_flag_p = False
    line_flag_q = False
    #それぞれを変数に格納
    A_x, A_y = datas[j]
    B_x, B_y = datas[j + 1]
    P_x, P_y = frame[i]
    Q_x, Q_y = frame[i + 1]
    #一つ目の点の線上判定
    if ((A_x <= P_x and P_x <= B_x) or (B_x <= P_x and P_x <= A_x)):
      if ((A_y <= P_y and P_y <= B_y) or (B_y <= P_y and P_y <= A_y)):
          if (math.floor(((P_y * (A_x - B_x)) + (A_y * (B_x - P_x)) + (B_y * (P_x - A_x))) * 10 ** 3) / (10 ** 3) == 0):
              #点Pが線分AB上にある
              line_flag_p = True
    #二つ目の線上判定
    if ((A_x <= Q_x and Q_x <= B_x) or (B_x <= Q_x and Q_x <= A_x)):
      if ((A_y <= Q_y and Q_y <= B_y) or (B_y <= Q_y and Q_y <= A_y)):
          if (math.floor(((Q_y * (A_x - B_x)) + (A_y * (B_x - Q_x)) + (B_y * (Q_x - A_x))) * 10 ** 3) / (10 ** 3) == 0):
              #点Qが線分AB上にある
              line_flag_q = True

    # print("デバッグ")
    # print(math.floor(((P_y * (A_x - B_x)) + (A_y * (B_x - P_x)) + (B_y * (P_x - A_x))) * 10 ** 3) / (10 ** 3))
    # print(math.floor(((Q_y * (A_x - B_x)) + (A_y * (B_x - Q_x)) + (B_y * (Q_x - A_x))) * 10 ** 3) / (10 ** 3))
    # print("座標")
    # print(datas[j])
    # print(datas[j + 1])
    # print(frame[i])
    # print(frame[i + 1])
    # print(line_flag_p and line_flag_q)

    if not [frame[i], frame[i + 1]] == make_road_edge:
      #両方とも線上にあるときroad_edgeに座標を格納
      if line_flag_p and line_flag_q:
        road_edge.append([frame[i], frame[i + 1]])

#要書き換え！
road_edge = [road_edge[0], road_edge[1]]
print("road_edge:" + str(road_edge))

#dxfのversion指定
doc = ezdxf.new("R2010")

#モデル空間に新しいエンティティを作成
msp = doc.modelspace()
cp_frame = copy.deepcopy(frame)

#20回描画
for j in range(5):
  for k in range(4):
    cp_frame = copy.deepcopy(frame)
    write_frame = []
    write_result = []
    #区画割の実行
    result, area_rate_calc, accessibility_rate, hatazao_cnt = parcel_allocation(make_road_edge, frame, road_width, road_edge, maguti, goal_area)

    print("frame:" + str(frame))
    print("cp_frame:" + str(cp_frame))
    print("result:" + str(result))
    result = list(result)
    area_rate_list.append(area_rate_calc)
    accessibility_rate_list.append(accessibility_rate)
    hatazao_list.append(hatazao_cnt)
    print("result:" + str(result))
    print("area_rare_calc:" + str(area_rate_calc))
    print("accessibility_rate:" + str(accessibility_rate))
    print("hatzao_cnt:" + str(hatazao_cnt))
    print("area_rate:" + str(area_rate_list))
    print("accessibility_rate:" + str(accessibility_rate_list))
    print("hatazao_list:" + str(hatazao_list))

    #描画用のリストの作成
    for i in range(len(cp_frame) - 1):
      write_frame.append([cp_frame[i], cp_frame[i + 1]])
    write_result = copy.deepcopy(result)

  #枠の描画
    for i in range(len(cp_frame) - 1):
      #直線を作成
      write_frame[i][0] = list(write_frame[i][0])
      write_frame[i][1] = list(write_frame[i][1])
      write_frame[i][0][0] = write_frame[i][0][0] + j * 100000
      write_frame[i][1][0] = write_frame[i][1][0] + j * 100000
      write_frame[i][0][1] = write_frame[i][0][1] + k * 80000
      write_frame[i][1][1] = write_frame[i][1][1] + k * 80000
      print("write_frame:" + str(write_frame[i]))
      msp.add_line(start=write_frame[i][0], end=write_frame[i][1])

    #枠の描画
    for i in range(len(write_result)):
      #直線を作成
      write_result[i][0] = list(write_result[i][0])
      write_result[i][1] = list(write_result[i][1])
      write_result[i][0][0] = write_result[i][0][0] + j * 100000
      write_result[i][1][0] = write_result[i][1][0] + j * 100000
      write_result[i][0][1] = write_result[i][0][1] + k * 80000
      write_result[i][1][1] = write_result[i][1][1] + k * 80000
      msp.add_line(start=write_result[i][0], end=write_result[i][1])

    #枠データの再度読み込み
    frame = cp_frame
    print("cp_frame:" + str(cp_frame))

#点数計算
result_score = []
for i in range(len(area_rate_list)):
  #500点満点での計算
  score = 0
  can_access = 1 - accessibility_rate_list[i]
  score += 200 - area_rate_list[i] * 2
  score += 300 * (can_access + accessibility_rate_list[i] * 0.7)
  result_score.append(score)

print("result_score:" + str(result_score))

#保存
doc.saveas('line.dxf')