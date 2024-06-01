import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import matplotlib

# 出力先DXFファイル
output_dir = "./out/"
output_dxf_file_name = "output.dxf"
output_dxf_img_name = "output.png"


def draw_line_by_point(point_list, color_index=2, dxf_file_name=output_dxf_file_name):
    """Point型のリストからdxf出力
    Args:
        point_list (list): Point型のリスト
    """
    dxfattribs = {"color": color_index}
    dxf_file_path = output_dir + dxf_file_name
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()
    draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(dxf_file_name)


# FrameList型
# TODO: Frame内のメソッドとして実装してもいいかも
def draw_line_by_frame_list(frame_list, color_index=2, dxf_file_name=output_dxf_file_name):
    """FrameList型のリストと色指定してdxf出力

    Args:
        frame_list (list): FrameList型のリスト
        color_index (int): 色
    """
    dxfattribs = {"color": color_index}
    dxf_file_path = output_dir + dxf_file_name
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()
    for i in range(len(frame_list)):
        if frame_list[i] is None:
            continue
        point_list = frame_list[i].points
        draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(dxf_file_path)


def draw_dxf_by_plan_list(plan_list, color_index=2, dxf_file_name=output_dxf_file_name):
    """PlanList型のリストと色指定してdxf出力

    Args:
        plan_list (list): PlanList型のリスト
        color_index (int): 色
    """
    dxf_file_path = output_dir + dxf_file_name
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()

    dxfattribs = {"color": color_index}

    for plan in plan_list:
        frame_list = plan.get_frame_list()
        for i in range(len(frame_list)):
            # モデル空間に新しいエンティティを作成
            point_list = frame_list[i].points
            draw_line_list(msp, point_list, dxfattribs)

    doc.saveas(dxf_file_path)


def clear_dxf(dxf_file_name=output_dxf_file_name):
    """dxfファイルをクリアする"""
    doc = ezdxf.new("R2010")
    dxf_file_path = output_dir + dxf_file_name
    doc.saveas(dxf_file_path)


def create_dxf(new_dxf_file_name):
    doc = ezdxf.new("R2010")
    new_dxf_file_path = output_dir + new_dxf_file_name
    doc.saveas(new_dxf_file_path)


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


def convert_dxf_to_png(dxf_file_name=output_dxf_file_name, output_dxf_img_name=output_dxf_img_name):
    """dxfファイルをpngに変換する

    Args:
        dxf_file_name (_type_, optional): _description_. Defaults to output_dxf_file_name.
        output_dxf_img_name (_type_, optional): _description_. Defaults to output_dxf_img_name.

    Raises:
        ioerror: _description_
        dxf_structure_error: _description_
    """
    try:
        dxf_file_path = output_dir + dxf_file_name
        dxf, auditor = recover.readfile(dxf_file_path)
    except IOError as ioerror:
        print(ioerror)
        raise ioerror
    except ezdxf.DXFStructureError as dxf_structure_error:
        print(dxf_structure_error)
        raise dxf_structure_error

    if not auditor.has_errors:
        output_img_path = output_dir + output_dxf_img_name
        matplotlib.qsave(dxf.modelspace(), output_img_path)
