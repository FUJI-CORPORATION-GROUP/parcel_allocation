import codecs
import sys
import re
import json

print("----parameter_in.py----")
# 道路情報を入力している
# TODO: parameter_in.pyとun_road_make.pyの役割がファイル名でわかりにくいため，統合 or リネームする

#コマンドライン引数（最小目標面積，最大目標面積）
road_width=4000
target_min_area = 100000000
target_max_area = 120000000

# コマンドライン引数の二つ目から読み込み
for i in range(2,len(sys.argv)):
  #aから始まる情報はroad_width(道幅)に代入
  if re.match(r"/a",sys.argv[i]):
    road_width=float(sys.argv[i][2:len(sys.argv[i])]) * 1000
  #bから始まる情報はmaguti(間口)に代入
  elif re.match(r"/b",sys.argv[i]):
    target_min_area=float(sys.argv[i][2:len(sys.argv[i])]) * 1000000
  #cから始まる情報はgoal_area(目標面積)に代入
  elif re.match(r"/c",sys.argv[i]):
    target_max_area=float(sys.argv[i][2:len(sys.argv[i])]) * 1000000

print(sys.argv)
print(" ")
print("target_min_area:" + str(target_min_area))
print("target_max_area:" + str(target_max_area))
print(" ")


# 道路の座標を取得
road_edge_point_list = []
xy = []

#tempの中身を取得
tmp_file = sys.argv[1]
f=open(tmp_file,mode="r")
for line in f:
  if re.match(r"hp",line):
    #一行ごとに読み込み
    xy=line.split()
    road_edge_point_list.append([float(xy[1]), float(xy[2])])
for i in range(len(road_edge_point_list)):
  for j in range(1, len(road_edge_point_list[i])):
    print(" " + str(road_edge_point_list[i][j - 1]) + " " + str(road_edge_point_list[i][j]))
f.close()

# 道路情報をjsonファイルに書き込む
def input_to_json(road_width, target_min_area, target_max_area, road_edge_point_list):
  # TODO: のちのちInputの構造体を作るとよりわかりやすい
  input_data = {'road_width': road_width, 'target_min_area': target_min_area, 'target_max_area': target_max_area, 'road_edge_point_list': road_edge_point_list}
  
  input_json_data = json.dumps(input_data, indent=4)
  
  with open('data/road_input_data.json', 'w') as f:
    f.write(input_json_data)

input_to_json(road_width, target_min_area, target_max_area, road_edge_point_list)