import numpy as np
from components.point import Point
import binary_calc as Calc

class Frame:
    """区画を扱うクラス

    functions:
        distance (list, list): _距離同士の距離を求める
        point_to_line_distance (list, list, list): _点と直線の距離公式

    """

    def __init__(self, points):
      self.points = points
      self.area = Calc.calc_area(self)

    # 直線ABで区切られる区画を返す
    def get_tmp_frame(self, move_line_point, binary_point, min_point,max_point, count,calc_count):
      """探索領域を直線ABで区切り,区画と残りの探索領域を取得する

      Args:
          move_line_point (Point): _奥行ベクトル_
          binary_point (Point): _2分探索中の点_
          min_point (Point): _探索範囲の最小値_

      Returns:
          parcel_frame (Frame): _区画_
          remain_frame (Frame): _残りの探索領域_
      """
      point_list_A, point_list_B = [], []
      move_line_point = move_line_point.add(binary_point)

      get_frame_flag = True
      for i in range(len(self.points)):
        point_s = self.points[i]
        point_e = self.points[i + 1] if(i+1<len(self.points)) else self.points[0]
        line_cross = Calc.line_cross_point(point_s, point_e, move_line_point, binary_point, count,calc_count)
        
        if(get_frame_flag):
          point_list_A.append(point_s)
        else:
          point_list_B.append(point_s)
        
        if (line_cross != None):
          point_list_A.append(line_cross)
          point_list_B.append(line_cross)
          get_frame_flag = not get_frame_flag
      
      tmp_frame_A = Frame(point_list_A)
      tmp_frame_B = Frame(point_list_B)
      
      if(tmp_frame_A.get_point_counts() < 0 and tmp_frame_B.get_point_counts() < 0):
        # ERR
        print("ERR: 2分探索失敗")
        raise ValueError("2分探索失敗")
        exit()
      elif(tmp_frame_A.get_point_counts() < 1):
        parcel_frame = tmp_frame_A
        remain_frame = tmp_frame_B
      elif(tmp_frame_B.get_point_counts() < 1):
        parcel_frame = tmp_frame_B
        remain_frame = tmp_frame_A
      else:
        tmp_barycenter_A = Calc.Get_vertical_intersection(min_point,max_point,tmp_frame_A.get_barycenter())
        tmp_barycenter_B = Calc.Get_vertical_intersection(min_point,max_point,tmp_frame_B.get_barycenter())
        tmp_distance_A_min = tmp_barycenter_A.distance(min_point)
        tmp_distance_B_min = tmp_barycenter_B.distance(min_point)
        parcel_frame = tmp_frame_A if(tmp_distance_A_min < tmp_distance_B_min) else tmp_frame_B
        remain_frame = tmp_frame_B if(tmp_distance_A_min < tmp_distance_B_min) else tmp_frame_A

      return parcel_frame, remain_frame
    
    # frameと奥行ベクトルから，探索領域を求める
    def Get_search_frame(self ,target_frame, search_depth_distance, road_start_point, road_end_point):
      # 道路方向ベクトル取得
      # TODO:0番目しかないと仮定．今後の入力形態に入力形態によって変更
      road_vec = road_end_point.sub(road_start_point)

      # 奥行ベクトル
      search_depth_vec = Point.unit(Point(-1 * road_vec.y, road_vec.x)).mul(search_depth_distance)
      
      # 切り出すための直線の始点と終点
      A = road_start_point.add(search_depth_vec)
      B = road_end_point.add(search_depth_vec)
      
      get_search_frame_flag = True
      search_point_list = []

      for i in range(len(target_frame.points)):
        # 直線ABとtarget_frameの辺の交点を求める
        the_point = target_frame.points[i]
        the_next_point = target_frame.points[(i+1) % len(target_frame.points)] 
        cross_point = Calc.line_cross_point(
            the_point, the_next_point, A, B, 0, 0)
        if get_search_frame_flag:
          search_point_list.append(the_point)

        if cross_point is not None:
          search_point_list.append(cross_point)
          get_search_frame_flag = False

        search_frame = Frame(search_point_list)
      return search_frame
    
    def move_frame(self, point):
      """区画自体を移動量ベクトル方向に動かす

      Args:
          point (Point): 移動する方向ベクトル

      Returns:
          Frame: 移動した区画
      """
      for i in range(len(self.points)):
        self.points[i] = self.points[i].add(point)

    def debug_move_frame(self, point):
      """デバッグ用：移動量ベクトル移動した区画を取得する（区画自体は移動しない）

      Args:
          point (Point): 移動する方向ベクトル

      Returns:
          Frame: 移動した場合の新しい区画
      """
      debug_points = []
      for i in range(len(self.points)):
        debug_points.append(self.points[i].add(point))
      return Frame(debug_points)

    def get_points_str(self):
      """区画の座標を文字列で取得する

      Returns:
          str: 座標文字列
      """
      str = ""
      for i in range(len(self.points)):
        str = f"{str} {self.points[i].get_str()}"
      return str
    
    def get_point_counts(self):
      """区画の頂点数を取得する

      Returns:
          int: _区画の頂点数_
      """
      return len(self.points)
    
    def get_list_xy(self):
      """区画の座標をリストで取得する

      Returns:
          list: x座標リスト
          list: y座標リスト
      """
      list_x , list_y = [], []
      for i in range(len(self.points)):
        list_x.append(self.points[i].x)
        list_y.append(self.points[i].y)
      return list_x,list_y
    
    def move_positive(self):
      """区画を第一象限に移動する
      """
      list_x, list_y = self.get_list_xy()
      min_x = abs(min(list_x)) if (min(list_x) < 0) else 0
      min_y = abs(min(list_y)) if (min(list_y) < 0) else 0
      
      move_positive_point = Point(min_x, min_y) 
      self = self.move_frame(move_positive_point)
    
    def move_zero(self):
      """区画を原点に移動する
      """
      list_x, list_y = self.get_list_xy()
      min_x,min_y = min(list_x),min(list_y)
      move_zero_point = Point(-1 * min_x, -1 * min_y) 
      self = self.move_frame(move_zero_point)

    def move_frame_and_road(frame, road_frame):
      """区画と道路区画を原点に移動する

      Args:
          frame (Frame): 区画のFrame
          road_frame (list<Frame[]): 道路Frameのリスト

      Returns:
          _type_: 区画のFrame, 道路Frameのリスト
      """
      
      # 区画を原点に移動
      list_x, list_y = frame.get_list_xy()
      min_x,min_y = min(list_x),min(list_y)
      move_zero_point = Point(-1 * min_x, -1 * min_y) 
      frame.move_frame(move_zero_point)

      # 道路区画も同一距離移動
      moved_road_frame_list = []
      for i in range(len(road_frame)):
        road_frame[i].move_frame(move_zero_point)
        moved_road_frame_list.append(road_frame[i])
        
      return frame, moved_road_frame_list
    
    def get_barycenter(self):
      """区画の重心を取得する

      Raises:
          ValueError: pointsがない場合

      Returns:
          Point: 区画の重心
      """
      num_points = len(self.points)

      if num_points == 0:
          raise ValueError("pointsないよ")

      sum_x = sum(point.x for point in self.points)
      sum_y = sum(point.y for point in self.points)

      barycenter = Point(sum_x / num_points, sum_y / num_points)

      return barycenter