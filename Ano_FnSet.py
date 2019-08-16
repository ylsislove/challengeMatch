# -*- coding:utf-8 -*-
#
# 不同状态下需要的函数集合
#

from cv_detector.detector import Detector
import Ano_Controller
import threading
# import time


class FnSet:

    def __init__(self):

        self.controller = Ano_Controller.Controller()
        self.command = self.controller.command
        self.detector = Detector()

        # 照片序号
        self.count = 1
        # 日志字典，最后结束的时候，会回显到图像中
        self.log_dict = self.detector.log_dict
        # 无人机当前高度
        self.cur_alt = self.command.get_alt()

    # 记录无人机的动作命令
    def record(self, x, y, l_angle, cur_alt, cmd):
        log_info = list()
        log_info.append([x, y, l_angle])
        log_info.append([cur_alt, cmd])
        self.log_dict[self.count] = log_info
        self.count += 1

    def takeoff(self):
        self.controller.takeoff()
        self.cur_alt = self.command.get_alt()
        tar_alt = 200
        while self.cur_alt < tar_alt:
            self.controller.move_up(tar_alt - self.cur_alt)
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
        self.controller.hover()
        return "search"
    
    def search(self):

        self.controller.is_trace = False

        # 当找到目标时，结束循环
        while True:

            # 检测landmark
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
            x, y, f_angle = self.detector.detect_h()

            # 检测到H，进入追踪小车阶段
            if x is not None:
                self.controller.move(x, y, f_angle, self.cur_alt)
                # 记录命令
                threading.Thread(target=self.record, args=(x, y, f_angle, self.cur_alt,
                                                           self.controller.record_info)).start()

                return "move"

            # 未检测到landmark，且未达到最大高度，控制飞机升高
            elif (self.cur_alt + 10) <= self.controller.max_alt:
                self.controller.move_up(20)

            # 未检测到landmark，超过最大高度10cm，控制飞机下降
            elif self.cur_alt >= self.controller.max_alt + 10:
                self.controller.move_down(20)

            # 未检测到landmark，且在最大高度范围内，转圈搜索
            else:
                self.controller.turn(90)

            # 记录命令
            threading.Thread(target=self.record, args=(x, y, f_angle, self.cur_alt,
                                                       self.controller.record_info)).start()

    # 追踪小车
    def move(self):

        self.controller.is_trace = True
        detect_num = 0

        # 当高度低于30cm，进入一键降落。当连续五次无法检测到H，进入搜索状态
        while True:

            # 检测降落标志
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
            x, y, f_angle = self.detector.detect_h()

            # 若5次未检测到landmark，进入搜索阶段
            if x is None:
                detect_num += 1
                # 记录命令
                threading.Thread(target=self.record, args=(x, y, f_angle, self.cur_alt, "None")).start()
                if detect_num == 5:
                    return "search"
                continue

            else:
                detect_num = 0
                self.controller.move(x, y, f_angle, self.cur_alt)
                # 记录命令
                threading.Thread(target=self.record, args=(x, y, f_angle, self.cur_alt,
                                                           self.controller.record_info)).start()
                if 0 < self.cur_alt <= 40:
                    return "land"

    def land(self):
        self.controller.land()
        return "landed"
