import numpy as np
import drowdxf
import sys
sys.path.append('../')
import Calc

"""_summary_
    ベクトルのリストと点を受け取り、その点がどのベクトルと交差するかを返す
"""
def getclossvecs(vecs, point):
    arrayList_clossvecs = []
    targetareaflag = True

    # ベクトルのリストと点を受け取り、その点がどのベクトルと交差するかを返す
    for i in range(len(vecs)):
        start = vecs[i]
        end = vecs[i + 1] if i + 1 < len(vecs) else vecs[0]
        if (targetareaflag):
            arrayList_clossvecs.append(start)
        
        if (start[0] < point and point < end[0]) or (end[0] < point and point < start[0]):
            y = (end[1] - start[1]) / (end[0] - start[0]) * (point - start[0]) + start[1]
            arrayList_clossvecs.append([point,y])
            targetareaflag = not targetareaflag
    
    # print(np.array(arrayList_clossvecs))
    return np.array(arrayList_clossvecs)


"""
二分探索
"""
def binarysearch(vecs,targetarea):
    min_x, max_x = 0, 0
    for i in range(len(vecs)):
        if i == 0:
            min_x = vecs[i][0]
            max_x = vecs[i][0]
        else:
            if vecs[i][0] < min_x:
                min_x = vecs[i][0]
            if vecs[i][0] > max_x:
                max_x = vecs[i][0]
    print("min_x",min_x,"max_x",max_x)

    closet_x = 0
    min_diff = targetarea

    while min_x < max_x:
        # 中央値を求める
        temp_x = ((min_x + max_x) / 2)

        # 図形の取得 個々の処理を関数化したい（むずそう）
        temp_vec = getclossvecs(vecs, temp_x)

        # 面積を求める
        temp_area = Calc.calc(temp_vec)

        #　中心の左右の値と比較
        temp_x_right = temp_x + 1
        temp_vec_right =getclossvecs(vecs, temp_x_right)
        temp_area_right = Calc.calc(temp_vec_right)
        min_diff_right = abs(targetarea - temp_area_right)

        temp_x_left = temp_x - 1
        temp_vec_left =getclossvecs(vecs, temp_x_left)
        temp_area_left = Calc.calc(temp_vec_left)
        min_diff_left = abs(targetarea - temp_area_left)

        if min_diff_right < min_diff_left:
            min_diff = min_diff_left
            closet_x = temp_x_right
        else:
            min_diff = min_diff_right
            closet_x = temp_x_left
        
        # 2分探索
        if temp_area > targetarea:
            max_x = temp_x - 1
        elif temp_area < targetarea:
            min_x = temp_x + 1
        else:
            return temp_x
        
    return temp_x


# ファイルのクリア
drowdxf.cleardxf()

# ベクトルのリストを受け取り、それを線分としてdxfファイルに出力する
vec =np.array([[-30,-10], [30,-30], [50,20], [-20,10]])
drowdxf.drowLine(vec)

print("全体面積",Calc.calc(vec))

targetarea = 500

print("目標面積",targetarea)

x = binarysearch(vec, targetarea)
drowdxf.drowLine(getclossvecs(vec, x))
print("実際面積",Calc.calc(getclossvecs(vec, x)))