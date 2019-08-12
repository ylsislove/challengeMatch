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
            "search": self.search,      # 搜索
            "move": self.move,          # 追踪
            "land": self.land,          # 降落
        }

    ##############################################################################

    # 起飞
    def takeoff(self):
        print("=============== takeoff ================")
        self.cur_stage = self.fnset.takeoff()

    # 搜索小车
    def search(self):
        print("=============== search ===============")
        self.cur_stage = self.fnset.search()

    # 追踪小车
    def move(self):
        print("=============== move ===============")
        self.cur_stage = self.fnset.move()

    # 降落
    def land(self):
        print("=============== land ===============")
        self.cur_stage = self.fnset.land()
