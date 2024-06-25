class Plan:

    # プランを作成する
    def __init__(self, frame_list):
        self.frame_list = frame_list
        self.frame_count = len(frame_list)

    def move_plan(self, move_point):
        for i in range(len(self.frame_list)):
            self.frame_list[i].move_frame(move_point)

    def get_frame_list(self):
        return self.frame_list

    def get_plan_str(self):
        str = "plan:\n"
        for i in range(len(self.frame_list)):
            if i < 5:
                str = f"{str} {self.frame_list[i].get_points_str()} \n"
        return str
