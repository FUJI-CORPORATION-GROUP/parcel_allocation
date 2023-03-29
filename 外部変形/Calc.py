import math
import copy

#点が図形内部あるかどうかの判定
def inside_polygon(p0, qs):
  # print("p0:" + str(p0))
  # print("qs:" + str(qs))
  cnt = 0
  L = len(qs)
  x, y = p0
  #判定
  for i in range(L):
      x0, y0 = qs[i-1]; x1, y1 = qs[i]
      x0 -= x; y0 -= y
      x1 -= x; y1 -= y

      cv = x0*x1 + y0*y1
      sv = x0*y1 - x1*y0
      if sv == 0 and cv <= 0:
          # a point is on a segment
          return True

      if not y0 < y1:
          x0, x1 = x1, x0
          y0, y1 = y1, y0

      if y0 <= 0 < y1 and x0*(y1 - y0) > y0*(x1 - x0):
          cnt += 1
  return (cnt % 2 == 1)

#点が線分上にあるどうかを判定
def line_judge(p1, p2, qx, qy):
  print("p1:" + str(p1))
  print("p2:" + str(p2))
  print("qx:" + str(qx))
  print("qy:" + str(qy))
  #渡された点をそれぞれ代入
  p1x, p1y = p1
  p2x, p2y = p2
  # print((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x))
  # print((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y))
  print("線上判定：" + str((qy * (p1x - p2x)) + (p1y * (p2x - qx)) + (p2y * (qx - p1x))))
#点qが線分上にあればTrueを返す
  if ((p1x <= qx) and (qx <= p2x)) or ((p2x <= qx) and (qx <= p1x)):
    if ((p1y <= qy) and (qy <= p2y)) or ((p2y <= qy) and (qy <= p1y)):
      #if ((qy * (p1x - p2x)) + (p1y * (p2x - qx)) + (p2y * (qx - p1x)) == 0):
      # 点Pが線分AB上にある
      return True
  #線上になかったのでFalseを返す
  return False

#式の傾き・切片の計算
def line_formula(xy1, xy2):
  #計算しやすいように代入
  x1,y1 = xy1
  x2,y2 = xy2
  #座標からの算出
  a = (y1 - y2) / (x1 - x2)
  b = y1 - a * x1
  return (a, b)

#直線同士の交点の計算
def line_cross_point(P0, P1, Q0, Q1):
  x0, y0 = P0; x1, y1 = P1
  x2, y2 = Q0; x3, y3 = Q1
  a0 = x1 - x0; b0 = y1 - y0
  a2 = x3 - x2; b2 = y3 - y2
  d = a0*b2 - a2*b0
  if d == 0:
    # 並行の場合
    return None
  # 交点計算
  sn = b2 * (x2-x0) - a2 * (y2-y0)
  x = x0 + a0*sn/d
  y = y0 + b0*sn/d
  #交点が線上に存在する場合のみ描画
  if (x0 <= x <= x1 and y0 <= y <= y1) or (x0 >= x >= x1 and y0 >= y >= y1) or (x0 <= x <= x1 and y0 >= y >= y1) or (x0 >= x >= x1 and y0 <= y <= y1):
    return x, y
  else:
    return None

#正のみを返す面積計算関数
def calc(data):
    #算出した値を合計して返す
    return sum(calc_triangle(tri) for tri in divide_triangles(data))

#3点から面積を計算する関数
def calc_triangle(pts):
    (ax, ay), (bx, by), (cx, cy) = pts
    return abs((ax - cx) * (by - ay) - (ax - bx) * (cy - ay)) / 2

#図形を三角形に分割していく関数
def divide_triangles(poly):
    for i in range(len(poly) - 2):
        yield poly[0], poly[i + 1], poly[i + 2]

#符号付き面積が正か負か判断する関数
def deci_triangle(data):
    (ax, ay), (bx, by), (cx, cy) = data
    tri = ((ax - cx) * (by - ay) - (ax - bx) * (cy - ay)) / 2
    #内角が180以上ならTrue,そうでないならFalseを返す
    if(tri < 0):
        return True
    else:
        return False

#180度以上の角の検出
def ob_angle(data):
    #180度以上の角が存在するか否か
    Flag = False
    #内角が180以上の角を算出
    for i in range(len(data) - 2):
        t_angle = data[i], data[i + 1], data[i + 2]
        if(deci_triangle(t_angle)):
            Flag = True
    #for文で網羅できなかった最後の角の確認
    t_angle = data[len(data) - 2], data[len(data) - 1], data[0]
    if(deci_triangle(t_angle)):
        Flag = True
    #最初の角の確認
    t_angle = data[len(data) - 1], data[0], data[1]
    if(deci_triangle(t_angle)):
        Flag = True
    return Flag

#三点の符号付き面積を算出
def ob_calc(data):
    (ax, ay), (bx, by), (cx, cy) = data
    return ((ax - cx) * (by - ay) - (ax - bx) * (cy - ay)) / 2

#減算面積を算出
def dec_area(data, ob_data):
    #減算する面積の合計
    min_sum = 0
    min_flag = False
    ob_flag = True
    true_list = []
    min_list = []
    min_calc = []
    # print("データ：" + str(data))
    #180度以上座標データの位置の取得
    for i in range(len(ob_data)):
        for j in range(len(data)):
            if ob_data[i] == data[j]:
                true_list.append(j)
    true_list.sort()
    # print("数値データ：" + str(true_list))
    # print("内角180度以上の座標：" + str(ob_data))
    #初期化
    i = 0
    j = 0
    if(ob_angle(data)):
        ob_flag = True
    else:
        ob_flag = False
    #180度以上の角の面積の算出
    while ob_flag:
        ob_flag = True
        #180度以上データの一つ目をリストに追加
        min_list.append(true_list[i])
        #180度以上座標データが存在する限りループ
        if(len(true_list) > 1):
            #隣り合う座標確認(前向き)
            while True:
                if(str(true_list[i + 1]) == str(int(true_list[i]) + 1)):
                    min_list.append(true_list[i + 1])
                else:
                    break
                if(i + 2 >= len(true_list)):
                    break
                i += 1
            #隣り合う座標確認(後ろ向き)
            while True:
                if j - 1 <= 0:
                    j = len(min_list)
                    if(str(int(true_list[j - 1])) == str(int(true_list[0]) - 1)):
                        min_list.append(true_list[j])
                        j -= 1
                    else:
                        break
                #連続を検証
                if(str(int(true_list[j - 1])) == str(int(true_list[j]) - 1)):
                    min_list.append(true_list[j - 1])
                if(j - 2 <= 0):
                    break
                j -= 1
        
        #初期化
        i = 0
        j = 0
        
        #180度以上の値をリストから削除
        for r in min_list:
            true_list.remove(r)
        # print("削除後：" + str(true_list))
        
        #最大値+1と最小値-1の数値をリストに追加
        if(max(min_list) + 1 < len(data)):
            min_list.append(max(min_list) + 1)
        else:
            min_flag = True
            min_list.append(0)
        if(min(min_list) - 1 > -1):
            min_list.append(min(min_list) - 1)
        elif(min_flag):
            #print("ソート済み：" + str(sorted(min_list)))
            min_list.append(sorted(min_list)[1] - 1)
        else:
            min_list.append(len(data) - 1)
        
        #180度以上角のを含む面積の座標
        for k in min_list:
            min_calc.append(data[k])
        
        #リストを逆順に
        min_calc.reverse()
        # print("逆順：" + str(min_calc))
        
        #180度以上の角を含む面積の算出
        if(ob_angle(min_calc)):
            min_sum += main_calc(min_calc)
        else:
            min_sum += calc(min_calc)
        
        # print("減算面積：" + str(min_sum))
        
        #リストの初期化
        min_list.clear()
        min_calc.clear()
        
        #180度以上の座標がなくなったら終了
        if(len(true_list) == 0):
            ob_flag = False
    
    #減算する面積の返却
    return min_sum

#最大面積の計算関数
def all_area(data, ob_data):
    # print("data:" + str(data))
    # print("ob_data:" + str(ob_data))
    
    #180度以上の座標を削除した状態の座標
    for i in ob_data:
            data.remove(i)
    
    
    #鋭角のみの面積の算出
    sum = calc(data)
    
    return sum

#重複した座標の存在の検知
def has_duplicates(p1, p2, p3, p4):
    seq = [p1, p2, p3, p4]
    seen = []
    unique_list = [x for x in seq if x not in seen and not seen.append(x)]
    return len(seq) != len(unique_list)

#座標の交差判定
def intersect(p1, p2, p3, p4):
    if(has_duplicates(p1, p2, p3, p4)):
        Flag = False
    else:
        #座標4点の交差を判定
        tc1 = (p1[0] - p2[0]) * (p3[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - p3[0])
        tc2 = (p1[0] - p2[0]) * (p4[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - p4[0])
        td1 = (p3[0] - p4[0]) * (p1[1] - p3[1]) + (p3[1] - p4[1]) * (p3[0] - p1[0])
        td2 = (p3[0] - p4[0]) * (p2[1] - p3[1]) + (p3[1] - p4[1]) * (p3[0] - p2[0])
        
        if(tc1 == tc2 == td1 == td2 == 0):
            Flag = False
        elif(tc1*tc2<=0 and td1*td2<=0):
            Flag = True
        else:
            Flag = False
    
    #結果の正誤を返却
    return Flag

#座標データすべてによる交差判定
def closs(data):
    closs_flag = True
    
    #座標の中に交差している物が存在すればFalse返却
    if len(data) > 5:
        for i in range(len(data)):
            if(i < len(data) - 3):
                if(intersect(data[i], data[i + 1], data[i + 2], data[i + 3])):
                    closs_flag = False
            elif(i == len(data) - 3):
                if(intersect(data[i], data[i + 1], data[i + 2], data[0])):
                    closs_flag = False
            elif(i == len(data) - 2):
                if(intersect(data[i], data[i + 1], data[0], data[1])):
                    closs_flag = False
            elif(i == len(data) - 1):
                if(intersect(data[i], data[0], data[1], data[2])):
                    closs_flag = False
    
    #交差が存在するかどうかのフラグを返却
    return closs_flag

#内側の座標を検出する関数
def in_judge(data):
    angle_flag = True
    cp_data = copy.copy(data)
    res_data = []
    in_list = []
    i = 0
    
    #180度を超える角の座標リスト作成
    if(ob_angle(data)):
        while len(cp_data) > 3:
            
            #180度を超える角がある限りループ
            while angle_flag:
                res_data = copy.copy(cp_data)
                
                #for文で網羅できなかった最後の角の確認
                if(i + 2 == len(cp_data)):
                    coor = cp_data[i], cp_data[i + 1], cp_data[0]
                    if(0 > ob_calc(coor)):
                        res_data.remove(res_data[i + 1])
                        if(closs(res_data)):
                            in_list.append(cp_data[i + 1])
                            cp_data.remove(cp_data[i + 1])
                            # print("ob_angle" + str(ob_angle(cp_data)))
                            i = 0
                            # print("if:" + str(cp_data))
                        else:
                            i += 1
                        
                        #180度を超える角がなければbreak
                        if not ob_angle(cp_data):
                            angle_flag = False
                    else:
                        i += 1
                elif(i + 1 == len(cp_data)):
                    coor = cp_data[i], cp_data[0], cp_data[1]
                    if(0 > ob_calc(coor)):
                        res_data.remove(res_data[0])
                        if(closs(res_data)):
                            in_list.append(cp_data[0])
                            cp_data.remove(cp_data[0])
                            i = 0
                            # print("elif:" + str(cp_data))
                        else:
                            i += 1
                        
                        #180度を超える角がなければbreak
                        if not ob_angle(cp_data):
                            angle_flag = False
                    else:
                        i += 1
                
                #180度を超える角があればリストに追加
                else:
                    coor = cp_data[i], cp_data[i + 1], cp_data[i + 2]
                    #180度超えるかの判定
                    if(0 > ob_calc(coor)):
                        res_data.remove(res_data[i + 1])
                        if(closs(res_data)):
                            in_list.append(cp_data[i + 1])
                            cp_data.remove(cp_data[i + 1])
                            i = 0
                            # print("else:" + str(cp_data))
                        else:
                            # print("交差あり")
                            i += 1
                        
                        #180度を超える角がなければbreak
                        if not ob_angle(cp_data):
                            angle_flag = False
                    else:
                        i += 1
                    
            #角削除後、再度確認
            if not ob_angle(cp_data):
                #完全に180度を超える角がなくなれがループ終了
                break
    
    return in_list

#面積の計算
def main_calc(data):
    cp_data = copy.copy(data)
    in_list_d = []
    in_list = []
    i = 0
    
    #座標の確認
    # print("受け取った座標：" + str(cp_data))
    
    #180度を超える角の座標リスト
    in_list_d = in_judge(data)
    
    #180度以上の座標データのソート
    for j in range(len(data)):
        for i in range(len(in_list_d)):
            if in_list_d[i] == data[j]:
                in_list.append(in_list_d[i])
    
    # print("座標が内側に存在する角：" + str(in_list))
    
    if len(in_list) > 1:
        #減算する面積の算出
        min_sum = dec_area(data, in_list)
    
    #新たに作成したリストの面積の計算
    sum = all_area(data, in_list)
    # print("概算面積：" + str(sum))
    
    if len(in_list) > 1:
        #削除した角を含む三角形を減算
        sum -= min_sum
    
    #面積を返す
    return sum
