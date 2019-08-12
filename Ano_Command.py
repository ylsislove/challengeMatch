# -*- coding:utf-8 -*-
#
# 控制命令集合
#

import Ano_Transmit
import Ano_Receiver
import binascii
import time


class Command:

    def __init__(self):
        self.sender = Ano_Transmit.Sender()
        self.receiver = Ano_Receiver.Receiver()
        self.receiver.start()

    def takeoff(self):
        self.sender.cmd_convert("takeoff", 0, 0)
        self.sender.send_cmd(binascii.a2b_hex(self.sender.append_cmd()))
        # print("command takeoff 函数被调用")

    def land(self):
        self.sender.cmd_convert("land", 0, 0)
        self.sender.send_cmd(binascii.a2b_hex(self.sender.append_cmd()))
        print("------------------ 无人机已降落 ------------------")
        # print("command land 函数被调用")

    def surLand(self):
        self.sender.cmd_convert("surLand", 0, 0)
        self.sender.send_cmd(binascii.a2b_hex(self.sender.append_cmd()))
        # print("command surLand 函数被调用")

    def setCommand(self, msg, cmd2, cmd3):
        self.sender.cmd_convert(msg, cmd2, cmd3)
        self.sender.send_cmd(binascii.a2b_hex(self.sender.append_cmd()))
        # print("command %s 函数被调用, distance: %d, speed: %d" % (msg, cmd2, cmd3))

    def hover_takeoff(self):
        self.sender.hover_takeoff()

    def hover(self):
        self.sender.hover()

    def get_alt(self):
        return self.receiver.receive()

    def close_receiver(self):
        self.receiver.close_receiver()


if __name__ == "__main__":
    test = Command()
    count = 0
    try:
        while True:
            print(test.get_alt())
            count += 1
    except KeyboardInterrupt:
        test.close_receiver()
