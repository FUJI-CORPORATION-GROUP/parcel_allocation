#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import json
import sys
import re


#書き込み用のファイルを展開
# info = codecs.open('外部変形/information.txt','w',"shift-jis")
info = codecs.open('data/information.txt','a',"shift-jis")

#コマンドライン引数(temp.txt)の受け取り
least_maguti=6800

#コマンドライン引数の二つ目から読み込み
for i in range(2,len(sys.argv)):
	#aから始まる情報はroad_width(道幅)に代入
	if re.match(r"/a",sys.argv[i]):
		least_maguti=float(sys.argv[i][2:len(sys.argv[i])]) * 1000
	#
#

#書き込み
info.write(str(least_maguti) + "\n")

#コマンドライン引数の受け取り
file = sys.argv[1]

#読み取り専用で代入
f=open(file,mode="r")
# print("デバッグ：" + str(f))

#変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
frame = []
xy = []

#tempの中身を取得
for line in f:
  #hpの場合は座標取得
  if re.match(r"hp",line):
    #一行ごとに読み込み
    xy=line.split()
    #後半は図形の枠
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


# 街区情報をjsonファイルに書き込む
def input_to_json(least_maguti,frame):
  # TODO: のちのちInputの構造体を作るとよりわかりやすい
  input_data = {'least_maguti': least_maguti, 'frame': frame}
  
  input_json_data = json.dumps(input_data, indent=4)
  
  with open('data/frame_input_data.json', 'w') as f:
    f.write(input_json_data)

input_to_json(least_maguti,frame)