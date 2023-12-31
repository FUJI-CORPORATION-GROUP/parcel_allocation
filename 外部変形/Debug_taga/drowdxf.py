import ezdxf
import numpy as np
# from point import Point, Vector3



"""_summary_
    ベクトルのリストを受け取り、それを線分としてdxfファイルに出力する
"""
def drowLine(vecs):
    doc = ezdxf.readfile(r"./debug_taga.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(vecs)):
        s = vecs[i]*100000
        e = vecs[i+1]*100000 if i+1 < len(vecs) else vecs[0]*100000
        msp.add_line(s, e)

    doc.saveas('debug_taga.dxf')

# Point型
def drowLine_by_point(pointlist):
    doc = ezdxf.readfile(r"./debug_taga.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(pointlist)):
        s = pointlist[i].to_np_array()*100000
        e = pointlist[i+1].to_np_array()*100000 if i+1 < len(pointlist) else pointlist[0].to_np_array()*100000
        msp.add_line(s, e)

    doc.saveas('debug_taga.dxf')


"""_summary_
    dxfファイルをクリアする
"""
def cleardxf():
    doc = ezdxf.new("R2010")
    doc.saveas('debug_taga.dxf')


# サンプル
# vec =np.array([[0,0], [100,0], [100,100], [0,100], [0,0]])
# drowLine(vec)

