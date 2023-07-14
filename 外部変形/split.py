# -*- coding: utf-8 -*-
# from audioop import reverse
import codecs
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
import collections
import un_load

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
  # print((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x))
  # print((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y))
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


#####区画割の実行#####
def parcel_allocation(deep_make_road_edge, make_road_edge, parcel_frame, road_width, road_edge, maguti, goal_area):

  print("\n\n================================")
  print("区画割の実行 parcel_allocation")
  print("================================")

  print("make_road_edge:" + str(make_road_edge))
  print("parcel_frame:" + str(parcel_frame))
  print("road_width:" + str(road_width))
  print("road_edge:" + str(road_edge))
  print("maguti:" + str(maguti))
  print("goal_area:" + str(goal_area))

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
  make_road_edge = copy.deepcopy(deep_make_road_edge)
  cp_parcel_frame = copy.deepcopy(parcel_frame)

  #区画を計算できる形に回転
  frame_flag = False
  last_parcel = []
  #目的の方向になるまで回転させる．
  while not frame_flag:
    for i in range(len(parcel_frame)):
      if parcel_frame[i] == make_road_edge[0]:
        print("i(1にならないといけない):" + str(i))
        if i == 1:
          frame_flag = True
        else:
          last_parcel = parcel_frame[1]
          instant_parcel = copy.deepcopy(parcel_frame)
          print("last_parcel:" + str(last_parcel))
          for j in range(len(parcel_frame) - 1):
            parcel_frame[j] = instant_parcel[j + 1]
          parcel_frame[-1] = last_parcel
          break
    print("ネスト上 parcel_frame:" + str(parcel_frame))
  print("ネスト下 parcel_frame:" + str(parcel_frame))

  #道の角度を決定する(道作成辺に対して垂直，他の接道辺に平行) 今は90度だけでとりあえず
  angle_list = []
  angle_list.append(90)
  #街区の端から区画を決めていく ＜後で＞
  #接道している区画を決定する
  for k in range(len(road_edge)):
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
    print("calc:" + str(road_edge[k][1][0] - road_edge[k][0][0]))
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

  #道の場所を無作為にずらす（左右の間隔は少し開ける）
  z = random.uniform(0, 0.3)
  # n = random.randrange(-1,2,2)
  # nz = z * n
  start_road = [start_road[0] + x * z, start_road[1] + y * z]
  print("z:" + str(z))
  print("start_road:" + str(start_road))

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
  #ここの座標選択を定式化しないといけない！！！！！
  if not road_inter_coor[0] == line_cross_point(make_road_edge[0], make_road_edge[1], start_road, make_road_edge[2]):
    road_mid_line.append(road_inter_coor[0])
  else:
    road_mid_line.append(road_inter_coor[1])
  #道の入り口，行き止まりの四点を追加
  instant_result = [inside_coor_1, inside_coor_2]
  result.append(instant_result)
  result.append([make_road_edge[4], inside_coor_2])
  result.append([make_road_edge[3], inside_coor_1])
  #道の個数が出力結果の戸数になるため，50パターン*道の種類(とりあえず)
  result.append(road_mid_line)
  #残りの区画を決定する

  print("##################################")
  print("result:" + str(result))
  print("parcel_frame:" + str(parcel_frame))

#####上区画の分割#####
  ###汎用的な記述ではない###
  print("進入経路の上側の区画の分割")
  goal_area_flag = False
  area_calc = []
  #道に沿って間口ベクトルの算出
  deviation = [(parcel_frame[1][0] - make_road_edge[4][0]), (parcel_frame[1][1] - make_road_edge[4][1])]
  parcel_deviation = [(parcel_frame[0][0] - parcel_frame[1][0]), (parcel_frame[0][1] - parcel_frame[1][1])]
  road_deviation = [(make_road_edge[4][0] - inside_coor_2[0]), (make_road_edge[4][1] - inside_coor_2[1])]
  deviation_k = maguti / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
  instant_coor_b = [make_road_edge[4][0] + deviation[1] * deviation_k, make_road_edge[4][1] - deviation[0] * deviation_k]
  instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] - road_deviation[1] * 5, instant_coor_b[1] + road_deviation[0] * 5])

  print("                                    #")
  print("instant_coor_b:" + str(instant_coor_b))
  print("instant_coor_a:" + str(instant_coor_a))
  print("deviation" + str(deviation))
  print("parcel_deviation" + str(parcel_deviation))
  print("deviation_k" + str(deviation_k))
  print("parcel_frame" + str(parcel_frame))
  print("make_road_edge" + str(make_road_edge))
  print("                                    #")

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
  print("                                    ")
  print("instant_coor_b:" + str(instant_coor_b))
  print("instant_coor_a:" + str(instant_coor_a))
  print("                                    ")
  print("home_area:" + str(home_area))
  #目標面積に達していればフラグを建てる
  if home_area >= goal_area:
    goal_area_flag = True
  #面積が足りていない場合は線をずらす
  if not goal_area_flag:
    #目標面積を満たせていない場合繰り返し
    while True:
      instant_area = []
      a=np.array(instant_coor_b)
      b=np.array(instant_coor_a)
      expand_area_distance = np.linalg.norm(b-a)
      expand_distance = (goal_area - home_area + 2000000) / expand_area_distance
      expand_k = expand_distance / math.sqrt(road_deviation[0] * road_deviation[0] + road_deviation[1] * road_deviation[1])
      #角度を変えずに平行移動
      instant_coor_b = [instant_coor_b[0] - road_deviation[0] * expand_k, instant_coor_b[1] - road_deviation[1] * expand_k]
      instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] - road_deviation[1] * 5, instant_coor_b[1] + road_deviation[0] * 5])
      instant_area.append(instant_coor_b)
      instant_area.append(instant_coor_a)
      instant_area.append(parcel_frame[1])
      instant_area.append(make_road_edge[4])
      home_area = Calc.calc(instant_area)
      if home_area >= goal_area:
        break
    area_calc[0] = instant_coor_b
    area_calc[1] = instant_coor_a
  else:
    goal_area_flag = False
  evaluation.append(area_calc)
  area_calc = []
  #座標の追加
  result.append([instant_coor_a, instant_coor_b])

  print("result:" + str(result))
  print("evaluation:" + str(evaluation))

  #後に割る区画として定義
  late_parcel.append(instant_coor_a)
  late_parcel.append(instant_coor_b)
  road_frame_flag = False
  inside_parcel_flag = False
  instant_b_inroad = False
  #道の奥側の処理
  instant_coor_b = [road_mid_line[1][0] - deviation[1] * deviation_k, road_mid_line[1][1] + deviation[0] * deviation_k]
  #直角の座標を入手
  x = make_road_edge[1][0] - make_road_edge[0][0]
  y = make_road_edge[1][1] - make_road_edge[0][1]
  instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] - x * 2, instant_coor_b[1] - y * 2])
  print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
  #指定の座標（上）がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[0]
    non_road = [road_mid_line[0][0] - inside_coor_1[0], road_mid_line[0][1] - inside_coor_1[1]]
    instant_coor_b = [instant_coor_a[0] - deviation[0], instant_coor_a[1] - deviation[1]]
    print("各座標:" + str(instant_coor_a) + " " + str(instant_coor_b))
    instant_b_inroad = True
  else:
    inside_parcel_flag = True
  #形式を変更
  instant_coor_a = [instant_coor_a[0], instant_coor_a[1]]
  #指定座標（下）が作成した進入経路上にあるかどうか
  if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
    print("進入経路上")
    road_frame_flag = True
    instant_coor_b = [instant_coor_b[0] - (x * constant_k), instant_coor_b[1] - (y * constant_k)]
  #road_mid_lineがparcel_frameのどの辺上にあるかで場合分け
  decrease_parcel_flag = False
  if not line_judge(parcel_frame[0], parcel_frame[3], road_mid_line[1][0], road_mid_line[1][1]):
    decrease_parcel_flag = True
  #4パターンの結果についてそれぞれ面積を求める
  if not decrease_parcel_flag:
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
  else:
    if road_frame_flag and inside_parcel_flag:
      area_calc.append(instant_coor_b)
      area_calc.append(inside_coor_2)
      area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
      area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
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
  oku_kukaku_count = 0
  #面積に到達できた場合
  break_flag = True
  if not goal_area_flag:
    #目標面積に到達していない場合繰り返し
    while True:
      oku_kukaku_count += 1
      a=np.array(instant_coor_a)
      b=np.array(instant_coor_b)
      expand_area_distance = np.linalg.norm(b-a)
      expand_distance = (goal_area - home_area + 2000000) / expand_area_distance
      expand_k = expand_distance / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
      print("各要素:" + str(instant_coor_a) + ", " + str(instant_coor_b))
      instant_coor_b = [instant_coor_b[0] - deviation[1] * expand_k, instant_coor_b[1] + deviation[0] * expand_k]
      instant_coor_a = line_cross_point(parcel_frame[0], late_parcel[0], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
      print("expand_area_distance:" + str(expand_area_distance))
      print("expand_distance:" + str(expand_distance))
      print("home_area:" + str(home_area))
      print("expand_k:" + str(expand_k))
      print("各要素:" + str(instant_coor_a) + ", " + str(instant_coor_b))
      if instant_coor_a is None:
        if oku_kukaku_count == 1:
          instant_coor_b = [road_mid_line[1][0] - deviation[1] * deviation_k * 1.5, road_mid_line[1][1] + deviation[0] * deviation_k * 1.5]
          instant_coor_a = line_cross_point(parcel_frame[0], late_parcel[0], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
          road_frame_flag = False
          print("各要素:" + str(instant_coor_a) + ", " + str(instant_coor_b))
        else:
          break_flag = False
          break
      #平行移動によって指定座標（下）が進入経路に干渉してしまっている場合の処理
      if not road_frame_flag:
        if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
          if not instant_b_inroad:
            #指定座標（下）を進入経路上に移動
            instant_coor_b = [instant_coor_b[0] - (x * constant_k), instant_coor_b[1] - (y * constant_k)]
          else:
            #指定座標（下）をroad_mid_line上に移動
            instant_coor_b = [instant_coor_b[0] + (x * constant_k), instant_coor_b[1] + (y * constant_k)]
          road_frame_flag = True
          print("線上に移動")
        area_calc = []
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
      else:
        area_calc = []
        area_calc.append(instant_coor_b)
        area_calc.append(inside_coor_2)
        area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
        area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
        area_calc.append(parcel_frame[0])
        area_calc.append(instant_coor_a)

      #再計算された面積
      print("area_calc:" + str(area_calc))
      home_area = Calc.calc(area_calc)
      print("home_area:" + str(home_area))
      #目標面積に達していればフラグを建てる
      if home_area >= goal_area:
        goal_area_flag = True
        break
  else:
    #フラグは元に戻しておく
    goal_area_flag = False
  #評価対象として格納
  if break_flag:
    evaluation.append(area_calc)

  print("いろいろデバッグ")
  print("area_calc:" + str(area_calc))
  print("instant_coor_b:" + str(instant_coor_b))
  print("instant_coor_a:" + str(instant_coor_a))
  print("evaluation:" + str(evaluation))
  print("home_area:" + str(home_area))
  print("いろいろデバッグ")

  area_calc = []

  print("late_parcel:" + str(late_parcel))

  if not decrease_parcel_flag:
    if not instant_coor_a is None:
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
    else:
        if road_frame_flag and inside_parcel_flag:
          late_parcel.append(road_mid_line[1])
          late_parcel.append(parcel_frame[0])
        elif road_frame_flag and not inside_parcel_flag:
          late_parcel.append(road_mid_line[1])
          late_parcel.append(parcel_frame[0])
        elif not road_frame_flag and inside_parcel_flag:
          late_parcel.append(inside_coor_2)
          late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
          late_parcel.append(road_mid_line[1])
          late_parcel.append(parcel_frame[0])
        elif not road_frame_flag and not inside_parcel_flag:
          late_parcel.append(inside_coor_2)
          late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
          late_parcel.append(road_mid_line[1])
          late_parcel.append(parcel_frame[0])
  else:
    if not instant_coor_a is None:
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
    else:
        if road_frame_flag and inside_parcel_flag:
          late_parcel.append(road_mid_line[1])
        elif road_frame_flag and not inside_parcel_flag:
          late_parcel.append(road_mid_line[1])
        elif not road_frame_flag and inside_parcel_flag:
          late_parcel.append(inside_coor_2)
          late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
          late_parcel.append(road_mid_line[1])
        elif not road_frame_flag and not inside_parcel_flag:
          late_parcel.append(inside_coor_2)
          late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
          late_parcel.append(road_mid_line[1])
  road_frame_flag = False
  inside_parcel_flag = False
  area_calc = []
  #残りの面積を算出
  home_area = Calc.calc(late_parcel)
  #作成できる宅地の個数を計算
  home_cnt = int(home_area / goal_area)
  if not instant_coor_a is None:
    #計算結果座標の追加
    result.append([instant_coor_a, instant_coor_b])
  #残りの区画を割る
  #頂点が三つの場合
  if len(late_parcel) == 3:
    #中に作れる家の戸数で場合分け
    #つくれない場合
    if home_cnt == 0:
      print("もう家が作れません")
    #一つだけ作成可能の場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の家が立てられる場合
    else:
      #残りの敷地を立てられる個数分割ったベクトルを生成
      late_deviation = [(late_parcel[2][0] - late_parcel[1][0]) / home_cnt, (late_parcel[2][1] - late_parcel[1][1]) / home_cnt]
      #家の戸数分ループ
      for i in range(1, home_cnt):
        instant_coor_b = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
        instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
        result.append([instant_coor_a, instant_coor_b])
        #算出した区画毎に評価用配列に格納
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
          evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
  elif len(late_parcel) == 4:
    #辺における間口・家の戸数・奥行の計算
    print("isnide_coor_2:" + str(inside_coor_2))
    print("instant_a:" + str(instant_coor_a))
    print("instant_b:" + str(instant_coor_b))
    print("road_mid_line:" + str(road_mid_line))
    print("late_parcel:" + str(late_parcel))
    print("################## " + str(road_distance) + " " + str(maguti))
    #家が作れない場合は終了
    if home_cnt == 0:
      print("もう家が作れません")
    #一つだけ作成可能の場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の家が建てられる場合
    else:
      late_deviation = [(late_parcel[2][0] - late_parcel[1][0]) / home_cnt, (late_parcel[2][1] - late_parcel[1][1]) / home_cnt]
      #家の戸数分ループ
      for i in range(1, home_cnt):
        instant_coor_b = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
        instant_coor_a = line_cross_point(parcel_frame[0], parcel_frame[1], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
        result.append([instant_coor_a, instant_coor_b])
        #算出結果を評価用配列に格納
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
          evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2], late_parcel[3]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
  elif len(late_parcel) == 5:
    print("isnide_coor_2:" + str(inside_coor_2))
    print("instant_a:" + str(instant_coor_a))
    print("instant_b:" + str(instant_coor_b))
    print("road_mid_line:" + str(road_mid_line))
    print("late_parcel:" + str(late_parcel))
    print("################## " + str(road_distance) + " " + str(maguti))
    if home_cnt == 0:
      print("操作終了")
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    else:
      late_deviation = [(late_parcel[4][0] - late_parcel[0][0]) / home_cnt, (late_parcel[4][1] - late_parcel[0][1]) / home_cnt]
      for i in range(1, home_cnt):
        instant_coor_a = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
        instant_coor_b = line_cross_point(late_parcel[1], late_parcel[2], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
        print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        if instant_coor_b is None:
          instant_coor_b = line_cross_point(late_parcel[3], late_parcel[4], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
          print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        result.append([instant_coor_a, instant_coor_b])
        #座標の追加・評価関数配列に格納
        if line_judge(late_parcel[1], late_parcel[2], instant_coor_b[0], instant_coor_b[1]):
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
            evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2], late_parcel[3], late_parcel[4]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
        else:
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], instant_coor_b, instant_coor_a])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
            evaluation.append([instant_coor_a, instant_coor_b, late_parcel[4]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])

  elif len(late_parcel) == 6:
    print("home_cnt:" + str(home_cnt))
    print("isnide_coor_2:" + str(inside_coor_2))
    print("instant_a:" + str(instant_coor_a))
    print("instant_b:" + str(instant_coor_b))
    print("road_mid_line:" + str(road_mid_line))
    print("late_parcel:" + str(late_parcel))
    print("################## " + str(road_distance) + " " + str(maguti))
    #一つも宅地が作れない場合
    if home_cnt == 0:
      print("操作終了")
    #一つしか宅地を作成できない場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の宅地を作成できる場合
    else:
      late_deviation = [(late_parcel[5][0] - late_parcel[0][0]) / home_cnt, (late_parcel[5][1] - late_parcel[0][1]) / home_cnt]
      for i in range(1, home_cnt):
        instant_coor_a = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
        instant_coor_b = line_cross_point(late_parcel[1], late_parcel[2], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
        print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        if instant_coor_b is None:
          instant_coor_b = line_cross_point(late_parcel[3], late_parcel[4], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
          print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        result.append([instant_coor_a, instant_coor_b])
        #座標の追加・評価関数配列に格納
        if line_judge(make_road_edge[4], inside_coor_2, instant_coor_b[0], instant_coor_b[1]):
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
            evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2], late_parcel[3], late_parcel[4], late_parcel[5]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
        else:
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], instant_coor_b, instant_coor_a])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
            evaluation.append([instant_coor_a, instant_coor_b, late_parcel[4], late_parcel[5]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (home_cnt - i + 1), late_parcel[1][1] - late_deviation[1] * (home_cnt - i + 1)], inside_coor_2, [road_mid_line[0][0], road_mid_line[0][1]], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
    ###汎用的な記述ではない###

#####下区画の分割#####
  ###汎用的な記述ではない###
  print("進入経路の下側の区画の分割")
  goal_area_flag = False
  area_calc = []
  #道に沿って間口ベクトルの算出
  deviation = [(parcel_frame[2][0] - make_road_edge[3][0]), (parcel_frame[2][1] - make_road_edge[3][1])]
  parcel_deviation = [(parcel_frame[3][0] - parcel_frame[2][0]), (parcel_frame[3][1] - parcel_frame[2][1])]
  road_deviation = [(make_road_edge[3][0] - inside_coor_1[0]), (make_road_edge[3][1] - inside_coor_2[1])]
  deviation_k = maguti / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
  instant_coor_b = [make_road_edge[3][0] - deviation[1] * deviation_k, make_road_edge[3][1] + deviation[0] * deviation_k]
  instant_coor_a = line_cross_point(parcel_frame[3], parcel_frame[2], instant_coor_b, [instant_coor_b[0] + deviation[0] * 3, instant_coor_b[1] + deviation[1] * 3])
  print("                                    #")
  print("もう半分の区画:" + str(late_parcel))
  print("instant_coor_b:" + str(instant_coor_b))
  print("instant_coor_a:" + str(instant_coor_a))
  print("deviation:" + str(deviation))
  print("parcel_deviation:" + str(parcel_deviation))
  print("deviation_k:" + str(deviation_k))
  print("parcel_frame:" + str(parcel_frame))
  print("make_road_edge:" + str(make_road_edge))
  print("                                    #")
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
  print("area_calc:" + str(area_calc))
  print("home_area:" + str(home_area))
  print("goal_area:" + str(goal_area))
  #目標面積に達していればフラグを建てる
  if home_area >= goal_area:
    goal_area_flag = True
    print("目標面積に到達:" + str(home_area))
  #面積が足りていない場合は線をずらす
  if not goal_area_flag:
    #目標面積を満たせていない場合繰り返し
    while True:
      instant_area = []
      a=np.array(instant_coor_b)
      b=np.array(instant_coor_a)
      expand_area_distance = np.linalg.norm(b-a)
      #ナナメでも目標目標を満たすための操作しようね
      expand_distance = (goal_area - home_area + 2000000) / expand_area_distance
      expand_k = expand_distance / math.sqrt(road_deviation[0] * road_deviation[0] + road_deviation[1] * road_deviation[1])
      #角度を変えずに平行移動
      instant_coor_b = [instant_coor_b[0] - road_deviation[0] * expand_k, instant_coor_b[1] - road_deviation[1] * expand_k]
      instant_coor_a = line_cross_point(parcel_frame[2], parcel_frame[3], instant_coor_b, [instant_coor_b[0] - road_deviation[1] * 5, instant_coor_b[1] + road_deviation[0] * 5])
      if line_judge(make_road_edge[3], inside_coor_1, instant_coor_b[0], instant_coor_b[1]):
        instant_area.append(instant_coor_b)
        instant_area.append(make_road_edge[3])
        instant_area.append(parcel_frame[2])
        instant_area.append(instant_coor_a)
        home_area = Calc.calc(instant_area)
      else:
        non_in_road = [road_mid_line[0][0] - inside_coor_1[0], road_mid_line[0][1] - inside_coor_1[1]]
        instant_coor_b = [instant_coor_b[0] + non_in_road[0], instant_coor_b[1] + non_in_road[1]]
        instant_area.append(instant_coor_b)
        instant_area.append(road_mid_line[0])
        instant_area.append(inside_coor_1)
        instant_area.append(make_road_edge[3])
        instant_area.append(parcel_frame[2])
        instant_area.append(instant_coor_a)
        home_area = Calc.calc(instant_area)
      print("instant_area:" + str(instant_area))
      print("home_area:" + str(home_area))
      if home_area >= goal_area:
        break
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

  #下側の座標が表示される可能範囲を代入
  limit_coor = copy.deepcopy(instant_coor_a)
  print("limit_coor:" + str(limit_coor))

  #後に割る区画として定義
  late_parcel = []
  late_parcel.append(instant_coor_b)
  late_parcel.append(instant_coor_a)
  #フラグの訂正
  road_frame_flag = False
  inside_parcel_flag = False
  #道の反対側の処理
  instant_coor_b = [road_mid_line[1][0] + deviation[1] * deviation_k, road_mid_line[1][1] - deviation[0] * deviation_k]
  #直角の座標を入手
  x = make_road_edge[0][0] - make_road_edge[1][0]
  y = make_road_edge[0][1] - make_road_edge[1][1]
  instant_coor_a = line_cross_point(late_parcel[1], parcel_frame[3], instant_coor_b, [instant_coor_b[0] - x * 2, instant_coor_b[1] - y * 2])
  non_in_road = [inside_coor_1[0] - road_mid_line[0][0], inside_coor_1[1] - road_mid_line[0][1]]
  print("各座標:" + str(instant_coor_a) + ", " + str(instant_coor_b))
  print("残りの区画:" + str(late_parcel))
  #指定の座標（下）がparcel内にあるかどうか
  if instant_coor_a is None:
    instant_coor_a = parcel_frame[3]
    instant_coor_b = [instant_coor_a[0] - deviation[0], instant_coor_a[1] - deviation[1]]
    print("各座標:" + str(instant_coor_a) + ", " + str(instant_coor_b))
  else:
    inside_parcel_flag = True
  #配列の形式に変更
  instant_coor_a = [instant_coor_a[0], instant_coor_a[1]]
  #指定座標（上）が作成した進入経路上にあるかどうか
  if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
    print("進入経路上")
    road_frame_flag = True
    instant_coor_b = [instant_coor_b[0] + non_in_road[0], instant_coor_b[1] + non_in_road[1]]
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
  oku_kukaku_count = 0
  if not goal_area_flag:
    #目標面積に到達していない場合繰り返し
    while True:
      oku_kukaku_count += 1
      a=np.array(instant_coor_a)
      b=np.array(instant_coor_b)
      expand_area_distance = np.linalg.norm(b-a)
      expand_distance = (goal_area - home_area) / expand_area_distance
      expand_k = expand_distance / math.sqrt(deviation[0] * deviation[0] + deviation[1] * deviation[1])
      instant_coor_b = [instant_coor_b[0] + deviation[1] * expand_k, instant_coor_b[1] - deviation[0] * expand_k]
      instant_coor_a = line_cross_point(parcel_frame[2], parcel_frame[3], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
      if instant_coor_a is None:
        if oku_kukaku_count == 1 and not road_frame_flag:
          instant_coor_b = [road_mid_line[1][0] + non_in_road[0], road_mid_line[1][1] + non_in_road[0]]
          instant_coor_a = line_cross_point(limit_coor, parcel_frame[3], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
          road_frame_flag = True
        else:
          break
      #平行移動によって指定座標（下）が進入経路に干渉してしまっている場合の処理
      if not road_frame_flag:
        if not line_judge(road_mid_line[0], road_mid_line[1], instant_coor_b[0], instant_coor_b[1]):
          #指定座標（下）を進入経路上に移動
          instant_coor_b = [instant_coor_b[0] + non_in_road[0], instant_coor_b[1] + non_in_road[1]]
          road_frame_flag = True
          print("線上に移動")
        area_calc = []
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
      else:
        area_calc = []
        area_calc.append(instant_coor_b)
        area_calc.append(instant_coor_a)
        area_calc.append(parcel_frame[3])
        area_calc.append([road_mid_line[1][0], road_mid_line[1][1]])
        area_calc.append([road_mid_line[0][0], road_mid_line[0][1]])
        area_calc.append(inside_coor_1)
      #再計算された面積
      print("area_calc:" + str(area_calc))
      home_area = Calc.calc(area_calc)
      print("home_area:" + str(home_area))
      #目標面積に達していればフラグを建てる
      if home_area >= goal_area:
        goal_area_flag = True
        break
  else:
    #フラグは元に戻しておく
    goal_area_flag = False
  #評価用配列に格納
  evaluation.append(area_calc)

  print("いろいろデバッグ:" + str(area_calc))
  print("いろいろデバッグ:" + str(instant_coor_b))
  print("いろいろデバッグ:" + str(instant_coor_a))
  print("いろいろデバッグ:" + str(home_area))
  print("late_parcel:" + str(late_parcel))
  area_calc = []

  if not instant_coor_a is None:
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
      late_parcel.append(inside_coor_1)
    elif not road_frame_flag and not inside_parcel_flag:
      late_parcel.append(instant_coor_a)
      late_parcel.append(instant_coor_b)
      late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
      late_parcel.append(inside_coor_1)
  else:
    if road_frame_flag and inside_parcel_flag:
      late_parcel.append(parcel_frame[3])
      late_parcel.append(road_mid_line[1])
    elif road_frame_flag and not inside_parcel_flag:
      late_parcel.append(parcel_frame[3])
      late_parcel.append(road_mid_line[1])
    elif not road_frame_flag and inside_parcel_flag:
      late_parcel.append(parcel_frame[3])
      late_parcel.append(road_mid_line[1])
      late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
      late_parcel.append(inside_coor_1)
    elif not road_frame_flag and not inside_parcel_flag:
      late_parcel.append(parcel_frame[3])
      late_parcel.append(road_mid_line[1])
      late_parcel.append([road_mid_line[0][0], road_mid_line[0][1]])
      late_parcel.append(inside_coor_1)
  road_frame_flag = False
  inside_parcel_flag = False
  area_calc = []
  #残りの面積を算出
  home_area = Calc.calc(late_parcel)
  #作成できる宅地の個数を計算
  home_cnt = int(home_area / goal_area)
  if not instant_coor_a is None:
    #計算結果座標の追加
    result.append([instant_coor_a, instant_coor_b])
    print("座標情報の追加")
  #残りの区画を割る
  if len(late_parcel) == 3:
    #家を作成できない場合
    if home_cnt == 0:
      print("もう家が作れません")
    #一つだけ作成可能の場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の宅地を作成できる場合
    else:
      #残りの敷地を立てられる戸数分割ったベクトルを生成
      late_deviation = [(late_parcel[2][0] - late_parcel[0][0]) / home_cnt, (late_parcel[2][1] - late_parcel[0][1]) / home_cnt]
      #家の戸数分ループ
      for i in range(1, home_cnt):
        instant_coor_b = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
        instant_coor_a = line_cross_point(parcel_frame[1], parcel_frame[2], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
        result.append([instant_coor_a, instant_coor_b])
        #算出した区画毎に評価用配列に格納
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_b, instant_coor_a])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
          evaluation.append([instant_coor_a, instant_coor_b, late_parcel[2]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_b, instant_coor_a])
  elif len(late_parcel) == 4:
    #家が作れない場合は終了
    if home_cnt == 0:
      print("もう家が作れません")
    #一つだけ作成可能の場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の家が建てられる場合
    else:
      late_deviation = [(late_parcel[3][0] - late_parcel[0][0]) / home_cnt, (late_parcel[3][1] - late_parcel[0][1]) / home_cnt]
      #家の戸数分ループ
      for i in range(1, home_cnt):
        instant_coor_b = [late_parcel[0][0] + late_deviation[0] * i, late_parcel[0][1] + late_deviation[1] * i]
        instant_coor_a = line_cross_point(parcel_frame[2], parcel_frame[3], instant_coor_b, [instant_coor_b[0] + deviation[0] * 5, instant_coor_b[1] + deviation[1] * 5])
        result.append([instant_coor_a, instant_coor_b])
        if i == 1:
          evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
        elif i == home_cnt - 1:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
          evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3]])
        else:
          evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
  elif len(late_parcel) == 5:
    print("isnide_coor_2:" + str(inside_coor_2))
    print("instant_a:" + str(instant_coor_a))
    print("instant_b:" + str(instant_coor_b))
    print("road_mid_line:" + str(road_mid_line))
    print("late_parcel:" + str(late_parcel))
    # print("################## " + str(road_distance) + " " + str(maguti))
    #家が建てられない場合
    if home_cnt == 0:
      print("操作終了")
    #一つしか家が建てられない場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の宅地が作成可能な場合
    else:
      late_deviation = [(late_parcel[2][0] - late_parcel[1][0]) / home_cnt, (late_parcel[2][1] - late_parcel[1][1]) / home_cnt]
      for i in range(1, home_cnt):
        instant_coor_a = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
        instant_coor_b = line_cross_point(late_parcel[0], late_parcel[4], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
        print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        if instant_coor_b is None:
          instant_coor_b = line_cross_point(late_parcel[2], late_parcel[3], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
          print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        #座標の追加・評価関数配列に格納
        result.append([instant_coor_a, instant_coor_b])
        if line_judge(late_parcel[0], late_parcel[4], instant_coor_b[0], instant_coor_b[1]):
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
            evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3], late_parcel[4]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
        else:
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
            evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2]])
          else:
            evaluation.append([[late_parcel[0][0] + late_deviation[0] * (i - 1), late_parcel[0][1] + late_deviation[1] * (i - 1)], [late_parcel[1][0] + late_deviation[0] * (i - 1), late_parcel[1][1] + late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
  elif len(late_parcel) == 6:
    print("home_cnt:" + str(home_cnt))
    print("isnide_coor_2:" + str(inside_coor_2))
    print("instant_a:" + str(instant_coor_a))
    print("instant_b:" + str(instant_coor_b))
    print("road_mid_line:" + str(road_mid_line))
    print("late_parcel:" + str(late_parcel))
    # print("################## " + str(road_distance) + " " + str(maguti))
    #一つも宅地が作れない場合
    if home_cnt == 0:
      print("操作終了")
    #一つしか宅地を作成できない場合
    elif home_cnt == 1:
      print("一つ分のスペースのみ存在")
      evaluation.append(late_parcel)
      print("evaluation:" + str(evaluation))
    #複数の宅地を作成できる場合
    else:
      late_deviation = [(late_parcel[2][0] - late_parcel[1][0]) / home_cnt, (late_parcel[2][1] - late_parcel[1][1]) / home_cnt]
      for i in range(1, home_cnt):
        instant_coor_a = [late_parcel[1][0] + late_deviation[0] * i, late_parcel[1][1] + late_deviation[1] * i]
        instant_coor_b = line_cross_point(late_parcel[0], late_parcel[5], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
        print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        if instant_coor_b is None:
          instant_coor_b = line_cross_point(late_parcel[3], late_parcel[4], instant_coor_a, [instant_coor_a[0] - deviation[0] * 5, instant_coor_a[1] - deviation[1] * 5])
          print("指定座標範囲判定・instant_coor_b:" + str(instant_coor_b))
        result.append([instant_coor_a, instant_coor_b])
        #座標の追加・評価関数配列に格納
        if line_judge(late_parcel[0], late_parcel[5], instant_coor_b[0], instant_coor_b[1]):
          # result.append([instant_coor_a, instant_coor_b])
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
            evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3], late_parcel[4], late_parcel[5]])
          else:
            evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
        else:
          if i == 1:
            evaluation.append([late_parcel[0], late_parcel[1], instant_coor_a, instant_coor_b, [road_mid_line[0][0], road_mid_line[0][1]], inside_coor_1])
          elif i == home_cnt - 1:
            evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
            evaluation.append([instant_coor_b, instant_coor_a, late_parcel[2], late_parcel[3]])
          else:
            evaluation.append([[late_parcel[0][0] - late_deviation[0] * (i - 1), late_parcel[0][1] - late_deviation[1] * (i - 1)], [late_parcel[1][0] - late_deviation[0] * (i - 1), late_parcel[1][1] - late_deviation[1] * (i - 1)], instant_coor_a, instant_coor_b])
  ###汎用的な記述ではない###

  print("評価要素：" + str(evaluation))
  cp_evaluation = copy.deepcopy(evaluation)

  #評価用の配列の定義
  fin_road_edge = []
  detail_list = []
  #評価に使う道路辺の格納
  for i in range(len(road_edge)):
    fin_road_edge.append(road_edge[i])
  fin_road_edge.append([make_road_edge[4], inside_coor_2])
  # fin_road_edge.append([inside_coor_2, inside_coor_1])
  fin_road_edge.append([make_road_edge[3], inside_coor_1])
  print("街区における道路辺配列:" + str(fin_road_edge))

  #評価の実行
  detail_list, total_score, total_score_margin = evaluate_calc.eval(fin_road_edge, cp_evaluation, road_width, goal_area)
  print("detail_list:" + str(detail_list))
  print("total_score:" + str(total_score))
  print("total_score_marigin:" + str(total_score_margin))
  print("cp_parcel_frame:" + str(cp_parcel_frame))
  print("cp_evaluation:" + str(cp_evaluation))

  #街区を計算用のリストに更新
  # calc_parcel_frame = cp_parcel_frame.remove(cp_parcel_frame[0][-1])
  # print("calc_parcel_frame:" + str(calc_parcel_frame))

  #有効宅地面積の計算
  yuko_menseki = evaluate_calc.yuko_calc(cp_evaluation, cp_parcel_frame[:-1])
  print("yuko_menseki:" + str(yuko_menseki))
  detail_list.append(yuko_menseki)

  #結果の返却
  print("デバッグ:" + str(road_mid_line) + " " + str(road_inter_coor))
  print("result:" + str(result))
  return result, detail_list, total_score, evaluation, total_score_margin






#####メインプログラム#####
#読み込み用のファイルを展開
print("================================")
print("メインプログラム split.py")
print("================================")
info = open('外部変形/information.txt','r',encoding='shift_jis')
print("hd")

#変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
road_edge_pt = []
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
rm_list = []
line_count = 0
least_maguti = 0
line_flag_p = False
line_flag_q = False

#infomationの行数の取得
for i in info:
  line_count += 1
  print("デバッグ" + str(i))

print("line_count:" + str(line_count))
info = open('外部変形/information.txt','r',encoding='shift_jis')

if line_count == 6:
  #カウントの初期化
  line_count = 0
  print("line_count:" + str(line_count))
  #infomationの中身を取得
  for line in info:
    print("デバッグ１")
    #一行ごとに読み込み
    xy=line.split()
    print(xy)
    # print(len(xy))
    #間口の読み込み
    if line_count == 0:
      maguti = float(xy[0])
    #目標面積の読み込み
    elif line_count == 1:
      goal_area = float(xy[0])
    #接道辺の読み込み
    elif line_count == 2:
      for i in range(0, len(xy), 2):
        # print(i)
        road_edge_pt.append([float(xy[i]), float(xy[i + 1])])
    #道幅の読み込み
    elif line_count == 3:
      road_width = float(xy[0])
    #街区の読み込み
    elif line_count == 4:
      for i in range(0, len(xy), 2):
        frame.append([float(xy[i]), float(xy[i + 1])])
    #道作成辺の読み込み
    elif line_count == 5:
      make_road_edge = [[float(xy[0]), float(xy[1])], [float(xy[2]), float(xy[3])]]
    #次行に移動
    line_count += 1
  print("デバッグ２")


  print("road_edge_pt:" + str(road_edge_pt))
  # print("road_edge_pt:" + str(road_edge_pt[0]))
  # print("road_edge_pt:" + str(road_edge_pt[1]))
  # print("road_edge_pt:" + str(road_edge_pt[0][0]))

  #ふたつずつ座標をまとめる：road_edge
  for i in range(int(len(road_edge_pt) / 2)):
    road_edge.append([road_edge_pt[i * 2], road_edge_pt[i * 2 + 1]])

  print("road_edge:" + str(road_edge))
  # print("road_edge:" + str(road_edge[0]))
  # print("road_edge:" + str(road_edge[1]))
  # print("road_edge:" + str(road_edge[0][0]))
  # print("road_edge:" + str(road_edge[1][0]))

  print(str(len(road_edge)))
  print("make_road_edge:" + str(make_road_edge))
  print("make_road_edge:" + str(make_road_edge[0]))

  #道作成辺と被っているものを削除
  for i in range(len(road_edge)):
    print(i)
    print(road_edge[i][0])
    if road_edge[i][0] == make_road_edge[0]:
      if road_edge[i][1] == make_road_edge[1]:
        rm_list.append(i)

  #余計な道を削除
  for i in range(len(rm_list)):
    road_edge.remove(road_edge[rm_list[i]])

  #毎回道作成辺をもとに戻す
  deep_make_road_edge = copy.deepcopy(make_road_edge)

  print(" ")
  print("road_width:" + str(road_width))
  print("maguti:" + str(maguti))
  print("goal_area:" + str(goal_area))
  print("make_road_edge:" + str(make_road_edge))
  print("frame:" + str(frame))
  print("road_edge:" + str(road_edge))
  print(" ")



  #dxfのversion指定
  doc = ezdxf.new("R2010")

  #モデル空間に新しいエンティティを作成
  msp = doc.modelspace()
  draw_cnt = 0

  #上位描画用のリスト作成
  result_index = []
  score_index = []
  score_index_margin = []
  detail_index = []
  evaluation_index = []

  #20回描画
  for i in range(30):
    cp_frame = copy.deepcopy(frame)
    draw_cnt += 1
    #区画割の実行
    print("現在の図面" + str(draw_cnt) + "個目")

    #区画割の実行
    result, detail_list, total_score, evaluation, total_score_margin = parcel_allocation(deep_make_road_edge, make_road_edge, cp_frame, road_width, road_edge, maguti, goal_area)
    #リスト化
    result = list(result)
    #結果をそれぞれのindexに追加
    result_index.append(result)
    score_index.append(total_score)
    score_index_margin.append(total_score_margin)
    detail_index.append(detail_list)
    evaluation_index.append(evaluation)

  print(score_index)
  print(sorted(score_index)[-1])
  #上位要素順に並び替え
  index_index = []
  #格納対象配列の高得点を上位から任意の個数抽出
  for i in range(1, 21, 1):
    target_num = sorted(score_index)[-i]
    index_index.append(target_num)

  print(index_index)
  #同じ得点の得点と個数を抽出
  material = [k for k, v in collections.Counter(index_index).items() if v > 1]
  count = [v for k, v in collections.Counter(index_index).items() if v > 1]
  #同じ得点のものは小さい加点で差をつける
  for i in range(len(material)):
    for j in range(count[i]):
      print(score_index.index(material[i]))
      score_index[score_index.index(material[i])] = score_index[score_index.index(material[i])] + 0.0001 * j
  #点数を調整して再度任意の個数を抽出
  index_index = []
  cp_result_index = []
  cp_detail_index = []
  cp_score_index = []
  cp_evaluation_index = []

  debag = []

  #任意の個数上位要素をresultとdetailに追加
  for i in range(1, 21, 1):
    #任意の上位個数を抽出
    target_num = sorted(score_index)[-i]
    index_index.append(target_num)
    cp_result_index.append(result_index[score_index.index(target_num)])
    cp_detail_index.append(detail_index[score_index.index(target_num)])
    cp_score_index.append(score_index[score_index.index(target_num)])
    cp_evaluation_index.append(evaluation_index[score_index.index(target_num)])
    debag.append(score_index.index(target_num))

  print("まとめ")
  kosu_count = []
  for i in range(len(cp_evaluation_index)):
    kosu_count.append(len(cp_evaluation_index[i]))
  print("cp_result_index:" + str(cp_result_index))
  print("cp_detail_index:" + str(cp_detail_index))
  print("cp_score_index:" + str(cp_score_index))
  print("cp_evaluation_index:" + str(cp_evaluation_index))
  print("それぞれの戸数:" + str(kosu_count))
  print("index_index:" + str(index_index))
  print("result_index:" + str(result_index))
  print("detail_index:" + str(detail_index))
  print("score_index:" + str(score_index))
  print("evaluation_index:" + str(evaluation_index))
  print("debag:" + str(debag))

  #20回描画
  write_count = 0
  for j in range(5):
    for k in range(4):
      cp_frame = copy.deepcopy(frame)
      write_frame = []
      write_result = []
      detail_list = []

      print("frame:" + str(frame))
      print("cp_frame:" + str(cp_frame))
      print("write_count:" + str(write_count))

      #描画用配列の作成
      for i in range(len(cp_frame) - 1):
        write_frame.append([cp_frame[i], cp_frame[i + 1]])
      write_result = copy.deepcopy(cp_result_index[write_count])
      print(write_frame)

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
      write_count += 1

  print(score_index_margin)
  print(sorted(score_index_margin)[-1])
  #上位要素順に並び替え
  index_index = []
  #格納対象配列の高得点を上位から任意の個数抽出
  for i in range(1, 21, 1):
    target_num = sorted(score_index_margin)[-i]
    index_index.append(target_num)

  print(index_index)
  #同じ得点の得点と個数を抽出
  material = [k for k, v in collections.Counter(index_index).items() if v > 1]
  count = [v for k, v in collections.Counter(index_index).items() if v > 1]
  #同じ得点のものは小さい加点で差をつける
  for i in range(len(material)):
    for j in range(count[i]):
      print(score_index_margin.index(material[i]))
      score_index_margin[score_index_margin.index(material[i])] = score_index_margin[score_index_margin.index(material[i])] + 0.0001 * j
  #点数を調整して再度任意の個数を抽出
  index_index = []
  cp_result_index = []
  cp_detail_index = []
  cp_score_index_margin = []
  cp_evaluation_index = []

  debag = []

  #任意の個数上位要素をresultとdetailに追加
  for i in range(1, 21, 1):
    #任意の上位個数を抽出
    target_num = sorted(score_index_margin)[-i]
    index_index.append(target_num)
    cp_result_index.append(result_index[score_index_margin.index(target_num)])
    cp_detail_index.append(detail_index[score_index_margin.index(target_num)])
    cp_score_index_margin.append(score_index_margin[score_index_margin.index(target_num)])
    cp_evaluation_index.append(evaluation_index[score_index_margin.index(target_num)])
    debag.append(score_index_margin.index(target_num))

  print("まとめ")
  kosu_count = []
  for i in range(len(cp_evaluation_index)):
    kosu_count.append(len(cp_evaluation_index[i]))
  print("cp_result_index:" + str(cp_result_index))
  print("cp_detail_index:" + str(cp_detail_index))
  print("cp_score_index_margin:" + str(cp_score_index_margin))
  print("cp_evaluation_index:" + str(cp_evaluation_index))
  print("それぞれの戸数:" + str(kosu_count))
  print("index_index:" + str(index_index))
  print("result_index:" + str(result_index))
  print("detail_index:" + str(detail_index))
  print("score_index_margin:" + str(score_index_margin))
  print("evaluation_index:" + str(evaluation_index))
  print("debag:" + str(debag))

  #20回描画
  write_count = 0
  for j in range(5):
    for k in range(4):
      cp_frame = copy.deepcopy(frame)
      write_frame = []
      write_result = []
      detail_list = []

      print("frame:" + str(frame))
      print("cp_frame:" + str(cp_frame))
      print("write_count:" + str(write_count))

      #描画用配列の作成
      for i in range(len(cp_frame) - 1):
        # write_frame.append([[cp_frame[i][0] - 100000, cp_frame[i][1] - 100000], [cp_frame[i + 1][0] - 80000, cp_frame[i + 1][1] - 80000]])
        write_frame.append([cp_frame[i], cp_frame[i + 1]])
      write_result = copy.deepcopy(cp_result_index[write_count])
      print(write_frame)

      #枠の描画
      for i in range(len(cp_frame) - 1):
        #直線を作成
        write_frame[i][0] = list(write_frame[i][0])
        write_frame[i][1] = list(write_frame[i][1])
        write_frame[i][0][0] = write_frame[i][0][0] - (j + 2) * 100000
        write_frame[i][1][0] = write_frame[i][1][0] - (j + 2) * 100000
        write_frame[i][0][1] = write_frame[i][0][1] + k * 80000
        write_frame[i][1][1] = write_frame[i][1][1] + k * 80000
        print("write_frame:" + str(write_frame[i]))
        msp.add_line(start=write_frame[i][0], end=write_frame[i][1])

      #枠の描画
      for i in range(len(write_result)):
        #直線を作成
        write_result[i][0] = list(write_result[i][0])
        write_result[i][1] = list(write_result[i][1])
        write_result[i][0][0] = write_result[i][0][0] - (j + 2) * 100000
        write_result[i][1][0] = write_result[i][1][0] - (j + 2) * 100000
        write_result[i][0][1] = write_result[i][0][1] + k * 80000
        write_result[i][1][1] = write_result[i][1][1] + k * 80000
        msp.add_line(start=write_result[i][0], end=write_result[i][1])

      #枠データの再度読み込み
      frame = cp_frame
      print("cp_frame:" + str(cp_frame))
      write_count += 1

  #有効宅地面積リスト
  yuko_list = []
  #有効宅地面積リストの作成
  for i in range(len(cp_detail_index)):
    yuko_list.append(cp_detail_index[i][-1])

  print("")
  print("#####操作終了#####")
  print("cp_result_index:" + str(cp_result_index))
  print("cp_detail_index:" + str(cp_detail_index))
  print("yuko_list:" + str(yuko_list))
  print("cp_score_index_margin:" + str(cp_score_index_margin))
  print("cp_evaluation_index:" + str(cp_evaluation_index))
  print("debag:" + str(debag))
  print("それぞれの戸数:" + str(kosu_count))

  #保存
  doc.saveas('line.dxf')

elif line_count == 5: #道作成しない場合の処理
  print("info:" + str(info))
  info = open('外部変形/information.txt','r',encoding='shift_jis')
  #カウントの初期化
  line_count = 0

  #infomationの中身を取得
  print("infomation")
  for line in info:
    #一行ごとに読み込み
    xy=line.split()
    print("\tLINEスプリット：" + str(xy))
    # print(len(xy))
    #間口の読み込み
    if line_count == 0:
      maguti = float(xy[0])
    #目標面積の読み込み
    elif line_count == 1:
      goal_area = float(xy[0])
    #接道辺の読み込み
    elif line_count == 2:
      for i in range(0, len(xy), 2):
        # print(i)
        road_edge_pt.append([float(xy[i]), float(xy[i + 1])])
    #道幅の読み込み
    elif line_count == 3:
      least_maguti = float(xy[0])
    #街区の読み込み
    elif line_count == 4:
      for i in range(0, len(xy), 2):
        frame.append([float(xy[i]), float(xy[i + 1])])
    #次行に移動
    line_count += 1

  for i in info:
    print("i" + str(i))
  print("道を作成しない場合の処理")
  print("road_edge_pt:" + str(road_edge_pt))
  print("road_edge_pt:" + str(road_edge_pt[0]))
  print("road_edge_pt:" + str(road_edge_pt[1]))
  print("road_edge_pt:" + str(road_edge_pt[0][0]))

  #ふたつずつ座標をまとめる：road_edge
  for i in range(int(len(road_edge_pt) / 2)):
    road_edge.append([road_edge_pt[i * 2], road_edge_pt[i * 2 + 1]])

  print("road_edge:" + str(road_edge))
  print("road_edge:" + str(road_edge[0]))
  # print("road_edge:" + str(road_edge[1]))
  print("road_edge:" + str(road_edge[0][0]))
  # print("road_edge:" + str(road_edge[1][0]))
  # print(str(len(road_edge)))

  #余計な道を削除
  for i in range(len(rm_list)):
    road_edge.remove(road_edge[rm_list[i]])


  print(" ")
  print("maguti:" + str(maguti))
  print("least_maguti:" + str(least_maguti))
  print("goal_area:" + str(goal_area))
  print("frame:" + str(frame))
  print("road_edge:" + str(road_edge))
  print(" ")



  #dxfのversion指定
  doc = ezdxf.new("R2010")

  #モデル空間に新しいエンティティを作成
  msp = doc.modelspace()
  draw_cnt = 0

  #上位描画用のリスト作成
  result_index = []
  score_index = []
  detail_index = []
  evaluation_index = []
  point_list = []

  #図面の複製
  cp_frame = copy.deepcopy(frame)



  #20回描画
  for i in range(100):
    cp_frame = copy.deepcopy(frame)
    draw_cnt += 1
    #区画割の実行
    print("現在の図面" + str(draw_cnt) + "個目")

    # 区画割の実行
    result, point_list, total_score, evaluation = un_load.unload_parcel_allocation(cp_frame, road_edge, maguti, least_maguti, goal_area)
    #リスト化
    result = list(result)
    #結果をそれぞれのindexに追加
    result_index.append(result)
    score_index.append(total_score)
    detail_index.append(point_list)
    evaluation_index.append(evaluation)


  # print(score_index)
  # print(sorted(score_index)[-1])
  #上位要素順に並び替え
  index_index = []
  #格納対象配列の高得点を上位から任意の個数抽出
  for i in range(1, 21, 1):
    target_num = sorted(score_index)[-i]
    index_index.append(target_num)

  print("index_index:" + str(index_index))
  # #同じ得点の得点と個数を抽出
  material = [k for k, v in collections.Counter(index_index).items() if v > 1]
  count = [v for k, v in collections.Counter(index_index).items() if v > 1]
  #同じ得点のものは小さい加点で差をつける
  for i in range(len(material)):
    for j in range(count[i]):
      print(score_index.index(material[i]))
      score_index[score_index.index(material[i])] = score_index[score_index.index(material[i])] + 0.0001 * j
  #点数を調整して再度任意の個数を抽出
  index_index = []
  cp_result_index = []
  cp_detail_index = []
  cp_score_index = []
  cp_evaluation_index = []

  #緊急
  # cp_result_index = copy.deepcopy(result_index)
  cp_result_index = []

  debag = []

  #任意の個数上位要素をresultとdetailに追加
  for i in range(1, 21, 1):
    #任意の上位個数を抽出
    target_num = sorted(score_index)[-i]
    index_index.append(target_num)
    cp_result_index.append(result_index[score_index.index(target_num)])
    cp_detail_index.append(detail_index[score_index.index(target_num)])
    cp_score_index.append(score_index[score_index.index(target_num)])
    cp_evaluation_index.append(evaluation_index[score_index.index(target_num)])
    debag.append(score_index.index(target_num))
    print(str(i) + "番目の結果:" + str(target_num))

  # print("まとめ")
  kosu_count = []
  for i in range(len(cp_evaluation_index)):
    kosu_count.append(len(cp_evaluation_index[i]))
  print("cp_result_index:" + str(cp_result_index))
  print("cp_detail_index:" + str(cp_detail_index))
  print("cp_score_index:" + str(cp_score_index))
  print("cp_evaluation_index:" + str(cp_evaluation_index))
  print("それぞれの戸数:" + str(kosu_count))
  print("index_index:" + str(index_index))
  print("result_index:" + str(result_index))
  print("detail_index:" + str(detail_index))
  print("score_index:" + str(score_index))
  print("evaluation_index:" + str(evaluation_index))
  print("debag:" + str(debag))

  #20回描画
  write_count = 0
  for j in range(5):
    for k in range(4):
      cp_frame = copy.deepcopy(frame)
      write_frame = []
      write_result = []
      detail_list = []

      print("frame:" + str(frame))
      print("cp_frame:" + str(cp_frame))
      print("write_count:" + str(write_count))

      #描画用配列の作成
      for i in range(len(cp_frame) - 1):
        write_frame.append([cp_frame[i], cp_frame[i + 1]])
      write_result = copy.deepcopy(cp_result_index[write_count])
      # write_result = copy.deepcopy(cp_result_index[0])
      print(write_frame)

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
      write_count += 1

  # #有効宅地面積リスト
  # yuko_list = []
  # #有効宅地面積リストの作成
  # for i in range(len(cp_detail_index)):
  #   yuko_list.append(cp_detail_index[i][-1])

  print("")
  # print("yuko_list:" + str(yuko_list))
  print("#####操作終了#####")
  print("cp_result_index:" + str(cp_result_index))
  print("cp_detail_index:" + str(cp_detail_index))
  print("cp_score_index:" + str(cp_score_index))
  print("cp_evaluation_index:" + str(cp_evaluation_index))
  print("debag:" + str(debag))
  print("それぞれの戸数:" + str(kosu_count))

  # #保存
  doc.saveas('line.dxf')