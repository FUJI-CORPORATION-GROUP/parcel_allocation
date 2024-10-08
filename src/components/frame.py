from components.point import Point
import binary_calc as Calc
import draw_dxf as Draw
from collections import deque

class Frame:
    """区画を扱うクラス

    functions:
        distance (list, list): _距離同士の距離を求める
        point_to_line_distance (list, list, list): _点と直線の距離公式

    """

    def __new__(self, points):
        if len(points) == 0:
            return None
        if Point.is_same_points(points[0], points[-1]):
            del points[-1]
        return super(Frame, self).__new__(self)

    def __init__(self, points):
        self.points = points
        self.area = Calc.calc_area(self)

    # 直線ABで区切られる区画を返す
    def get_tmp_frame(self, move_line_point, binary_point, min_point, max_point, count, calc_count):
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
            point_e = self.points[i + 1] if (i + 1 < len(self.points)) else self.points[0]
            line_cross = Calc.line_cross_point(point_s, point_e, move_line_point, binary_point, count, calc_count)

            if get_frame_flag:
                point_list_A.append(point_s)
            else:
                point_list_B.append(point_s)

            if line_cross is not None:
                point_list_A.append(line_cross)
                point_list_B.append(line_cross)
                get_frame_flag = not get_frame_flag

        tmp_frame_A = Frame(point_list_A)
        tmp_frame_B = Frame(point_list_B)

        if tmp_frame_A is None and tmp_frame_B is None:
            # ERR
            print("ERR: 2分探索失敗")
            raise ValueError("2分探索失敗")
            exit()
        elif tmp_frame_A is None or tmp_frame_B is None:
            parcel_frame = tmp_frame_A if tmp_frame_A is not None else tmp_frame_B
            remain_frame = tmp_frame_A if tmp_frame_A is not None else tmp_frame_B
        else:
            tmp_barycenter_A = Calc.Get_vertical_intersection(min_point, max_point, tmp_frame_A.get_barycenter())
            tmp_barycenter_B = Calc.Get_vertical_intersection(min_point, max_point, tmp_frame_B.get_barycenter())
            tmp_distance_A_min = tmp_barycenter_A.distance(min_point)
            tmp_distance_B_min = tmp_barycenter_B.distance(min_point)
            parcel_frame = tmp_frame_A if (tmp_distance_A_min < tmp_distance_B_min) else tmp_frame_B
            remain_frame = tmp_frame_B if (tmp_distance_A_min < tmp_distance_B_min) else tmp_frame_A

        return parcel_frame, remain_frame

    # TODO: utilsとかに書き出し
    # frameと奥行ベクトルから，探索領域を求める
    def Get_search_frame(self, target_frame, search_depth_distance, road_start_point, road_end_point):
        """
        Args:
            target_frame (Frame): _対象区画_
            search_depth_distance (float): _探索する奥行きベクトル_
            road_start_point (Point): _道路の始点_
            road_end_point (Point): _道路の終点_
        
        Returns:
            search_frame (Frame): _探索領域_
            remain_search_frame (Frame): _残りの探索領域_
        """

        # 道路方向ベクトル取得
        # TODO:0番目しかないと仮定．今後の入力形態に入力形態によって変更
        road_vec = road_end_point.sub(road_start_point)

        # Draw.debug_png_by_frame_list([target_frame], "target_frame from Get_search_frame")

        # 奥行ベクトル
        search_depth_vec = Point.unit(Point(-1 * road_vec.y, road_vec.x)).mul(search_depth_distance)

        # 切り出すための直線の始点と終点
        cat_line_start_point = road_start_point.add(search_depth_vec)
        cat_line_end_point = road_end_point.add(search_depth_vec)

        # target_frameがroad_start_pointの値から始まるように回転させる
        min_distance = road_start_point.distance(target_frame.points[0])
        close_point_index = 0
        for i in range(len(target_frame.points)):
            distance = road_start_point.distance(target_frame.points[i])
            if distance < min_distance:
                min_distance = distance
                close_point_index = i

        # 道路始点が0番目になるように座標回転
        target_frame = target_frame.rotate_frame(close_point_index)

        get_search_frame_flag = True
        search_point_list = []
        remain_search_point_list = []

        # Draw.debug_png_by_frame_list([Frame([cat_line_start_point, cat_line_end_point])], "cat_line", [target_frame])

        for i in range(len(target_frame.points)):
            # cat_lineとtarget_frameの辺の交点を求める
            the_point = target_frame.points[i]
            the_next_point = target_frame.points[(i + 1) % len(target_frame.points)]

            cross_point = Calc.line_cross_point(the_point, the_next_point, cat_line_start_point, cat_line_end_point, 0, 0)
            if get_search_frame_flag:
                search_point_list.append(the_point)
            else:
                remain_search_point_list.append(the_point)

            if cross_point is not None:
                search_point_list.append(cross_point)
                remain_search_point_list.append(cross_point)
                get_search_frame_flag = not get_search_frame_flag

        # リストが時計回りの時に反転させる
        if Calc.is_clockwise(search_point_list):
            search_point_list.reverse()

        # search_point_listを出力
        # for i in range(len(search_point_list)):
        #     print(f"search_point_list[{i}]: {search_point_list[i].get_str()}")

        search_frame = Frame(search_point_list)
        remain_search_frame = Frame(remain_search_point_list)

        # Draw.debug_png_by_frame_list([search_frame], "search_frame", [target_frame])
        # Draw.debug_png_by_frame_list([remain_search_frame], "remain_search_frame", [target_frame])

        return search_frame, remain_search_frame

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
        list_x, list_y = [], []
        for i in range(len(self.points)):
            list_x.append(self.points[i].x)
            list_y.append(self.points[i].y)
        return list_x, list_y

    def move_positive(self):
        """区画を第一象限に移動する"""
        list_x, list_y = self.get_list_xy()
        min_x = abs(min(list_x)) if (min(list_x) < 0) else 0
        min_y = abs(min(list_y)) if (min(list_y) < 0) else 0

        move_positive_point = Point(min_x, min_y)
        self = self.move_frame(move_positive_point)

    def move_zero(self):
        """区画を原点に移動する"""
        list_x, list_y = self.get_list_xy()
        min_x, min_y = min(list_x), min(list_y)
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
        min_x, min_y = min(list_x), min(list_y)
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

    def draw_frame(self, color_index=1):
        """区画をdxfファイルに描画する

        Args:
            color_index (int): 色
        """
        Draw.draw_line_by_point(self.points, color_index)

    def rotate_frame(self, rotate_count):
        """区画を回転させる

        Args:
            rotate_count (int): 回転させる回数

        Returns:
            Frame: 回転させた区画
        """
        # rotate_count = rotate_count % len(self.points)
        # TODO: 正常に動いていない可能性
        rotated_points = deque(self.points)
        rotated_points.rotate(rotate_count)
        return Frame(list(rotated_points))
