from cv_detector.detector import Detector
import Ano_Controller
import time
import sys


class Test:

    def __init__(self):

        self.controller = Ano_Controller.Controller()
        self.command = self.controller.command
        self.detector = Detector()
        # 照片序号
        self.count = 1

    def test(self):
        time.sleep(1)
        while True:
            # alt = self.command.get_alt()
            # print(self.count, "ALT: ", alt)
            # self.count += 1
            self.detector.detect_h()
            time.sleep(0.1)


if __name__ == "__main__":
    test = Test()
    try:
        test.test()

    except KeyboardInterrupt:
        test.detector.save_all(True)
        test.detector.cvRead.close_down_cam()
        test.command.close_receiver()
        print('我被成功退出啦~')
