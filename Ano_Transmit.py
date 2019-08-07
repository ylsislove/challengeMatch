# -*- coding:utf-8 -*-
#
# 向无人机发送命令
#

import Ano_Base
import time

class Sender:

    def __init__(self):

        self.base = Ano_Base.Base()

        # 帧头AA  发送设备AF(上位机)  目标设备05(拓空者飞控)
        self.data_hex = 'AAAF05'

        # 飞行控制单次控制，功能字：E0，长度：11Byte，模式：10
        self.ctrl_fun_len_model = 'E00B10'

        # 动作指令
        self.cmd1 = '0000'  # 动作类别
        self.cmd2 = 0  # 高度(cm)，距离(cm)，角度(deg)
        self.cmd3 = 0  # 速度(cm/s)
        self.cmd4 = 0  # 固定位0
        self.cmd5 = 0  # 固定位0

        self.hovr_takeoff = [0xAA, 0xAF, 0x05, 0x03, 0x14, 0x05, 0xBC, 0x05, 0xBC, 0x05, 0xBC, 0x05, 0xBC, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]
        self.hovr = [0xAA, 0xAF, 0x05, 0xE0, 0x0B, 0x10, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                     0x5E]

    # 发送控制指令
    def send_cmd(self, cmd):
        time.sleep(0.01)  # 每隔10ms发送一次数据
        try:
            self.base.port.write(cmd)
        except (OSError, serial.SerialException, serial.SerialTimeoutException):
            print('channel Except error')

    # 悬停
    def hover(self):
        self.base.port.write(self.hovr)
        time.sleep(0.01)

    # 起飞用悬停
    def hover_takeoff(self):
        self.base.port.write(self.hovr_takeoff)
        time.sleep(0.01)

    # 十进制整型转换为十六进制字符串(两个Byte)
    def hex_to_str(self, num):
        num = str(hex(num))[2:]
        return (4 - len(num)) * '0' + num

    # 通道值传输的校验位
    def add_hex_cmd(self):
        temp = 0
        self.hex = []
        self.hex.append(self.data_hex)
        self.hex.append(self.ctrl_fun_len_model)
        self.hex.append(self.cmd1)
        self.hex.append(self.hex_to_str(self.cmd2))
        self.hex.append(self.hex_to_str(self.cmd3))
        # print(self.hex)
        for i in self.hex:
            for j in range(0, len(str(i)), 2):
                temp += int(str(i)[j : j+2], 16)
        return str(hex(temp)[-2:])

    # 待发送的十六进制命令数据
    def append_cmd(self):
        # print(self.data_hex + self.ctrl_fun_len_model + self.cmd1 \
        #        + self.hex_to_str(self.cmd2) + self.hex_to_str(self.cmd3) \
        #        + self.hex_to_str(self.cmd4) + self.hex_to_str(self.cmd5) \
        #        + self.add_hex_cmd())
        return self.data_hex + self.ctrl_fun_len_model + self.cmd1 \
               + self.hex_to_str(self.cmd2) + self.hex_to_str(self.cmd3) \
               + self.hex_to_str(self.cmd4) + self.hex_to_str(self.cmd5) \
               + self.add_hex_cmd()

    # 飞行指令
    def cmd_convert(self, msg, cmd2, cmd3):
        # 指令
        if (msg == "takeoff"):
            self.cmd1 = "0001"
        elif (msg == "land"):
            self.cmd1 = "0002"
        elif (msg == "up"):
            self.cmd1 = "0003"
        elif (msg == "down"):
            self.cmd1 = "0004"
        elif (msg == "forward"):
            self.cmd1 = "0005"
        elif (msg == "back"):
            self.cmd1 = "0006"
        elif (msg == "left"):
            self.cmd1 = "0007"
        elif (msg == "right"):
            self.cmd1 = "0008"
        elif (msg == "turnL"):
            self.cmd1 = "0009"
        elif (msg == "turnR"):
            self.cmd1 = "000A"
        elif (msg == "surLand"):
            self.cmd1 = "00A0"

        self.cmd2 = cmd2    # 高度(cm)，距离(cm)，角度(deg)
        self.cmd3 = cmd3    # 速度(cm/s)

