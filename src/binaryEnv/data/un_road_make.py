#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import json
import sys
import re

# コマンドライン引数(temp.txt)の受け取り
least_maguchi = 6800

# コマンドライン引数の二つ目から読み込み
for i in range(2, len(sys.argv)):
    # road_width(道幅)に代入
    if re.match(r"/road_width", sys.argv[i]):
        least_maguchi = float(sys.argv[i].split(":")[1]) * 1000

# 変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
frame = []
xy = []

# tempの中身を取得
tmp_file = sys.argv[1]
f = open(tmp_file, mode="r")
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


# 街区情報をjsonファイルに書き込む
def input_to_json(least_maguchi, frame):
    # TODO: のちのちInputの構造体を作るとよりわかりやすい
    input_data = {"least_maguchi": least_maguchi, "frame": frame}

    input_json_data = json.dumps(input_data, indent=4)

    with open("data/frame_input_data.json", "w") as f:
        f.write(input_json_data)


input_to_json(least_maguchi, frame)
