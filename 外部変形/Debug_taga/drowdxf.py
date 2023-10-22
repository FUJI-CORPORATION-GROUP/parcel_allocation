import ezdxf
import numpy as np


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


"""_summary_
    dxfファイルをクリアする
"""
def cleardxf():
    doc = ezdxf.new("R2010")
    doc.saveas('debug_taga.dxf')


# サンプル
# vec =np.array([[0,0], [100,0], [100,100], [0,100], [0,0]])
# drowLine(vec)