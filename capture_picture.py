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
        while self.count < 101:
            alt = self.controller.get_alt()
            print(self.count, "ALT: ", alt)
            self.count += 1
            self.detector.detect_landmark()
            time.sleep(0.1)
        self.detector.save_all(True)
        self.detector.cvRead.close_down_cam()
        print('我被成功退出啦~')
        sys.exit(0)


if __name__ == "__main__":
    test = Test()
    test.test()
