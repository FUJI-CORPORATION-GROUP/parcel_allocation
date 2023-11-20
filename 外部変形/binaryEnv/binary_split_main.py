from point import Point
from frame import Frame
import binary_search
import draw_dxf

def main():
  #####メインプログラム#####
  #読み込み用のファイルを展開
  print("================================")
  print("メインプログラム split.py")
  print("================================")
  info = open('data/information.txt','r',encoding='shift_jis')
  print("hd")

  # 変数宣言
  line_count = 0
  road_edge_pt = []
  frame = []
  load_edge = []
  rm_list = []


  #infomationの行数の取得
  for i in info:
    line_count += 1
    print(str(line_count), "番目：",str(i), end="")

  print("")
  info = open('data/information.txt','r',encoding='shift_jis')
  #カウントの初期化
  line_count = 0

  #infomationの中身を取得
  for line in info:
    #一行ごとに読み込み
    info_line=line.split()
    print("LINEスプリット：" + str(info_line))
    # print(len(xy))
    #間口の読み込み
    if line_count == 0:
      maguti = float(info_line[0])
    #目標面積の読み込み
    elif line_count == 1:
      target_area = float(info_line[0])
    #接道辺の読み込み
    elif line_count == 2:
      for i in range(0, len(info_line), 2):
        # print(i)
        road_edge_pt.append([float(info_line[i]), float(info_line[i + 1])])
    #道幅の読み込み
    elif line_count == 3:
      least_maguti = float(info_line[0])
    #街区の読み込み
    elif line_count == 4:
      for i in range(0, len(info_line), 2):
        frame.append([float(info_line[i]), float(info_line[i + 1])])
    #次行に移動
    line_count += 1

  #ふたつずつ座標をまとめる：road_edge
  for i in range(int(len(road_edge_pt) / 2)):
    load_edge.append([road_edge_pt[i * 2], road_edge_pt[i * 2 + 1]])

  #余計な道を削除
  for i in range(len(rm_list)):
    load_edge.remove(load_edge[rm_list[i]])


  print(" ")
  print("goal_area:" + str(target_area))
  print("frame:" + str(frame))
  print("road_edge:" + str(load_edge))
  print(" ")

  # classの変更
  for i in range(len(frame)):
    frame[i] = Point(frame[i][0], frame[i][1])
  frame = Frame(frame)
  print("Before"+frame.get_points_str())
  frame.move_positive()
  print("After"+frame.get_points_str())
  
  load_frame = load_edge
  for i in range(len(load_edge)):
    for k in range(len(load_edge[i])):
      load_frame[i][k] = Point(load_edge[i][k][0], load_edge[i][k][1])

  # デバッグ用
  # target_area = 28000

  # 二分探索の実行
  # 道に接する辺の数だけ実行
  # 計算毎にseach_frameを変更しながら計算する
  # for i in range(len(load_edge)):
  #   binary_search.debug_main(load_edge[i], frame, target_area)

  # 探索領域
  search_frame = frame
  move_line = Point(0,50)

  draw_dxf.clear_dxf()
  draw_dxf.draw_line_by_point(search_frame.points)
  binary_parcel_list = []
  count = 0
  # target_area = 1000

  print(f"search_frame : {search_frame.get_points_str()}")

  # 探索領域が目標面積取れなくなるまで区画割
  while(True):
    print(f"\n{count} 回目")
    parcel_frame, remain_frame = binary_search.get_side_parcel(search_frame,load_frame[0],target_area,move_line)
    
    count += 1
    binary_parcel_list.append(parcel_frame)
    
    if(target_area > remain_frame.area):
      print(f"探索終了 残り面積{remain_frame.area}")
      break
    
    if(count > 30):
      # 念のため
      break
    
    search_frame = remain_frame

  draw_dxf.draw_line_by_frame_list_color(binary_parcel_list, 1)
  
  
main()