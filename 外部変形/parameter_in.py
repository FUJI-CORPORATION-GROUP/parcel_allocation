import codecs
import sys
import re

print("---parameter_in.py---")

# 書き込み用のファイルを展開
info = codecs.open('外部変形/information.txt', 'w', "shift-jis")

# コマンドライン引数（道幅，間口，目標面積）
road_width = 4000
maguchi = 7600
goal_area = 100000000

# コマンドライン引数の二つ目から読み込み
for i in range(2, len(sys.argv)):
    # aから始まる情報はroad_width(道幅)に代入
    if re.match(r"/a", sys.argv[i]):
        road_width = float(sys.argv[i][2:len(sys.argv[i])]) * 1000
  # bから始まる情報はmaguchi(間口)に代入
    elif re.match(r"/b", sys.argv[i]):
        maguchi = float(sys.argv[i][2:len(sys.argv[i])]) * 1000
  # cから始まる情報はgoal_area(目標面積)に代入
    elif re.match(r"/c", sys.argv[i]):
        goal_area = float(sys.argv[i][2:len(sys.argv[i])]) * 1000000
    #
#

print(sys.argv)
print(" ")
print("maguchi:" + str(maguchi))
print("goal_area:" + str(goal_area))
print(" ")

info.write(str(maguchi) + "\n")
info.write(str(goal_area) + "\n")

# コマンドライン引数(temp.txt)の受け取り
file = sys.argv[1]

# 読み取り専用で代入
f = open(file, mode="r")

# 変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
make_road_edge = []
frame = []
xy = []

# tempの中身を取得
for line in f:
    if re.match(r"hp", line):
        # 一行ごとに読み込み
        xy = line.split()
        frame.append([float(xy[1]), float(xy[2])])
for i in range(len(frame)):
    for j in range(1, len(frame[i])):
        print(" " + str(frame[i][j - 1]) + " " + str(frame[i][j]))
f.close()

# 道路と設置している辺の座標の取得
for i in range(len(frame)):
    if i == len(frame) - 1:
        info.write(str(frame[i][0]) + " " + str(frame[i][1]) + "\n")
    else:
        info.write(str(frame[i][0]) + " " + str(frame[i][1]) + " ")
