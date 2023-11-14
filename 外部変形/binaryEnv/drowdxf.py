import ezdxf
import numpy as np
from point import Point

"""_summary_
    ベクトルのリストを受け取り、それを線分としてdxfファイルに出力する
"""
# Point型
def drowLine_by_point(pointlist):
    # cleardxf()
    
    doc = ezdxf.readfile(r"./output.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(pointlist)):
        s = pointlist[i].to_np_array()*100000
        e = pointlist[i+1].to_np_array()*100000 if i+1 < len(pointlist) else pointlist[0].to_np_array()*100000
        msp.add_line(s, e)

    doc.saveas('output.dxf')


"""_summary_
    dxfファイルをクリアする
"""
def cleardxf():
    doc = ezdxf.new("R2010")
    doc.saveas('output.dxf')


# サンプル
# vec =np.array([[0,0], [100,0], [100,100], [0,100], [0,0]])
# drowLine(vec)

