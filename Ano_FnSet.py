# -*- coding:utf-8 -*-
#
# 不同状态下需要的函数集合
#

from cv_detector.detector import Detector
import Ano_Controller
import threading
import time


class FnSet:

    def __init__(self):

        self.controller = Ano_Controller.Controller()
        self.command = self.controller.command
        self.detector = Detector()

        # 照片序号
        self.count = 1
        # 当前模式
        self.cur_mode = ""
        # 目标模式
        self.tar_mode = ""
        # 日志字典，最后结束的时候，会回显到图像中
        self.log_dict = self.detector.log_dict

        # 无人机当前高度
        self.cur_alt = self.command.get_alt()

        self.search_time = 0
        self.search_count = 0
        self.move2qr_time = 0
        self.move2qr_count = 0
        self.landmark_time = 0
        self.landmark_count = 0

    # 检测当前飞机状态
    def check_stage(self):
        # 当前激光测距高度是10cm左右，则返回无人机状态为将要起飞状态
        if 5 <= self.cur_alt <= 15:
            return "takeoff"
        elif 15 < self.cur_alt <= self.controller.max_alt:
            return "search"
        else:
            return "None"

    # 记录无人机的动作命令
    def record(self, x, y, l_ag, f_ag, cur_alt, cur_mode, cmd):
        log_info = list()
        log_info.append([x, y, l_ag, f_ag])
        log_info.append([cur_alt, cur_mode])
        log_info.append([cmd])
        self.log_dict[self.count] = log_info
        self.count += 1

    def takeoff(self):
        self.controller.takeoff()
        self.cur_alt = self.command.get_alt()
        tar_alt = 150
        while self.tar_mode == self.cur_mode and self.cur_alt < tar_alt:
            self.controller.move_up(tar_alt - self.cur_alt)
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
        self.controller.hover()
        return "search"
    
    def search(self):

        self.cur_alt = self.command.get_alt()
        while self.tar_mode == self.cur_mode and self.cur_alt < self.controller.min_alt:
            self.controller.move_up(self.controller.min_alt - self.cur_alt)
            self.cur_alt = self.command.get_alt()

        t = time.time()

        # 当当前模式等于目标模式的时候，进行循环
        while self.tar_mode == self.cur_mode:

            new_time = time.time()
            self.search_time += (new_time - t)
            t = time.time()

            # 检测landmark
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
            x, y, l_ag, f_ag = self.detector.detect_landmark()
            # x, y, l_ag, f_ag = self.detector.detect_qr()

            # 检测到landmark，进入追踪小车阶段
            if x is not None:
                self.controller.move(x, y, l_ag, f_ag, self.cur_alt)
                # 记录命令
                threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                           self.cur_alt, self.cur_mode,
                                                           self.controller.record_info)).start()

                new_time = time.time()
                self.search_time += (new_time - t)
                self.search_count += 1

                return "move2qr"

            # 未检测到landmark，且未达到最大高度，控制飞机升高
            elif (self.cur_alt + 10) <= self.controller.max_alt:
                self.controller.move_up(10)

            # 未检测到landmark，超过最大高度10cm，控制飞机下降
            elif self.cur_alt >= self.controller.max_alt + 10:
                print("Warning! Warning! Warning!")
                self.controller.move_down(20)

            # 未检测到landmark，且在最大高度范围内，转圈搜索
            else:
                self.controller.turn(-30)

            # 记录命令
            threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                       self.cur_alt, self.cur_mode,
                                                       self.controller.record_info)).start()
            self.search_count += 1

    # 追踪小车
    def move2qr(self):

        t = time.time()
        detect_num = 0
        # 当当前模式等于目标模式的时候，进行循环
        while self.tar_mode == self.cur_mode:

            new_time = time.time()
            self.move2qr_time += (new_time - t)
            t = time.time()

            # 检测降落标志
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
            x, y, l_ag, f_ag = self.detector.detect_landmark()
            # x, y, l_ag, f_ag = self.detector.detect_qr()

            # 若5次未检测到landmark，进入搜索阶段
            if x is None:
                detect_num += 1
                # 记录命令
                threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                           self.cur_alt, self.cur_mode,
                                                           None)).start()
                if detect_num == 5:

                    new_time = time.time()
                    self.move2qr_time += (new_time - t)
                    self.move2qr_count += 1
                    return "search"

                self.move2qr_count += 1
                continue

            detect_num = 0

            if self.cur_mode == "trace":
                self.controller.trace_car(x, y, l_ag, f_ag, self.cur_alt)

            else:
                self.controller.move(x, y, l_ag, f_ag, self.cur_alt)

            # 记录命令
            threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                       self.cur_alt, self.cur_mode,
                                                       self.controller.record_info)).start()

            if self.cur_mode == "normal" and (0 < self.cur_alt < self.controller.min_alt):
                new_time = time.time()
                self.move2qr_time += (new_time - t)
                self.move2qr_count += 1
                return "landmark"

            self.move2qr_count += 1

    # 着陆前的微调
    def landmark(self):

        t = time.time()
        detect_num = 0
        self.cur_alt = self.command.get_alt()
        x = y = 0
        # 当当前模式等于目标模式的时候，进行循环
        while self.tar_mode == self.cur_mode and (self.cur_alt > 30 or abs(x) > 8 or abs(y) > 8):

            new_time = time.time()
            self.landmark_time += (new_time - t)
            t = time.time()

            # 检测降落标志
            self.cur_alt = self.command.get_alt()
            print("alt:", self.cur_alt)
            x, y, l_ag, f_ag = self.detector.detect_landmark()
            # x, y, l_ag, f_ag = self.detector.detect_qr()

            # 若5次未检测到landmark，进入搜索阶段
            if x is None:
                detect_num += 1
                threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                           self.cur_alt, self.cur_mode,
                                                           None)).start()

                x = y = 100
                if detect_num == 5:
                    new_time = time.time()
                    self.landmark_time += (new_time - t)
                    self.landmark_count += 1
                    return "search"

                self.landmark_count += 1
                continue

            # 若在正上方，直接降落
            # if self.cur_alt < 65 and abs(x) <= 30 and abs(y) <= 30:
            #     threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
            #                                                self.cur_alt, self.cur_mode,
            #                                                "land")).start()
            #     new_time = time.time()
            #     self.landmark_time += (new_time - t)
            #     self.landmark_count += 1
            #     return "land"

            # 否则进行微调
            else:
                detect_num = 0
                x, y = self.controller.move_small(x, y, l_ag, self.cur_alt)
                threading.Thread(target=self.record, args=(x, y, l_ag, f_ag,
                                                           self.cur_alt, self.cur_mode,
                                                           self.controller.record_info)).start()

            self.cur_alt = self.command.get_alt()

            self.landmark_count += 1

        return "land"

    def land(self):
        print("search_time：", self.search_time)
        print("search_count：", self.search_count)
        print("move2qr_time：", self.move2qr_time)
        print("move2qr_count：", self.move2qr_count)
        print("landmark_time：", self.landmark_time)
        print("landmark_count：", self.landmark_count)
        self.controller.land()
        return "landed"
