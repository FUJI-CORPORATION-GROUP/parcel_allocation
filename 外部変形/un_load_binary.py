# -*- coding: utf-8 -*-
import numpy as np
from numpy import linalg as LA
import Calc
import random
from scipy.spatial import distance
import copy
import evaluate_calc

def paramas_calc(count, road_edge, maguti, least_maguti, goal_area):
	"""今後の計算で使用する値を算出する関数

	Args:
			count (int): _計算のカウント
			road_edge (list): _街区が道路に接している辺のリスト
			maguti (int): _間口の広さ
			least_maguti (int): _間口の下限(上限)値
			goal_area (int): _目標面積

	Returns:
			road_distance: _長辺の長さ
			use_maguti: _使用する間口
			home_cnt: _建てる家の戸数
			home_depth: _使用する奥行き
			maguti_vector: _間口単位ベクトル
			depth_vector: _奥行き単位ベクトル
	"""
	#指定街区の辺の長さ
	a=np.array(road_edge[count][0])
	b=np.array(road_edge[count][1])

	#関数に使用する変数の計算
	road_distance = np.linalg.norm(b-a) # 長辺の長さ
	use_maguti = random.randrange(maguti, least_maguti) if least_maguti >= maguti else random.randrange(least_maguti, maguti) # 使用する間口
	home_cnt = int(road_distance / use_maguti) # 辺に建てる戸数
	home_depth = goal_area / use_maguti # 奥行き

	# 区画に使うベクトルの計算
	maguti_vector = [(road_edge[count][1][0] - road_edge[count][0][0]) / road_distance, (road_edge[count][1][1] - road_edge[count][0][1]) / road_distance] #間口単位ベクトル
	depth_vector = [-maguti_vector[1] * home_depth, maguti_vector[0] * home_depth] # 奥行き単位ベクトル

	return road_distance, use_maguti, home_cnt, home_depth, maguti_vector, depth_vector


def end_area_calc(goal_area, home_depth, maguti_vector, depth_vector, frame):
	"""端の区画を計算する関数

	Args:
			goal_area (int): _目標面積
			home_depth (int): _奥行きの長さ
			maguti_vector (list): _間口単位ベクトル
			depth_vector (list): _奥行き単位ベクトル
			frame (list): _街区リスト

	Returns:
			area_list: _端区画の座標群
	"""
	area_list = []

	# 間口の長さとベクトルからビンの底辺を算出する
	# 街区を二分探索用に切った図形を算出する
	# 二分探索を実行する


	
	return area_list


####道を作成しないケースの区画割の実行####
def unload_parcel_allocation(frame, road_edge, maguti, least_maguti, goal_area):
	"""進入経路を確保しない際の区画割実行関数

	Returns:
			result: _結果の座標リスト jwへの描画用に[[A, B], [B, C]]の形式で記述
			point_list: _評価結果得点の集合リスト [向き, 広さ, 面積]の順に格納
			total_score: _各結果の合計スコア
			evaluation: _評価用に加工した二次元配列座標群
	"""
	print("道を作成しない区画割+二分探索")
	result = 0
	point_list = []
	total_score = []
	evaluation = []

	#道路に隣接している辺の数だけ区画を作成
	for k in range(len(road_edge)):
		
		# 計算に使う値を算出
		road_distance, use_maguti, home_cnt, home_depth, maguti_vector, depth_vector = paramas_calc(k, road_edge, maguti, least_maguti, goal_area)

		# 端区画を計算
		unload_parcel_allocation(goal_area, home_depth, maguti_vector, depth_vector, frame)


	

	return result, point_list, total_score, evaluation