import cv2 as cv
import threading


class CVRead(threading.Thread):

    def __init__(self):
        super().__init__()
        self.capture_down = None
        self.capture_serial = 0
        self.img = None
        self.frame = None
        self.is_close = False

    # 打开下置摄像头
    def open_down_cam(self):
        self.capture_down = cv.VideoCapture(self.capture_serial)
        self.capture_down.set(cv.CAP_PROP_FRAME_WIDTH, 848)
        self.capture_down.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        _, _ = self.capture_down.read()

    # 关闭下置摄像头
    def close_down_cam(self):
        self.is_close = True

    def run(self):
        print("摄像头已启动")
        self.open_down_cam()
        while not self.is_close:
            ret, self.frame = self.capture_down.read()
            if ret:
                self.img = self.frame
            else:
                print("read image wrong")
        self.capture_down.release()

    def read(self):
        return self.img
