import ezdxf

# 出力先DXFファイル
output_file_name = "output.dxf"
output_file_path = "./out/" + output_file_name


def draw_line_by_point(point_list, color_index=2):
    """Point型のリストからdxf出力
    Args:
        point_list (list): Point型のリスト
    """
    dxfattribs = {"color": color_index}
    doc = ezdxf.readfile(output_file_path)
    msp = doc.modelspace()
    draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(output_file_path)


# FrameList型
# TODO: Frame内のメソッドとして実装してもいいかも
def draw_line_by_frame_list(frame_list, color_index=2):
    """FrameList型のリストと色指定してdxf出力

    Args:
        frame_list (list): FrameList型のリスト
        color_index (int): 色
    """
    dxfattribs = {"color": color_index}
    doc = ezdxf.readfile(output_file_path)
    msp = doc.modelspace()
    for i in range(len(frame_list)):
        point_list = frame_list[i].points
        draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(output_file_path)


def draw_dxf_by_plan_list(plan_list, color_index=2):
    """PlanList型のリストと色指定してdxf出力

    Args:
        plan_list (list): PlanList型のリスト
        color_index (int): 色
    """
    doc = ezdxf.readfile(output_file_path)
    msp = doc.modelspace()

    dxfattribs = {"color": color_index}

    for plan in plan_list:
        frame_list = plan.get_frame_list()
        for i in range(len(frame_list)):
            # モデル空間に新しいエンティティを作成
            point_list = frame_list[i].points
            draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(output_file_path)


def clear_dxf():
    """dxfファイルをクリアする"""
    doc = ezdxf.new("R2010")
    doc.saveas(output_file_path)


def draw_line_list(msp, point_list, dxfattribs):
    """Draw a line from point_list.

    Args:
        msp (Modelspace): dxfのモデル空間
        point_list ([Point]): Point型のリスト
        dxfattribs (Object): dxfの属性
    """
    for i in range(len(point_list)):
        start_point = point_list[i].to_np_array()
        end_point = point_list[(i + 1) % len(point_list)].to_np_array()
        msp.add_line(start_point, end_point, dxfattribs=dxfattribs)


def draw_line(msp, start, end, dxfattribs):
    """Draw a line from start to end.

    Args:
        msp (Modelspace): dxfのモデル空間
        start (Point): 始点
        end (Point): 終点
        dxfattribs (Object): dxfの属性
    """
    msp.add_line(start.to_np_array(), end.to_np_array(), dxfattribs=dxfattribs)
