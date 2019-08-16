# -*- coding:utf-8 -*-
#
# 通过偏差值计算动作指令，一次只能调整一个动作
#

import Ano_Command
import threading
import time


class Controller:

    def __init__(self):

        self.command = Ano_Command.Command()
        self.action = 'no'
        self.speed = 0
        # 飞机在landmark进行微调的临界高度
        self.min_alt = 100
        # 飞机最大高度
        self.max_alt = 200
        # 记录飞机控制命令
        self.record_info = ""

        # 像素距离与实际距离转换的比例
        # self.proportion = math.tan(45 * math.pi / 180)
        # 分辨率长边的一半
        # self.height_half = 424
        self.height_half = 320

        # PID算法
        self.Kp_move = 0.55
        self.Kp_angle = 0.5

        # 无人机已跟踪的时间
        self.trace_time = 0
        # 是否记录跟踪时间
        self.is_trace = False
        # 规定的跟踪时间
        self.normal_trace_time = 30

        # 开启时间子线程
        t = threading.Thread(target=self.recode_time, args=())
        t.setDaemon(True)
        t.start()

    # 记录无人机已追踪的时间
    def recode_time(self):
        while True:
            cur_time = time.time()
            while self.is_trace:
                continue
            delta_time = (time.time() - cur_time)
            if delta_time > 0.01:
                self.trace_time += delta_time
            # print("trace_time:", self.trace_time)

    def record(self, _cmd, _distance, _speed):
        self.record_info = "%s, distance: %d, speed: %d" % (_cmd, _distance, _speed)
        print(self.record_info)

    def move(self, x_bias, y_bias, f_angle, alt):

        # 像素距离转化为实际距离
        x_bias = round(alt / self.height_half * x_bias)
        y_bias = round(alt / self.height_half * y_bias) - 10

        if abs(x_bias) < 40 and abs(y_bias) < 40:

            if self.trace_time >= self.normal_trace_time:
                print("降落")
                self.move_down(40)

            else:
                self.hover()

        elif abs(x_bias) <= 60 and abs(y_bias) <= 60:

            if abs(x_bias) >= 30:
                self.move_for_x(x_bias)

            else:
                self.move_for_y(y_bias)

        else:
            if abs(f_angle) >= 15:
                self.turn(f_angle)

            else:
                self.move_for_y(y_bias)

    # --------------------- 无人机 转向 控制命令 ----------------------

    def turn(self, angle_bias):

        angle = abs(angle_bias)
        speed = round(angle * self.Kp_angle)

        if angle_bias > 0:
            self.command.setCommand("turnR", angle, speed)
            self.record("turn right", angle, speed)

        # 控制右转对应的偏角
        elif angle_bias < 0:
            self.command.setCommand("turnL", angle, speed)
            self.record("turn left", angle, speed)

    # --------------------- 无人机 前进后退 控制命令 ----------------------

    def move_for_y(self, y_bias):

        distance = abs(y_bias)
        speed = round(distance * self.Kp_move)

        if y_bias > 0:
            self.command.setCommand("back", distance, speed)
            self.record("go back", distance, speed)

        elif y_bias < 0:
            self.command.setCommand("forward", distance, speed)
            self.record("go forward", distance, speed)

    # --------------------- 无人机 左移右移 控制命令 ----------------------

    def move_for_x(self, x_bias):

        distance = abs(x_bias)
        speed = round(distance * self.Kp_move)

        if x_bias > 0:
            self.command.setCommand("right", distance, speed)
            self.record("go right", distance, speed)

        elif x_bias < 0:
            self.command.setCommand("left", distance, speed)
            self.record("go left", distance, speed)

    # --------------------- 无人机 上升下降 控制命令 ----------------------

    # 控制飞机上升
    def move_up(self, z_bias):

        distance = z_bias
        speed = round(distance * self.Kp_move)

        self.command.setCommand("up", distance, speed)
        self.record("move up", distance, speed)

    # 控制飞机下降
    def move_down(self, z_bias):

        distance = z_bias
        speed = round(distance * self.Kp_move)

        self.command.setCommand("down", distance, speed)
        self.record("move down", distance, speed)

    # --------------------- 无人机 一键式操作 控制命令 ----------------------

    # 控制飞机悬停
    def hover(self):
        self.command.hover()
        self.record("hover", 0, 0)

    # 一键起飞
    def takeoff(self):
        self.command.takeoff()
        self.record("takeoff", 0, 0)

    # 一键降落
    def land(self):
        self.command.land()
        self.record("land", 0, 0)
