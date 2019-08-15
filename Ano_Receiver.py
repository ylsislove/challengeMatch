# -*- coding:utf-8 -*-
#
# 获取无人机的数据
#

import Ano_Base
import binascii
import re


class Receiver:

    def __init__(self):

        super().__init__()

        self.base = Ano_Base.Base()

        # 帧头AA  发送设备05(拓空者飞控)  目标设备AF(上位机)
        self.data_hex = 'aa05af'

        # 姿态等基本信息，功能字：01，长度：12Byte
        self.posture_fun_len = '010c'

        # 传感器数据，功能字：02，长度：18Byte
        self.sensor_fun_len = '0212'

        # 控制数据，功能字：03，长度：20Byte
        self.control_fun_len = '0314'

        # 板载气压计高度、附加测高传感器、传感器温度
        self.alt_addition_fun_len = '070a'

        # 姿态等基本信息变量
        # 机头为X正，左侧为Y正，Z方向满足笛卡尔直角坐标
        # 北为X正，西为Y正，天为Z正
        self.ROL = 0    # 以X轴为轴转动偏角
        self.PIT = 0    # 以Y轴为轴转动偏角
        self.YAW = 0    # 以Z轴为轴转动偏角
        self.ALT_USE = 0    # 高度(cm)    ！不准确
        self.FLY_MODEL = 0  # 飞行模式
        self.ARMED = 0      # 飞控是否解锁

        # 传感器数据
        self.ACC_X = 0
        self.ACC_Y = 0
        self.ACC_Z = 0
        self.GYRO_X = 0
        self.GYRO_Y = 0
        self.GYRO_Z = 0
        self.MAG_X = 0
        self.MAG_Y = 0
        self.MAG_Z = 0

        # 控制数据
        self.ctrl_THR = 0
        self.ctrl_YAW = 0
        self.ctrl_ROL = 0
        self.ctrl_PIT = 0
        self.AUX1 = 0
        self.AUX2 = 0
        self.AUX3 = 0
        self.AUX4 = 0
        self.AUX5 = 0
        self.AUX6 = 0

        # 其他重要信息
        self.ALT_BAR = 0    # 板载气压计高度，精确到0.01
        self.ALT_ADDITION = 0   # 附加测高传感器，精确到0.01
        self.SEN_TMP = 0    # 传感器温度，精确到0.01

        self.pattern = re.compile("(.*?aa05af070a(.*?))aa05af", re.IGNORECASE)

    # 清空缓冲区
    def clear(self):
        self.base.port.flushInput()

    # 接收
    def receive(self):
        self.clear()
        while True:
            if self.base.port.inWaiting() > 0:
                # 十六进制转换binascii.b2a_hex()
                data_str = binascii.b2a_hex(self.base.port.read(200)).decode('utf-8')
                # 是否有高度信息
                if self.pattern.search(data_str) is not None:
                    match = self.pattern.search(data_str)
                    data = match.group(2)
                    try:
                        alt = int(data[8:16], 16)
                        if 0 < alt < 500:
                            return alt
                    except ValueError:
                        pass

    # 解析姿态等信息
    def parse_posture_info(self, data):
        data = data[len(self.posture_fun_len):]
        # print('posture_info: '+data)
        self.ROL = int(data[:4], 16) / 100
        self.PIT = int(data[4:8], 16) / 100
        self.YAW = int(data[8:12], 16) / 100
        self.ALT_USE = int(data[12:20], 16)
        self.FLY_MODEL = int(data[20:22], 16)
        self.ARMED = int(data[22:24], 16)

    # 解析传感器
    def parse_sensor_info(self, data):
        data = data[len(self.sensor_fun_len):]
        # print('sensor_info:' + data)
        self.ACC_X = int(data[:4], 16)
        self.ACC_Y = int(data[4:8], 16)
        self.ACC_Z = int(data[8:12], 16)
        self.GYRO_X = int(data[12:16], 16)
        self.GYRO_Y = int(data[16:20], 16)
        self.GYRO_Z = int(data[20:24], 16)
        self.MAG_X = int(data[24:28], 16)
        self.MAG_Y = int(data[28:32], 16)
        self.MAG_Z = int(data[32:36], 16)

    # 解析控制数据信息
    def parse_control_info(self, data):
        data = data[len(self.control_fun_len):]
        # print('control_info:' + data)
        self.ctrl_THR = int(data[:4], 16)
        self.ctrl_YAW = int(data[4:8], 16)
        self.ctrl_ROL = int(data[8:12], 16)
        self.ctrl_PIT = int(data[12:16], 16)
        self.AUX1 = int(data[16:20], 16)
        self.AUX2 = int(data[20:24], 16)
        self.AUX3 = int(data[24:28], 16)
        self.AUX4 = int(data[28:32], 16)
        self.AUX5 = int(data[32:36], 16)
        self.AUX6 = int(data[36:40], 16)

    # 解析板载气压计高度、附加测高传感器、传感器温度
    def parse_alt_addition_info(self, data):
        data = data[len(self.alt_addition_fun_len):]
        # print('alt_addition_info:' + data)
        self.ALT_BAR = int(data[:8], 16)
        self.ALT_ADDITION = int(data[8:16], 16)
        self.SEN_TMP = int(data[16:20], 16)
