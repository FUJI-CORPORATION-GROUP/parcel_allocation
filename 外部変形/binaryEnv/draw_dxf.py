import ezdxf
import numpy as np
from point import Point

"""_summary_
    ベクトルのリストを受け取り、それを線分としてdxfファイルに出力する
"""
# Point型
def draw_line_by_point(pointlist):
    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(pointlist)):
        s = pointlist[i].to_np_array()*100000
        e = pointlist[i+1].to_np_array()*100000 if i+1 < len(pointlist) else pointlist[0].to_np_array()*100000
        msp.add_line(s, e)

    doc.saveas('output.dxf')

"""_summary_
    ベクトルのリストを受け取り、それを線分としてdxfファイルに出力する
"""
# Point型
def draw_line_by_point_color(pointlist,color_index):
    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(pointlist)):
        s = pointlist[i].to_np_array()*100000
        e = pointlist[i+1].to_np_array()*100000 if i+1 < len(pointlist) else pointlist[0].to_np_array()*100000
        msp.add_line(s, e,dxfattribs={'color':color_index})

    doc.saveas('output.dxf')

# FrameList型
def draw_line_by_frame_list_color(frame_list,color_index):
    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")
    msp = doc.modelspace()

    for i in range(len(frame_list)):
        #モデル空間に新しいエンティティを作成
        pointlist = frame_list[i].points
        for i in range(len(pointlist)):
            s = pointlist[i].to_np_array()*100000
            e = pointlist[i+1].to_np_array()*100000 if i+1 < len(pointlist) else pointlist[0].to_np_array()*100000
            msp.add_line(s, e,dxfattribs={'color':color_index})

    doc.saveas('output.dxf')


"""_summary_
    dxfファイルをクリアする
"""
def clear_dxf():
    doc = ezdxf.new("R2010")
    doc.saveas('output.dxf')

