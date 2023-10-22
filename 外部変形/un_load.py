# -*- coding: utf-8 -*-
import numpy as np
from numpy import linalg as LA
import Calc
import random
from scipy.spatial import distance
import copy
import evaluate_calc

####道を作成しないケースの区画割の実行####
def unload_parcel_allocation(frame, road_edge, maguti, least_maguti, goal_area):
	print("\t================================")
	print("\t道を作成しない区画割の実行 unload_parcel_allocation")
	print("\t================================")
	exist_flag = False
	result = []
	# detail_list = []
	total_score = []
	evaluation = []
	inter_coor = []
	instant_result = []
	eva_coor = []
	instant_coor_a = []
	instant_coor_b = []
	instant_coor = []
	area_calc = []
	maguti_coor = []
	depth_coor = []
	parcel_frame = copy.deepcopy(frame)

	#道路に隣接している辺の数だけ区画を作成
	for k in range(len(road_edge)):
		# parcel_frame = copy.deepcopy(frame)
		print("\t----------" + str(k + 1) + "周目----------")
		#指定街区の辺の長さ
		a=np.array(road_edge[k][0])
		b=np.array(road_edge[k][1])
    #長さ計算
		road_distance = np.linalg.norm(b-a)
		#使用する間口の決定
		# use_maguti = random.randint(maguti, least_maguti)
		use_maguti = random.randrange(maguti, least_maguti) if least_maguti >= maguti else random.randrange(least_maguti, maguti)
		#辺上に建てられる戸数を決定
		home_cnt = int(road_distance / use_maguti)
		if home_cnt > 1:
			#奥行きの決定
			home_depth = goal_area / use_maguti
			#間口毎のベクトルの算出
			#edge[0]から[1]への単位ベクトルの算出
			maguti_deviation = [(road_edge[k][1][0] - road_edge[k][0][0]) / road_distance, (road_edge[k][1][1] - road_edge[k][0][1]) / road_distance]
			#直角内側(左に折れる)のベクトルの算出
			depth_deviation = [-maguti_deviation[1] * home_depth, maguti_deviation[0] * home_depth]
			print("vector_calc:" + str(road_edge[k][1][0] - road_edge[k][0][0]))
			print("maguti_deviation:" + str(maguti_deviation))
			print("depth_deviation:" + str(depth_deviation))
			#間口座標(一つ目)の算出
			maguti_coor = [road_edge[k][0][0] + maguti_deviation[0], road_edge[k][0][1] + maguti_deviation[1]]
			#奥行き座標(一つ目)の算出
			depth_coor = [road_edge[k][0][0] + depth_deviation[0], road_edge[k][0][1] + depth_deviation[1]]
			#奥行座標と間口間ベクトルで構成された直線と枠線の交点（二点）を算出
			for i in range(1, len(parcel_frame)):
				intersection = Calc.line_cross_point(parcel_frame[i - 1], parcel_frame[i], [depth_coor[0], depth_coor[1]], [depth_coor[0] + maguti_deviation[0], depth_coor[1] + maguti_deviation[1]])
				print("parcel_" + str(i - 1) + ":" + str(parcel_frame[i - 1]))
				print("parcel_" + str(i) + ":" + str(parcel_frame[i]))
				print("depth_coor[0]:" + str(depth_coor[0]))
				print("depth_coor[1]:" + str(depth_coor[1]))
				print("intersection:" + str(intersection))
				#交点を追加
				if intersection is not None:
					area_calc.append(road_edge[k][0])
					area_calc.append(maguti_coor)
					area_calc.append(depth_coor)
					for j in range(i, len(parcel_frame)):
						area_calc.append(parcel_frame[j])
					area = Calc.calc(area_calc)
					if area >= goal_area:
						area_calc = []
						inter_coor.append(intersection)
					else:
						a=np.array(depth_coor)
						b=np.array(maguti_coor)
						depth_distance = np.linalg.norm(b-a)
						need_area = goal_area - area
						move_distance = need_area / depth_distance
						maguti_coor = [maguti_coor[0] + maguti_deviation[0] * move_distance, maguti_coor[1] + maguti_deviation[1] * move_distance]
						depth_coor = [depth_coor[0] + depth_deviation[0] * move_distance, depth_coor[1] + depth_deviation[1] * move_distance]
						intersection = Calc.line_cross_point(parcel_frame[i - 1], parcel_frame[i], [depth_coor[0], depth_coor[1]], [depth_coor[0] + maguti_deviation[0], depth_coor[1] + maguti_deviation[1]])
						
				else:
					print("角度が小さすぎるので別の処理推奨")
				inter_coor.append(intersection)
			if k % 2 == 0:
				#inter_coorを逆順にソート
				inter_coor.reverse()
			if len(inter_coor) == 2:
				#結果リストに格納(本来は図形内にあるかの確認が必要！！！)
				result.append([[inter_coor[0][0], inter_coor[0][1]], [inter_coor[1][0], inter_coor[1][1]]])
				#各種数値の出力（デバッグ）
				print("road_distance:" + str(road_distance))
				print("home_cnt:" + str(home_cnt))
				print("real_maguti:" + str(use_maguti))
				print("home_depth:" + str(home_depth))
				print("least_maguti:" + str(least_maguti))
				print("inter_coor:" + str(inter_coor))
				print("result:" + str(result))
				#
				#各家の座標を格納(間口間ベクトル参照)
				for i in range(1, home_cnt):
					cp_inter_coor = copy.deepcopy(inter_coor)
					exist_flag = True
					instant_coor_a.append(road_edge[k][0][0] + (i * maguti_deviation[0] * maguti))
					instant_coor_a.append(road_edge[k][0][1] + (i * maguti_deviation[1] * maguti))
					instant_coor_b.append(instant_coor_a[0] + depth_deviation[0])
					instant_coor_b.append(instant_coor_a[1] + depth_deviation[1])
					instant_coor.append(instant_coor_a)
					instant_coor.append(instant_coor_b)
					instant_result.extend(instant_coor)
					instant_coor_a = []
					instant_coor_b = []
					instant_coor = []
					#まとめた座標を結果に追加
					result.append(instant_result)
					eva_coor.append(instant_result[0])
					eva_coor.append(instant_result[1])
					instant_result = []
					#結果の確認(デバッグ用)
					print("result:" + str(result))
					print("eva_coor:" + str(eva_coor))
					if exist_flag:
						if k % 2 == 0:
							if i == 1:
								evaluation.append([eva_coor[0], eva_coor[1], [cp_inter_coor[0][0], cp_inter_coor[0][1]], parcel_frame[0]])
							elif i == home_cnt - 1:
								evaluation.append([eva_coor[i * 2 - 2], eva_coor[i * 2 - 1], eva_coor[i * 2 - 3], eva_coor[i * 2 - 4]])
								evaluation.append([parcel_frame[1], [cp_inter_coor[1][0], cp_inter_coor[1][1]], eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2]])
								break
							else:
								evaluation.append([eva_coor[i * 2 - 2], eva_coor[i * 2 - 1], eva_coor[i * 2 - 3], eva_coor[i * 2 - 4]])
						else:
							if i == 1:
								evaluation.append([[cp_inter_coor[0][0], cp_inter_coor[0][1]], parcel_frame[2], eva_coor[0], eva_coor[1]])
							elif i == home_cnt - 1:
								evaluation.append([eva_coor[i * 2 - 3], eva_coor[i * 2 - 4], eva_coor[i * 2 - 2], eva_coor[i * 2 - 1]])
								evaluation.append([parcel_frame[3], [cp_inter_coor[1][0], cp_inter_coor[1][1]], eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2]])
								break
							else:
								evaluation.append([eva_coor[i * 2 - 3], eva_coor[i * 2 - 4], eva_coor[i * 2 - 2], eva_coor[i * 2 - 1]])
					else:
						if k % 2 == 0:
							evaluation.append([parcel_frame[1], [inter_coor[1][0], inter_coor[1][1]], eva_coor[(i - 1) * 2 - 2], eva_coor[(i - 1) * 2 - 1]])
							break
						else:
							evaluation.append([eva_coor[(i - 1) * 2 - 1], eva_coor[(i - 1) * 2 - 2], [inter_coor[1][0], inter_coor[1][1]], parcel_frame[3]])
							break
				exist_flag = False
				eva_coor = []
				for i in range(len(parcel_frame)):
					for j in range(len(road_edge[k])):
						if parcel_frame[i] == road_edge[k][j]:
							parcel_frame[i] = [inter_coor[j][0], inter_coor[j][1]]
				eva_coor = []
				inter_coor = []
				print("evaluation:" + str(evaluation))
				print("parcel_frame:" + str(parcel_frame))
				print("result:" + str(result))
			print("----------" + str(k + 1) + "週目終わり----------")

	print("\n\t評価要素：" + str(evaluation))
	cp_evaluation = copy.deepcopy(evaluation)

	#評価用の配列の定義
	point_list = []

	#評価の実行
	point_list = evaluate_calc.unload_eval(cp_evaluation, goal_area)
	total_score = sum(point_list)

	print("point_list:" + str(point_list))
	print("total_score:" + str(total_score))
	print("parcel_frame:" + str(parcel_frame))
	print("cp_evaluation:" + str(cp_evaluation))

	return result, point_list, total_score, evaluation