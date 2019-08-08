# -*- coding:utf-8 -*-
#
# 向无人机发送命令
#


from threading import Thread
from socket import *
import traceback
import Ano_Mode
import signal
import time
import sys


class AnoDrone:

    def __init__(self):
        self.mode = Ano_Mode.Mode()
        self.is_exit = False

        self.addr = ("192.168.4.1", 5210)
        self.ano_sock = socket(AF_INET, SOCK_STREAM)

        self.ano_sock_thread = Thread(target=self.receive_data, args=())
        self.ano_sock_thread.setDaemon(True)

        # 当前模式，目标模式。当二者不匹配时，进行模式切换
        self.cur_mode = ""
        self.tar_mode = ""

        # 手动控制模式，命令集合
        self.control_cmd_list = ["takeoff", "land", "up", "down", "forward", "back",
                                 "left", "right", "turnL", "turnR", "surLand"]
        # 手动控制模式，缓冲列表
        self.control_buf_list = []

        # 当前飞机状态
        self.cur_stage = "takeoff"

    # --------------------------- 主线程，主循环函数 ---------------------------

    def main_process(self):

        is_connect = False
        # 建立连接
        while not is_connect:
            try:
                self.ano_sock.connect(self.addr)
                is_connect = True
            except ConnectionRefusedError:
                print("连接小车失败...5秒后重试")
                time.sleep(5)

        data = self.ano_sock.recv(1024).decode("utf-8")
        print("(192.168.4.1) Car:", data)

        # 启动子线程用来接收小车命令
        self.ano_sock_thread.start()

        while not self.is_exit:

            if self.tar_mode == "control":
                self.cur_mode = "control"
                self.mode.stage.fnset.cur_mode = ""
                # 无人机进入手动控制模式
                while self.tar_mode == self.cur_mode:
                    if len(self.control_buf_list) > 0:
                        for msg in self.control_buf_list:
                            self.mode.control(msg)
                        self.control_buf_list.clear()
                    else:
                        # 沉睡0.5s，等待缓冲队列中有命令
                        time.sleep(0.5)

            elif self.tar_mode == "normal":
                self.cur_mode = "normal"
                self.mode.stage.fnset.cur_mode = "normal"
                self.mode.stage.cur_stage = self.cur_stage
                # 无人机进入normal模式，自动检测小车并降落
                while self.tar_mode == self.cur_mode:
                    stage = self.mode.stage.cur_stage
                    if stage == "landed":
                        self.tar_mode = "landed"
                        self.mode.stage.fnset.tar_mode = "landed"
                        break
                    if stage is None:
                        stage = "search"
                    self.mode.stage.switch.get(stage)()

            elif self.tar_mode == "trace":
                self.cur_mode = "trace"
                self.mode.stage.fnset.cur_mode = "trace"
                self.mode.stage.cur_stage = self.cur_stage
                # 无人机进入trace模式，自动检测小车并追踪
                while self.tar_mode == self.cur_mode:
                    stage = self.mode.stage.cur_stage
                    self.mode.stage.switch.get(stage)()

            else:
                time.sleep(1)

    # ----------------------- 子线程，接收小车命令并回显 ------------------------

    # 接收小车命令并回显给小车
    def receive_data(self):

        while not self.is_exit:
            data = self.ano_sock.recv(1024).decode("utf-8")
            print("(192.168.4.1) Car:", data)

            if data == "quit":
                self.ano_sock.send(data.encode("utf-8"))
                self.is_exit = True
                self.mode.stage.fnset.tar_mode = "landed"
                self.tar_mode = "landed"
                self.mode.controller.land()
                self.ano_exit()
                break

            elif self.tar_mode == "landed" and data == "takeoff":
                self.tar_mode = self.cur_mode
                self.mode.stage.fnset.tar_mode = self.cur_mode

            elif self.cur_mode == "control" and data in self.control_cmd_list:
                self.control_buf_list.append(data)

            # 切换到手动控制模式
            elif data == "ctrl" or data == "control":
                print("已切换到 ---------> 手动控制模式 <---------")
                self.tar_mode = "control"
                self.mode.stage.fnset.tar_mode = "control"

            # 切换到追踪降落模式
            elif data == "normal":
                # 检查当前无人机状态
                self.cur_stage = self.mode.stage.check_stage()
                if self.cur_stage == "None":
                    data = "无人机状态异常，请检查后重试"
                else:
                    if self.cur_stage == "takeoff":
                        self.mode.stage.fnset.tar_mode = "landed"
                        self.tar_mode = "landed"
                        self.cur_mode = "normal"
                    elif self.cur_stage == "search":
                        self.tar_mode = "normal"
                        self.mode.stage.fnset.tar_mode = "normal"
                    print("已切换到 ---------> 追踪降落模式 <---------")

            # 切换到追踪模式
            elif data == "trace":
                # 检查当前无人机状态
                self.cur_stage = self.mode.stage.check_stage()
                if self.cur_stage == "None":
                    data = "无人机状态异常，请检查后重试"
                else:
                    if self.cur_stage == "takeoff":
                        self.mode.stage.fnset.tar_mode = "landed"
                        self.tar_mode = "landed"
                        self.cur_mode = "trace"
                    elif self.cur_stage == "search":
                        self.tar_mode = "trace"
                        self.mode.stage.fnset.tar_mode = "trace"
                    print("已切换到 ---------> 追踪模式 <---------")

            else:
                print("无效的输入！")
                data += " 无效的输入！请尝试输入ano ctrl"

            self.ano_sock.send(data.encode("utf-8"))

        self.ano_sock.close()

    # ---------------------------- 退出函数 -----------------------------

    def ano_exit(self):
        self.ano_sock.close()
        self.mode.stage.fnset.detector.save_all(True)
        self.mode.stage.fnset.detector.cvRead.close_down_cam()
        print('我被成功退出啦~')

    # 将保存在内存中的图片和log保存到硬盘中
    def signal_handler(self, signum, frame):
        self.ano_exit()


# ---------------------------- 程序启动入口 ----------------------------
if __name__ == '__main__':

    anoDrone = AnoDrone()
    # 检测是否按下ctrl+c
    signal.signal(signal.SIGINT, anoDrone.signal_handler)

    try:
        anoDrone.main_process()

    except Exception as ex:
        print(ex)
        ex_type, ex_val, ex_stack = sys.exc_info()
        for stack in traceback.extract_tb(ex_stack):
            print(stack)
        anoDrone.ano_sock.send("quit".encode("utf-8"))
        anoDrone.is_exit = True
        anoDrone.mode.stage.fnset.tar_mode = "landed"
        anoDrone.tar_mode = "landed"
        anoDrone.mode.controller.land()
        anoDrone.ano_exit()
