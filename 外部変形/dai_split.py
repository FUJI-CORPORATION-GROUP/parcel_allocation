# -*-coding: Shift_JIS -*-
import importlib
import math
import sys
import re
import os
import Calc

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
    if (x0 <= x <= x1 and y0 <= y <= y1) or (x0 >= x >= x1 and y0 >= y >= y1):
      return x, y
    else:
      return None

#間口を基準に最大戸数の宅地を形成
def maguchi(data, coor):
  lines_h = []
  lines_l = []
  fin_line = []

  #縁の長さを計算
  edge = abs(coor[0][0] - coor[1][0])
  #間口は7.1mで計算
  num = (int)(edge / 7100)
  #宅地割に使う平行線の長さの計算
  depth = abs(coor[1][1] - coor[2][1]) / 1000

  print("edge:" + str(edge) + " num:" + str(num))

#家を作成する戸数を決定
  flont_x = edge / num
  flont_y = abs(coor[0][1] - coor[1][1]) / num

  #複線を間口の感覚で作成
  for i in range(1,num):
    lines_l.append([coor[2][0] + flont_x * i - 1000000, coor[2][1] + flont_y * i - 1000000])
    lines_h.append([coor[1][0] + flont_x * i - 1000000, coor[1][1] + flont_y * i - 1000000])

    for j in range(len(data)):
      if j + 1 == len(data):
        #算出した点が枠上に存在する場合リストに追加
        fin_coor = line_cross_point(data[j], data[1], lines_h[i - 1], lines_l[i - 1])
        if fin_coor is not None:
          fin_line.append(fin_coor)
      else:
        fin_coor = line_cross_point(data[j], data[j + 1], lines_h[i - 1], lines_l[i - 1])
        if fin_coor is not None:
          fin_line.append(fin_coor)

  print("fin_line" + str(fin_line))
  print(len(fin_line))

  #作成した複線を描画
  for i in range(0, len(fin_line), 2):
    print(i)
    print(" %.11f %.11f %.11f %.11f\n" %(fin_line[i][0],fin_line[i][1],fin_line[i + 1][0], fin_line[i + 1][1]))


  #区画二つ分の敷地があれば
  if flont_x * depth > 200:
    print("区画二つ分の面積あり")
    mid_line = []
    mid_line.append([(coor[1][0] + coor[2][0]) / 2 - 1000000, (coor[1][1] + coor[2][1]) / 2 - 1000000])
    mid_line.append([mid_line[0][0] + flont_x * num, mid_line[0][1] + flont_y * num])
    print(" %.11f %.11f %.11f %.11f\n" %(mid_line[0][0],mid_line[0][1],mid_line[1][0], mid_line[1][1]))


#文字列の長さを返す
def size(moji):
	return len(moji.encode("SHIFT-JIS"))
#

#コマンドライン引数(temp.txt)の受け取り
file = sys.argv[1]

#読み取り専用で代入
f=open(file,mode="r")
print("hd")
datas = []
xy = []
hp = []
hp_coor = []
hp_coor_plus = []
start = 0
hp_cnt = 0

#tempの中身を取得
for line in f:

	#hq(実行なし)は無視
  if re.match(r"hq",line):
    pass
  #hpの場合は座標取得
  elif re.match(r"hp",line):
    xy=line.split()
    for i in range(len(xy)):
      if i==0:
        #hp.append(xy[i])
        hp_cnt += 1
      else:
        hp.append(xy[i])
  #空白の場合も座標取得
  elif re.match(r" ",line):
    xy=line.split()
    datas.append([xy[0],xy[1]])
    datas.append([xy[2],xy[3]])
    print(line,end="")

f.close()

#重複削除
datas = list(map(list,set(map(tuple,datas))))

#リストの中身を全てfloat型に
hp = [float(item) for item in hp]
cnt = (len(hp) / 2 + 2)

print(hp)

#hpを座標リストに変換
for i in range(0, len(hp), 2):
  hp_coor_plus.append([hp[i] + 1000000, hp[i + 1] + 1000000])
  hp_coor.append([hp[i], hp[i + 1]])

print(hp_coor_plus)

#面積/戸数の計算
area = Calc.main_calc(hp_coor_plus)
units = area / 100000000

print("面積は" + str(area) + "戸数は" + str(int(units)))

if len(datas) > 3:
  #個別座標の入力
  x=float(datas[0][0])
  y=float(datas[0][1])

  m1 = (float(datas[0][0]) + float(datas[1][0])) / 2
  m2 = (float(datas[0][1]) + float(datas[1][1])) / 2
  m3 = (float(datas[2][0]) + float(datas[3][0])) / 2
  m4 = (float(datas[2][1]) + float(datas[3][1])) / 2

  #中点の描画
  print("")
  print(" " + str(int(m1)) + " " + str(int(m2)) + " " + str(int(m3)) + " " + str(int(m4)))

maguchi(hp_coor, hp_coor_plus)