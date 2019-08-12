# -*- coding:utf-8 -*-
#
# 向无人机发送命令
#


import traceback
import Ano_Stage
import signal
import sys


class AnoDrone:

    def __init__(self):
        self.stage = Ano_Stage.Stage()
        self.port = self.stage.fnset.command.sender.base.port

    # --------------------------- 主线程，主循环函数 ---------------------------

    def main_process(self):
        while self.port.isOpen():
            # 获取改变后的状态
            stage = self.stage.cur_stage
            # 根据当前状态，调用对应函数（仿照switch）
            self.stage.switch.get(stage)()

    # ---------------------------- 退出函数 -----------------------------

    def ano_exit(self):
        self.stage.fnset.detector.save_all(True)
        self.stage.fnset.detector.cvRead.close_down_cam()
        self.stage.fnset.command.close_receiver()
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
        anoDrone.stage.fnset.controller.land()
        anoDrone.ano_exit()
