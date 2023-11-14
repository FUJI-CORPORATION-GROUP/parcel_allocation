import numpy as np

class Point:
    """座標を扱うクラス

    functions:
        distance (list, list): _距離同士の距離を求める
        point_to_line_distance (list, list, list): _点と直線の距離公式

    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        """距離を求める関数

        Args:
            self (Point): _距離を求めたい点リスト
            other (Point): _もう一個の点

        Returns:
            distance (float): _点と点の距離
        """
        distance_vec = np.array([other.x - self.x, other.y - self.y])
        distance = np.linalg.norm(distance_vec)
        return distance

    def point_to_line_distance(self, line_pointA, line_pointB):
        """点と直線の距離を求める

        Args:
            self (list): _距離を求めたい点リスト
            line_pointA (list): _直線の片方の点
            line_pointB (list): _直線のもう片方の点

        Returns:
            distance (float): _点と直線の距離
        """
        u = np.array([line_pointB.x - line_pointA.x, line_pointB.y - line_pointA.y])
        v = np.array([self.x - line_pointA.x, self.y - line_pointA.y])
        distance = abs(np.cross(u, v) / np.linalg.norm(u))
        return distance

    def to_np_array(self):
        """listをnumpyのarrayに変更する関数

        Args:
            self (list): _arrayに変更したいリスト

        Returns:
            array (array): _変換後のarray
        """
        array = np.array([self.x,self.y])
        return array
    
    def get_str(self):
        return f"({self.x}, {self.y})"