import codecs
import sys
import re
import json

print("----parameter_in.py----")
# 道路情報を入力している？

#書き込み用のファイルを展開
info = codecs.open('data/information.txt','w',"shift-jis")

#コマンドライン引数（最小目標面積，最大目標面積）
road_width=4000
goal_min_area = 100000000
goal_max_area = 120000000
# maguti = 7600
# goal_area = 100000000

# コマンドライン引数の二つ目から読み込み
for i in range(2,len(sys.argv)):
  #aから始まる情報はroad_width(道幅)に代入
  if re.match(r"/a",sys.argv[i]):
    road_width=float(sys.argv[i][2:len(sys.argv[i])]) * 1000
  #bから始まる情報はmaguti(間口)に代入
  elif re.match(r"/b",sys.argv[i]):
    goal_min_area=float(sys.argv[i][2:len(sys.argv[i])]) * 1000000
  #cから始まる情報はgoal_area(目標面積)に代入
  elif re.match(r"/c",sys.argv[i]):
    goal_max_area=float(sys.argv[i][2:len(sys.argv[i])]) * 1000000

print(sys.argv)
print(" ")
print("goal_min_area:" + str(goal_min_area))
print("goal_max_area:" + str(goal_max_area))
print(" ")

info.write(str(goal_min_area) + "\n")
info.write(str(goal_max_area) + "\n")

#コマンドライン引数(temp.txt)の受け取り
file = sys.argv[1]

#読み取り専用で代入
f=open(file,mode="r")

#変数を宣言（接道辺，道作成辺，街区，座標，選択された連続線，枠上判定）
make_road_edge = []
road_frame = []
xy = []

#tempの中身を取得
for line in f:
  if re.match(r"hp",line):
    #一行ごとに読み込み
    xy=line.split()
    road_frame.append([float(xy[1]), float(xy[2])])
for i in range(len(road_frame)):
  for j in range(1, len(road_frame[i])):
    print(" " + str(road_frame[i][j - 1]) + " " + str(road_frame[i][j]))
f.close()

# 道路と設置している辺の座標の取得
for i in range(len(road_frame)):
  if i == len(road_frame) - 1:
    info.write(str(road_frame[i][0]) + " " + str(road_frame[i][1]) + "\n")
  else:
    info.write(str(road_frame[i][0]) + " " + str(road_frame[i][1]) + " ")

# 道路情報をjsonファイルに書き込む
def input_to_json(road_width, goal_min_area, goal_max_area, road_frame):
  # TODO: のちのちInputの構造体を作るとよりわかりやすい
  input_data = {'road_width': road_width, 'goal_min_area': goal_min_area, 'goal_max_area': goal_max_area, 'road_frame': road_frame}
  
  input_json_data = json.dumps(input_data, indent=4)
  
  with open('data/road_input_data.json', 'w') as f:
    f.write(input_json_data)

input_to_json(road_width, goal_min_area, goal_max_area, road_frame)