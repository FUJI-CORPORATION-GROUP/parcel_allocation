from frame import Frame

class Plan:
  
  frame_list = []
  
  # プランを作成する
  def __init__(self, frame_list):
    self.frame_list = frame_list
  
  def move_plan(self, move_point):
    for i in range(len(self.frame_list)):
      self.frame_list[i].move_frame(move_point)
    return self
  
  def get_frame_list(self):
    return self.frame_list
