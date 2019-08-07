# -*- coding:utf-8 -*-
#
# 封装道路二维码红十字等的检测函数，提供接口
# 用于检测和检测后的图片每50张存一次硬盘
#

from cv_detector.landmark import detect_landmark
from cv_detector.redcross import detect_redcross
from cv_detector.road import detect_road
from cv_detector.cv_read import CVRead
from cv_detector.qr import *
import threading
import cv2 as cv
import time
import os


class Detector:
    def __init__(self):
        self.cvRead = CVRead()
        self.cvRead.start()
        self.frame = None
        self.img = None

        # 初始化建立图片文件夹，将文件夹命名为时间戳，并将时间戳放到log中
        self._time = time.strftime("%Y:%m:%d %H:%M", time.localtime())
        self.timeArray = time.strptime(self._time, "%Y:%m:%d %H:%M")
        # 时间戳（分级）
        self.timeStamp = int(time.mktime(self.timeArray))
        # 创建图片文件夹，保存处理后的图片
        self.origpath = "./picture/" + str(self.timeStamp) + "/origpic/"
        self.propath = "./picture/" + str(self.timeStamp) + "/propic/"

        # 原图和处理后的图片，50张保存一次
        self.origlist = []
        self.prolist = []

        if os.path.exists(self.origpath) is False:
            os.makedirs(self.origpath)
        if os.path.exists(self.propath) is False:
            os.makedirs(self.propath)

        self.count_ori = 1
        self.count_pro = 1
        self.now_time = time.time()
        self.old_time = time.time()

        # 日志字典，最后结束的时候，会回显到图像中
        self.log_dict = {}

    def save_all(self, is_exit=False):

        if self.frame is not None:
            self.origlist.append(self.frame)
        if self.img is not None:
            self.prolist.append(self.img)

        # 程序退出，保存当前已记录到的图片
        if is_exit:
            t = threading.Thread(target=self.save_pic, args=(self.prolist, self.origlist))
            t.start()
            t.join()
            self.prolist = []
            self.origlist = []

            # 日志记录回显到图像中
            for key, value in self.log_dict.items():
                count = 1
                src = cv.imread("%s/%d.jpg" % (self.propath, key))
                cv.putText(src, "alt: %d | mode: %s" %
                           (value[1][0], value[1][1]),
                           (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if value[0][0] is not None:
                    count += 1
                    cv.putText(src, "x: %d | y: %d | land_ag: %d | for_ag: %d" %
                               (value[0][0], value[0][1], value[0][2], value[0][3]),
                               (10, 30 * count), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if value[2][0] is not None:
                    count += 1
                    cv.putText(src, value[2][0],
                               (10, 30 * count), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                cv.imwrite("%s/%d.jpg" % (self.propath, key), src)

            return

        # 当列表中图片数量到50时，存入硬盘
        if len(self.prolist) == 50:
            threading.Thread(target=self.save_pic, args=(self.prolist, self.origlist)).start()
            self.prolist = []
            self.origlist = []

    # 检测二维码
    def detect_qr(self):
        self.save_all()
        self.frame = self.cvRead.read()
        self.img, x_bias, y_bias, qr_angle, forward_angle = detect_qr(self.frame)
        return x_bias, y_bias, qr_angle, forward_angle

    # 检测二维码上的一个回形区域
    def detect_small_qr(self):
        self.save_all()
        self.frame = self.cvRead.read()
        self.img, x_bias, y_bias, qr_angle = detect_small_qr(self.frame)
        return x_bias, y_bias, qr_angle

    # 检测路
    def detect_road(self):
        self.save_all()
        self.frame = self.cvRead.read()
        self.img, angle, x_bias = detect_road(self.frame)
        if x_bias is not None:
            return x_bias, -115, -1 * angle
        else:
            return 0, 0, 0

    # 检测红十字
    def detect_redcross(self):
        self.save_all()
        self.frame = self.cvRead.read()
        self.img, x_bias, y_bias = detect_redcross(self.frame)
        return x_bias, y_bias

    # 检测降落标志
    def detect_landmark(self, alt):
        self.save_all()
        self.frame = self.cvRead.read()
        self.img, x, y, l_ag, f_ag = detect_landmark(self.frame, alt)
        return x, y, l_ag, f_ag

    # 保存内存中的图片
    def save_pic(self, prolist, origlist):
        self.now_time = time.time()
        self.old_time = self.now_time
        # 保存处理后的图片和原图
        for image in prolist:
            cv.imwrite(self.propath + str(self.count_pro) + ".jpg", image)
            self.count_pro += 1
        for image in origlist:
            cv.imwrite(self.origpath + str(self.count_ori) + ".jpg", image)
            self.count_ori += 1
        self.now_time = time.time()
        print("save pic........ time: ", self.now_time - self.old_time)
