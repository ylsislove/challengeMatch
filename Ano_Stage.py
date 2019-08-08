# -*- coding:utf-8 -*-
#
# 无人机的不同状态集合，根据状态的不同调用fnset中相应的函数
#

import Ano_FnSet


class Stage:

    def __init__(self):

        self.cur_stage = "takeoff"  # 初始takeoff
        self.fnset = Ano_FnSet.FnSet()

        self.switch = {
            "takeoff": self.takeoff,    # 起飞
            "search": self.search,      # 搜索二维码
            "move2qr": self.move2qr,    # 追踪二维码
            "landmark": self.landmark,  # H标识
            "land": self.land,      # 降落
        }

    ##############################################################################

    # 检查无人机当前状态
    def check_stage(self):
        print("=============== check stage ================")
        return self.fnset.check_stage()

    # 起飞
    def takeoff(self):
        print("=============== takeoff ================")
        self.cur_stage = self.fnset.takeoff()

    # 搜索二维码
    def search(self):
        print("=============== search qr ===============")
        self.cur_stage = self.fnset.search()

    # 追踪小车
    def move2qr(self):
        print("=============== move to qr ===============")
        self.cur_stage = self.fnset.move2qr()

    # 降落点悬停
    def landmark(self):
        print("=============== landmark ===============")
        self.cur_stage = self.fnset.landmark()

    # 降落
    def land(self):
        print("=============== land ===============")
        self.cur_stage = self.fnset.land()

