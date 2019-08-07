# -*- coding:utf-8 -*-
#
# 通过偏差值计算动作指令，一次只能调整一个动作
#

import Ano_Command
# import time


class Controller:

    def __init__(self):

        self.command = Ano_Command.Command()
        self.action = 'no'
        self.speed = 0
        # 飞机在landmark进行微调的临界高度
        self.min_alt = 120
        # 飞机最大高度
        self.max_alt = 220
        # 记录飞机控制命令
        self.record_info = ""

    def record(self, _cmd, _distance, _speed):
        self.record_info = "%s, distance: %d, speed: %d" % (_cmd, _distance, _speed)
        print(self.record_info)

    # 微调最后的位置
    def move_small(self, x_bias, y_bias, angle_bias):
        # 微调landmark_angle
        if 5 < angle_bias:
            self.turn(angle_bias, "small")
        # 微调x偏差
        elif 50 < abs(x_bias):
            self.move_for_x(x_bias, "small")
        # 微调y偏差
        elif 50 < abs(y_bias):
            self.move_for_y(y_bias, "small")
        # 尽量降低飞机飞行高度
        else:
            self.move_down()

    def move(self, x_bias, y_bias, landmark_angle_bias, forward_angle_bias, alt):

        # 若小车位置较远，先调整角度
        if abs(y_bias) > 130 or abs(x_bias) > 130:

            # 若角度偏差在（测试）25度之内，调整角度
            if 15 < abs(forward_angle_bias) <= 25:
                self.turn(forward_angle_bias)

            # 在25度范围之外，调整角度的速度加快一点
            elif 25 < abs(forward_angle_bias) <= 35:
                self.turn(forward_angle_bias, "big")

            # 如果x偏差过大，先控制飞机左移或右移
            elif 130 < abs(x_bias) < 200:
                self.move_for_x(x_bias)

            elif 200 <= abs(x_bias):
                self.move_for_x(x_bias, "big")

            # 其次，y轴方向偏差过大，控制飞机前进或后退
            elif 130 < abs(y_bias) < 200:
                self.move_for_y(y_bias)

            elif 200 <= abs(y_bias):
                self.move_for_y(y_bias, "big")

        # 否则，微调小车的位置偏差
        else:
            # 若landmark角度偏差在（测试）15度之外，调整角度
            if 15 < abs(landmark_angle_bias) < 45:
                self.turn(landmark_angle_bias)

            # 微调x偏差
            elif 70 < abs(x_bias) <= 130:
                self.move_for_x(x_bias)

            # 微调y偏差
            elif 70 < abs(y_bias) <= 130:
                self.move_for_y(y_bias)

            elif alt >= self.min_alt:
                self.move_down()

    # --------------------- 无人机 转向 控制命令 ----------------------

    def turn(self, angle_bias, degree="normal"):

        if degree == "small":
            angle = 5
            speed = 5

        elif degree == "big":
            angle = abs(angle_bias)
            speed = 30

        else:
            angle = 10
            speed = 10

        if angle_bias > 0:
            self.command.setCommand("turnR", angle, speed)
            self.record("turn right", angle, speed)
            # time.sleep(0.1)
        # 控制右转对应的偏角
        elif angle_bias < 0:
            self.command.setCommand("turnL", angle, speed)
            self.record("turn left", angle, speed)
            # time.sleep(0.1)

    # --------------------- 无人机 前进后退 控制命令 ----------------------

    def move_for_y(self, y_bias, degree="normal"):

        if degree == "small":
            distance = 20
            speed = 5

        elif degree == "big":
            distance = 40
            speed = 30

        else:
            distance = 30
            speed = 10

        if y_bias > 0:
            self.command.setCommand("back", distance, speed)
            self.record("go back", distance, speed)
            # time.sleep(0.1)
        elif y_bias < 0:
            self.command.setCommand("forward", distance, speed)
            self.record("go forward", distance, speed)
            # time.sleep(0.1)

    # --------------------- 无人机 左移右移 控制命令 ----------------------

    def move_for_x(self, x_bias, degree="normal"):

        if degree == "small":
            distance = 20
            speed = 5

        elif degree == "big":
            distance = 40
            speed = 20

        else:
            distance = 30
            speed = 10

        if x_bias > 0:
            self.command.setCommand("right", distance, speed)
            self.record("go right", distance, speed)
            # time.sleep(0.1)
        elif x_bias < 0:
            self.command.setCommand("left", distance, speed)
            self.record("go left", distance, speed)
            # time.sleep(0.1)

    # --------------------- 无人机 上升下降 控制命令 ----------------------

    # 获得高度
    def get_alt(self):
        return self.command.get_ALT()

    # 控制飞机上升
    def move_up(self):
        distance = speed = 10
        self.command.setCommand("up", distance, speed)
        self.record("move up", distance, speed)
        # time.sleep(0.1)

    # 控制飞机下降
    def move_down(self):
        distance = speed = 10
        self.command.setCommand("down", distance, speed)
        self.record("move down", distance, speed)
        # time.sleep(0.1)

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

    def trace_car(self, x_bias, y_bias, angle_bias, alt):

        # 若小车位置较远，先调整角度
        if 30 < abs(angle_bias) and (abs(x_bias) > 150 or abs(y_bias) > 150):
            # 小幅度调整角度
            if 30 < abs(angle_bias) < 50:
                self.trace_turn(angle_bias, "small")

            # 中等幅度调整角度
            elif 50 < abs(angle_bias) < 90:
                self.trace_turn(angle_bias)

            # 大幅度调整角度
            elif 90 < abs(angle_bias):
                self.trace_turn(angle_bias, "big")

        # 控制飞机前后移动
        elif 50 < abs(y_bias) <= 70:
            self.move_for_y(y_bias, "small")

        elif 70 < abs(y_bias) <= 130:
            self.move_for_y(y_bias)

        elif 130 < abs(y_bias):
            self.move_for_y(y_bias, "big")

        # 控制飞机左右移动
        elif 50 < abs(x_bias):
            self.move_for_x(x_bias, "small")

        # 控制飞机高度在120cm
        elif alt < 115:
            self.move_up()
        elif alt > 125:
            self.move_down()

        else:
            self.hover()

    def trace_turn(self, angle_bias, degree="normal"):

        if degree == "small":
            angle = 30
            speed = 20

        elif degree == "big":
            angle = abs(angle_bias)
            speed = 60

        else:
            angle = 50
            speed = 40

        # 控制飞机右转对应的偏角
        if angle_bias > 0:
            self.command.setCommand("turnR", angle, speed)
            self.record("turn right", angle, speed)
            # time.sleep(0.1)

        # 控制飞机右转对应的偏角
        elif angle_bias < 0:
            self.command.setCommand("turnL", angle, speed)
            self.record("turn left", angle, speed)
            # time.sleep(0.1)
