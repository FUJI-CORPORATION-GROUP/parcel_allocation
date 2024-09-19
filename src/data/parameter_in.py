import sys
import re
import json

print("----parameter_in.py----")
# 道路情報を入力している
# TODO: parameter_in.pyとun_road_make.pyの役割がファイル名でわかりにくいため，統合 or リネームする

# コマンドライン引数（最小目標面積，最大目標面積）
road_width = 4000
target_min_area = 100000000
target_max_area = 120000000
min_maguchi = 7000
max_maguchi = 8000

# コマンドライン引数の二つ目から読み込み
for i in range(2, len(sys.argv)):
    data = sys.argv[i]
    # road_width(道幅)に代入
    if re.match(r"/road_width", data):
        road_width = int(data.split(":")[1]) * 1000
    # 最小間口 m -> mm
    elif re.match(r"/min_maguchi", data):
        min_maguchi = int(data.split(":")[1]) * 1000
    # 最大間口 m -> mm
    elif re.match(r"/max_maguchi", data):
        max_maguchi = int(data.split(":")[1]) * 1000
    # 最小目標面積 m^2 -> mm^2
    elif re.match(r"/target_min_area", data):
        target_min_area = int(data.split(":")[1]) * 1000000
    # 最大目標面積 m^2 -> mm^2
    elif re.match(r"/target_max_area", data):
        target_max_area = int(data.split(":")[1]) * 1000000

print(sys.argv)
print(" ")
print("min_maguchi:" + str(min_maguchi))
print("max_maguchi:" + str(max_maguchi))
print("target_min_area:" + str(target_min_area))
print("target_max_area:" + str(target_max_area))
print(" ")


# 道路の座標を取得
road_edge_point_list = []
xy = []

# tempの中身を取得
tmp_file = sys.argv[1]
f = open(tmp_file, mode="r")
for line in f:
    if re.match(r"hp", line):
        # 一行ごとに読み込み
        xy = line.split()
        road_edge_point_list.append([float(xy[1]), float(xy[2])])
for i in range(len(road_edge_point_list)):
    for j in range(1, len(road_edge_point_list[i])):
        print(" " + str(road_edge_point_list[i][j - 1]) + " " + str(road_edge_point_list[i][j]))
f.close()


# 道路情報をjsonファイルに書き込む
def input_to_json(road_width, target_min_area, target_max_area, road_edge_point_list):
    # TODO: のちのちInputの構造体を作るとよりわかりやすい
    input_data = {
        "road_width": road_width,
        "min_maguchi": min_maguchi,
        "max_maguchi": max_maguchi,
        "target_min_area": target_min_area,
        "target_max_area": target_max_area,
        "road_edge_point_list": road_edge_point_list,
    }

    input_json_data = json.dumps(input_data, indent=4)

    with open("data/road_input_data.json", "w") as f:
        f.write(input_json_data)


input_to_json(road_width, target_min_area, target_max_area, road_edge_point_list)
