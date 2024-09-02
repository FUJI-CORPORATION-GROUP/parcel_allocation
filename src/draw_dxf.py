import datetime
import os
import shutil
import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import matplotlib
import inspect


# 出力先DXFファイル
output_dir = "./out/"
output_dxf_file_name = "output.dxf"
output_dxf_img_name = "output.png"


def draw_line_by_point(point_list, color_index=3, dxf_file_name=output_dxf_file_name):
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
def draw_line_by_frame_list(frame_list, color_index=3, dxf_file_name=output_dxf_file_name):
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


def draw_dxf_by_plan_list(plan_list, target_frame=None, color_index=3, dxf_file_name=output_dxf_file_name):
    """PlanList型のリストと色指定してdxf出力

    Args:
        plan_list (list): PlanList型のリスト
        color_index (int): 色
    """
    dxf_file_path = output_dir + dxf_file_name
    doc = ezdxf.readfile(dxf_file_path)
    msp = doc.modelspace()

    dxfattribs = {"color": color_index}


    # 基準となるtarget_flameの描写
    if target_frame is not None:
        point_list = target_frame.points
        draw_line_list(msp, point_list, dxfattribs)

    for plan in plan_list:
        frame_list = plan.get_frame_list()
        for i in range(len(frame_list)):
            # モデル空間に新しいエンティティを作成
            point_list = frame_list[i].points
            # print(type(frame_list[i]))
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


def debug_png_by_plan_list(plan_list, file_name):
    """dxfファイルをpngに変換するデバッグ用"""
    date = datetime.datetime.now().strftime("%m%d-%H%M-%S.%f")[:-3]
    caller_name = f" from {inspect.stack()[1].function}"
    new_dxf_name = date + " " + file_name + caller_name + ".dxf"
    new_png_name = date + " " + file_name + caller_name + ".png"
    create_dxf(new_dxf_name)
    draw_dxf_by_plan_list(plan_list, None, 2, new_dxf_name)
    convert_dxf_to_png(new_dxf_name, new_png_name)
    os.remove(output_dir + new_dxf_name)


def debug_png_by_frame_list(frame_list, file_name, target_flame=None):
    """dxfファイルをpngに変換するデバッグ用"""
    
    date = datetime.datetime.now().strftime("%m%d-%H%M-%S.%f")[:-3]
    caller_name = f" from {inspect.stack()[1].function}"
    new_dxf_name = date + " " + file_name + caller_name + ".dxf"
    new_png_name = date + " " + file_name + caller_name + ".png"
    create_dxf(new_dxf_name)

    # 基準となるtarget_flameの描写
    if target_flame is not None:
        draw_line_by_frame_list(target_flame, 7, new_dxf_name)

    draw_line_by_frame_list(frame_list, 2, new_dxf_name)
    convert_dxf_to_png(new_dxf_name, new_png_name)
    os.remove(output_dir + new_dxf_name)


def delete_output_files():
    """出力ファイルを削除する"""
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)
