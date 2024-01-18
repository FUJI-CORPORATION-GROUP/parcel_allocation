import math
import random
from point import Point
from frame import Frame
import binary_search
import draw_dxf
from plan import Plan


def get_plans(target_max_area, target_min_area, binary_parcel_list, search_frame, count, road_frame, move_line):
  # frameListを作成して，Planを返す
  # 探索領域が目標面積取れなくなるまで区画割
  while(True):
    if(search_frame.area > target_max_area):
      target_area = random.randint(target_min_area,target_max_area)
      print(f"\n{count} 回目 探索開始 ランダム目標面積：{target_area}")
    else:
      target_area = target_max_area
      print(f"\n{count} 回目 探索開始 最小目標面積：{target_area}")
  
    parcel_frame, remain_frame = binary_search.get_side_parcel(search_frame,road_frame[0],target_area,move_line,count)
    
    
    count += 1
    binary_parcel_list.append(parcel_frame)
    
    if(target_min_area > remain_frame.area):
      print(f"探索終了 残り面積{math.floor(remain_frame.area/1000000)}㎡")
      break
    
    if(count > 30):
      # 念のため
      break
    
    search_frame = remain_frame
  
  # ここでPlan生成
  plan = Plan(binary_parcel_list)
  return plan

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
  road_edge = []
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
    # 最小目標面積の読み込み
    if line_count == 0:
      target_min_area = float(info_line[0])
    # 最大目標面積の読み込み
    elif line_count == 1:
      target_max_area = float(info_line[0])
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
    road_edge.append([road_edge_pt[i * 2], road_edge_pt[i * 2 + 1]])

  #余計な道を削除
  for i in range(len(rm_list)):
    road_edge.remove(road_edge[rm_list[i]])


  print(" ")
  print("target_min_area" + str(target_min_area))
  print("target_max_area" + str(target_max_area))
  print(" ")

  # classの変更
  for i in range(len(frame)):
    frame[i] = Point(frame[i][0], frame[i][1])
  frame = Frame(frame)
  frame.move_zero()
  road_frame = road_edge
  for i in range(len(road_edge)):
    for k in range(len(road_edge[i])):
      road_frame[i][k] = Point(road_edge[i][k][0], road_edge[i][k][1])
  # デバッグ用
  # target_area = 28000

  # 二分探索の実行
  # 道に接する辺の数だけ実行
  # 計算毎にseach_frameを変更しながら計算する
  # for i in range(len(road_edge)):
  #   binary_search.debug_main(road_edge[i], frame, target_area)

  # 探索領域
  search_frame = frame
  
  move_line = Point(0,50)

  # 参照しているDXFファイルをリセット
  draw_dxf.clear_dxf()
  # draw_dxf.draw_line_by_point(search_frame.points)
  binary_parcel_list = []
  count = 0
  # target_area = 1000
  # rate = 1000000
  # target_min_area = 90000000 * rate
  # target_max_area = 110000000 * rate

  if(len(road_frame) > 1):
    print("道路が2本以上あります")
    exit()
  elif(len(road_frame) == 0):
    print("道路がありません")
    exit()

  # 道路方向ベクトル取得
  # TODO:0番目しかないと仮定．今後の入力形態に入力形態によって変更
  road_vec = road_frame[0][1].sub(road_frame[0][0])
  # 道路方向ベクトルを回転させてMoveLineを取得
  move_line = Point(-1 * road_vec.y, road_vec.x)

  # TODO:30回実行
  plan_list = []
  for executions in range(30):
    # frameListを作成して，Planを返す
    plan = get_plans(target_max_area, target_min_area, binary_parcel_list, search_frame, count, road_frame, move_line)
    plan_list.append(plan)

  print(plan_list)
  # 描写開始
  
  for i in range(len(plan_list)):
    point_shift = Point((i % 5) * 100000, (i // 5) * 80000)
    plan_list[i] = plan_list[i].move_plan(point_shift)
    # draw_dxf.draw_dxf_by_plan(plan_list[i].move_plan(point_shift), 1)
    # draw_dxf.draw_dxf_by_plan(plan_list[i], 1)
  
  draw_dxf.draw_dxf_by_plan_list(plan_list, 1)

main()