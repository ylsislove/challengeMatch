# -*- coding:utf-8 -*-
#
# 不同状态下需要的函数集合
#

from cv_detector.detector import Detector
import Ano_Controller
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

        self.search_time = 0
        self.search_count = 0
        self.move2qr_time = 0
        self.move2qr_count = 0
        self.landmark_time = 0
        self.landmark_count = 0

    # 检测当前飞机状态
    def check_stage(self):
        alt = self.controller.get_alt()
        # 当前激光测距高度是10cm左右，则返回无人机状态为将要起飞状态
        if 5 <= alt <= 15:
            return "takeoff"
        elif 15 < alt < self.controller.max_alt:
            return "search"
        else:
            return "None"

    # 获得当前高度值，并显示在屏幕上
    def get_alt_and_show(self, counted=False):
        alt = self.controller.get_alt()
        if counted is False:
            print("ALT: ", alt)
        else:
            print(self.count, "ALT: ", alt)
        return alt

    # 记录无人机的动作命令
    def record(self, x, y, l_ag, f_ag, cur_alt, cmd):
        log_info = list()
        log_info.append([x, y, l_ag, f_ag])
        log_info.append([cur_alt, self.cur_mode])
        log_info.append([cmd])
        self.log_dict[self.count] = log_info
        self.count += 1

    def takeoff(self):
        self.controller.takeoff()
        cur_alt = self.get_alt_and_show()
        tar_alt = 150
        while self.tar_mode == self.cur_mode and cur_alt < tar_alt:
            self.controller.move_up()
            cur_alt = self.controller.get_alt()
            print("alt:", cur_alt)
        return "search"
    
    def search(self):

        t = time.time()

        # 当当前模式等于目标模式的时候，进行循环
        while self.tar_mode == self.cur_mode:

            new_time = time.time()
            self.search_time += (new_time - t)
            t = time.time()

            # 检测landmark
            alt = self.get_alt_and_show(True)
            x, y, l_ag, f_ag = self.detector.detect_landmark(alt)

            # 检测到landmark，进入追踪小车阶段
            if x is not None:
                print("x_bias: ", x, " y_bias: ", y, " landmark_angle: ", l_ag, "forward_angle: ", f_ag)
                self.controller.move(x, y, l_ag, f_ag, alt)
                # 记录命令
                self.record(x, y, l_ag, f_ag, alt, self.controller.record_info)

                new_time = time.time()
                self.search_time += (new_time - t)
                self.search_count += 1

                return "move2qr"

            # 未检测到landmark，且未达到最大高度，控制飞机升高
            elif (alt + 10) <= self.controller.max_alt:
                self.controller.move_up()

            # 未检测到landmark，超过最大高度10cm，控制飞机下降
            elif alt >= self.controller.max_alt + 10:
                print("Warning! Warning! Warning!")
                self.controller.move_down()

            # 未检测到landmark，且在最大高度范围内，转圈搜索
            else:
                self.controller.turn(-30, "big")
                # time.sleep(0.5)

            # 记录命令
            self.record(x, y, l_ag, f_ag, alt, self.controller.record_info)

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
            alt = self.get_alt_and_show(True)
            x, y, l_ag, f_ag = self.detector.detect_landmark(alt)

            # 若5次未检测到landmark，进入搜索阶段
            if x is None:
                detect_num += 1
                # 记录命令
                self.record(x, y, l_ag, f_ag, alt, None)
                if detect_num == 5:

                    new_time = time.time()
                    self.move2qr_time += (new_time - t)
                    self.move2qr_count += 1
                    return "search"

                self.move2qr_count += 1
                continue

            detect_num = 0
            print("mode:", self.cur_mode,
                  "x_bias:", x, "y_bias:", y,
                  "landmark_angle:", l_ag,
                  "forward_angle:", f_ag)

            if self.cur_mode == "trace":
                self.controller.trace_car(x, y, f_ag, alt)

            else:
                self.controller.move(x, y, l_ag, f_ag, alt)

            # 记录命令
            self.record(x, y, l_ag, f_ag, alt, self.controller.record_info)

            if self.cur_mode == "normal" and 0 < alt < self.controller.min_alt:
                new_time = time.time()
                self.move2qr_time += (new_time - t)
                self.move2qr_count += 1
                return "landmark"

            self.move2qr_count += 1

    # 着陆前的微调
    def landmark(self):

        t = time.time()
        detect_num = 0
        alt = self.controller.get_alt()
        x = y = 0
        # 当当前模式等于目标模式的时候，进行循环
        while self.tar_mode == self.cur_mode and alt > 30 or abs(x) > 30 or abs(y) > 30:

            new_time = time.time()
            self.landmark_time += (new_time - t)
            t = time.time()

            # 检测降落标志
            alt = self.get_alt_and_show(True)
            x, y, l_ag, f_ag = self.detector.detect_landmark(alt)

            # 若5次未检测到landmark，进入搜索阶段
            if x is None:
                detect_num += 1
                self.record(x, y, l_ag, f_ag, alt, None)
                x = y = 100
                if detect_num == 5:
                    new_time = time.time()
                    self.landmark_time += (new_time - t)
                    self.landmark_count += 1
                    return "search"

                self.landmark_count += 1
                continue

            detect_num = 0
            print("mode:", self.cur_mode,
                  "x_bias:", x, "y_bias:", y,
                  "landmark_angle:", l_ag,
                  "forward_angle:", f_ag)

            # 若在正上方，直接降落
            if alt < 65 and abs(x) <= 30 and abs(y) <= 30:
                self.record(x, y, l_ag, f_ag, alt, "land")
                new_time = time.time()
                self.landmark_time += (new_time - t)
                self.landmark_count += 1
                return "land"

            # 否则进行微调
            else:
                self.controller.move_small(x, y, l_ag)
                self.record(x, y, l_ag, f_ag, alt, self.controller.record_info)

            alt = self.controller.get_alt()

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
