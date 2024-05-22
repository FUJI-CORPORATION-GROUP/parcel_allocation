#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import sys
import re


# 書き込み用のファイルを展開
# info = codecs.open('外部変形/information.txt','w',"shift-jis")
info = codecs.open("外部変形/information.txt", "a", "shift-jis")

# コマンドライン引数(temp.txt)の受け取り
least_maguchi = 6800

# コマンドライン引数の二つ目から読み込み
for i in range(2, len(sys.argv)):
    # aから始まる情報はroad_width(道幅)に代入
    if re.match(r"/a", sys.argv[i]):
        least_maguchi = float(sys.argv[i][2 : len(sys.argv[i])]) * 1000
    #
#

# 書き込み
info.write(str(least_maguchi) + "\n")

# コマンドライン引数の受け取り
file = sys.argv[1]

# 読み取り専用で代入
f = open(file, mode="r")
# print("デバッグ：" + str(f))

# 変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
make_road_edge = []
frame = []
xy = []
datas = []
hp_count = 0

# tempの中身を取得
for line in f:
    # hpの場合は座標取得
    if re.match(r"hp", line):
        # 一行ごとに読み込み
        xy = line.split()
        # 後半は図形の枠
        frame.append([float(xy[1]), float(xy[2])])

for i in range(len(frame)):
    for j in range(1, len(frame[i])):
        print(" " + str(frame[i][j - 1]) + " " + str(frame[i][j]))
f.close()

# 街区
for i in range(len(frame)):
    if i == len(frame) - 1:
        info.write(str(frame[i][0]) + " " + str(frame[i][1]) + "\n")
    else:
        info.write(str(frame[i][0]) + " " + str(frame[i][1]) + " ")
