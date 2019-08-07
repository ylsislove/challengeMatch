import cv2 as cv
import os


class Picture:

    def __init__(self):
        self.path = "./picture/"
        if os.path.exists(self.path) is False:
            os.makedirs(self.path)
        self.capture_down = cv.VideoCapture(0)
        self.capture_down.set(cv.CAP_PROP_FRAME_WIDTH, 960)
        self.capture_down.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
        self.count = 1

    def picture(self):
        while True:
            ret, frame = self.capture_down.read()
            if ret:
                image = cv.flip(cv.transpose(frame), 0)
                cv.imwrite(self.path + str(self.count) + ".jpg", image)
                print(self.path + str(self.count) + ".jpg")
                self.count += 1


if __name__ == "__main__":
    print("已启动")
    test = Picture()
    test.picture()
