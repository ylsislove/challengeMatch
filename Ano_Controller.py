# -*- coding:utf-8 -*-
#
# 通过偏差值计算动作指令，一次只能调整一个动作
#

import Ano_Command
# import time
import math


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
        self.proportion = math.tan(45 * math.pi / 180)
        # 分辨率长边的一半
        self.height_half = 424

        # PID算法
        self.Kp_move = 0.6
        self.Kp_angle = 0.5

    def record(self, _cmd, _distance, _speed):
        self.record_info = "%s, distance: %d, speed: %d" % (_cmd, _distance, _speed)
        print(self.record_info)

    # 微调最后的位置
    def move_small(self, x_bias, y_bias, angle_bias, alt):

        # 像素距离转化为实际距离
        x_bias = round(alt * (self.proportion - 0.2) / self.height_half * x_bias)
        y_bias = round(alt * (self.proportion - 0.2) / self.height_half * y_bias) - 4

        # 微调landmark_angle
        if 5 < angle_bias:
            self.turn(angle_bias)

        # 微调x偏差
        elif 10 < abs(x_bias):
            self.move_for_x(x_bias)

        # 微调y偏差
        elif 10 < abs(y_bias):
            self.move_for_y(y_bias)

        # 尽量降低飞机飞行高度
        else:
            self.move_down()

    def move(self, x_bias, y_bias, l_angle_bias, f_angle_bias, alt):

        # 像素距离转化为实际距离
        x_bias = round(alt * (self.proportion - 0.1) / self.height_half * x_bias)
        y_bias = round(alt * (self.proportion - 0.1) / self.height_half * y_bias)

        if abs(x_bias) < 40 and abs(y_bias) < 40:

            if 20 < abs(x_bias):
                self.move_for_x(x_bias)

            elif 20 < abs(y_bias):
                self.move_for_y(y_bias)

            elif 8 < abs(l_angle_bias):
                self.turn(l_angle_bias)

            else:
                self.move_down()

        else:
            if 20 < abs(f_angle_bias):
                self.turn(f_angle_bias)

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
    def move_up(self):
        distance = speed = 10
        self.command.setCommand("up", distance, speed)
        self.record("move up", distance, speed)

    # 控制飞机下降
    def move_down(self):
        distance = speed = 10
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

    # ------------------------ 追踪小车的主要控制函数 ------------------------

    def trace_car(self, x_bias, y_bias, l_angle_bias, f_angle_bias, alt):

        # 像素距离转化为实际距离
        x_bias = round(alt * self.proportion / self.height_half * x_bias)
        y_bias = round(alt * self.proportion / self.height_half * y_bias)

        if abs(x_bias) < 40 and abs(y_bias) < 40:

            if 15 < abs(x_bias):
                self.move_for_x(x_bias)

            elif 15 < abs(y_bias):
                self.move_for_y(y_bias)

            else:
                self.turn(l_angle_bias)

        else:
            if 15 <= abs(f_angle_bias):
                self.turn(f_angle_bias)

            else:
                self.move_for_y(y_bias)
