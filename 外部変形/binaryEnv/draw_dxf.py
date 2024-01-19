import ezdxf
import numpy as np
from point import Point
from frame import Frame
from plan import Plan


def draw_line_by_point(point_list):
    """Point型のリストからdxf出力
    Args:
        point_list (list): Point型のリスト
    """

    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(point_list)):
        s = point_list[i].to_np_array()
        e = point_list[i+1].to_np_array() if i+1 < len(point_list) else point_list[0].to_np_array()
        msp.add_line(s, e)

    doc.saveas('output.dxf')

# Point型
def draw_line_by_point_color(point_list,color_index):
    """Point型のリストと色指定してdxf出力

    Args:
        point_list (list): Point型のリスト
        color_index (int): 色
    """
    
    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")

    #モデル空間に新しいエンティティを作成
    msp = doc.modelspace()
    for i in range(len(point_list)):
        s = point_list[i].to_np_array()
        e = point_list[i+1].to_np_array() if i+1 < len(point_list) else point_list[0].to_np_array()
        msp.add_line(s, e,dxfattribs={'color':color_index})

    doc.saveas('output.dxf')

# FrameList型
def draw_line_by_frame_list_color(frame_list,color_index):
    """FrameList型のリストと色指定してdxf出力

    Args:
        frame_list (list): FrameList型のリスト
        color_index (int): 色
    """
    # clear_dxf()
    
    doc = ezdxf.readfile(r"./output.dxf")
    msp = doc.modelspace()

    for i in range(len(frame_list)):
        #モデル空間に新しいエンティティを作成
        point_list = frame_list[i].points
        for i in range(len(point_list)):
            s = point_list[i].to_np_array()
            e = point_list[i+1].to_np_array() if i+1 < len(point_list) else point_list[0].to_np_array()
            msp.add_line(s, e,dxfattribs={'color':color_index})

    doc.saveas('output.dxf')

def draw_dxf_by_plan_list(plan_list, color_index):
    """PlanList型のリストと色指定してdxf出力

    Args:
        plan_list (list): PlanList型のリスト
        color_index (int): 色
    """
    doc = ezdxf.readfile(r"./output.dxf")
    msp = doc.modelspace()
    
    for plan in plan_list:
        frame_list = plan.get_frame_list()        
        for i in range(len(frame_list)):
            #モデル空間に新しいエンティティを作成
            point_list = frame_list[i].points
            for i in range(len(point_list)):
                s = point_list[i].to_np_array()
                e = point_list[i+1].to_np_array() if i+1 < len(point_list) else point_list[0].to_np_array()
                msp.add_line(s, e,dxfattribs={'color':color_index})
    
    doc.saveas('output.dxf')


def clear_dxf():
    """dxfファイルをクリアする
    """
    doc = ezdxf.new("R2010")
    doc.saveas('output.dxf')

