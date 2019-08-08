# -*- coding:utf-8 -*-
#
# 检测降落标志
#

import cv2 as cv
import numpy as np
import math


image_center = (240, 424)


def detect_landmark(_src):
    # 图像逆时针旋转90度
    _src = cv.flip(cv.transpose(_src), 0)
    gray = cv.cvtColor(_src, cv.COLOR_RGB2GRAY)
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    # print("ret: ", ret)
    # cv.imshow("binary", binary)

    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # 存储轮廓中心点信息，为聚类做准备
    c_centers = []
    for c in range(len(contours)):
        # 计算最小外接矩形
        rect = cv.minAreaRect(contours[c])
        # 得到最小外接矩形的中心点
        cx, cy = rect[0]
        # 得到最小外接矩形的宽和高
        ww, hh = rect[1]

        # 轮廓近似，寻找矩形轮廓
        result = cv.approxPolyDP(contours[c], 4, True)
        vertexes = result.shape[0]
        if vertexes == 4:
            # 计算矩形轮廓的横纵比
            ratio = np.minimum(ww, hh) / np.maximum(ww, hh)
            # 计算矩形轮廓的面积
            area = cv.contourArea(contours[c])
            # 寻找正方形轮廓
            if ratio > 0.8 and area > 250:
                box = cv.boxPoints(rect)
                # cv.drawContours(_src, [np.int0(box)], 0, (0, 255, 0), 2)
                # 存储信息为 0：轮廓的顶点信息、1：轮廓中心点x坐标、2：轮廓中心点y坐标、3：轮廓的偏角
                c_centers.append([np.int0(box), round(cx), round(cy), rect[2]])

    if len(c_centers) < 2:
        return _src, None, None, None, None

    def compute_distance(x1, y1, x2, y2):
        return math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2)

    # print(c_centers)
    for c in c_centers:
        c.append(False)

    # 矩形聚类
    c_list = []
    for c in c_centers:
        # 跳过已经被聚类的点
        if c[4] is True:
            continue

        # 当前点加入临时列表
        t_list = []
        c[4] = True
        t_list.append(c)

        # 计算当前点与其余点的欧式距离
        for t in c_centers:
            if t[4] is False and compute_distance(c[1], c[2], t[1], t[2]) < 49:
                t[4] = True
                t_list.append(t)

        c_list.append(t_list)

    # print(c_list)

    # 找到子元素最多的那一类的索引
    t = [len(i) for i in c_list]
    c_index = t.index(max(t))

    # 绘制轮廓
    cx = cy = 0
    for c in c_list[c_index]:
        cv.drawContours(_src, [c[0]], 0, (0, 255, 0), 2)
        cx += c[1]
        cy += c[2]

    c_len = len(c_list[c_index])
    cx = round(cx / c_len)
    cy = round(cy / c_len)
    landmark_angle = round(c_list[c_index][0][3])

    # landmark中心减图像中心，得到x偏差和y偏差
    x_bias = cx - image_center[0]
    y_bias = cy - image_center[1]

    # 计算landmark偏角
    if landmark_angle < -45:
        landmark_angle = 90 + landmark_angle

    # 计算forward_angle
    x_abs = abs(x_bias)
    y_abs = abs(y_bias)
    if x_bias == 0 or y_bias == 0:
        return _src, x_bias, y_bias, landmark_angle, 0

    forward_angle = round(math.atan(x_abs / y_abs) / math.pi * 180)
    # 第一象限
    if y_bias < 0 < x_bias:
        pass
    # 第二象限
    elif x_bias < 0 and y_bias < 0:
        forward_angle = -forward_angle
    # 第三象限
    elif x_bias < 0 < y_bias:
        forward_angle = forward_angle - 180
    # 第四象限
    elif forward_angle != 0:
        forward_angle = 180 - forward_angle

    cv.circle(_src, (cx, cy), 2, (255, 255, 255), 2)
    cv.circle(_src, image_center, 2, (255, 255, 255), 2)
    cv.line(_src, image_center, (cx, cy), (255, 0, 0), 2)

    return _src, x_bias, y_bias, landmark_angle, forward_angle


if __name__ == "__main__":
    # src = cv.imread("../picture/1563035940/origpic/468.jpg")
    src = cv.imread("../picture/1563045840/origpic/1.jpg")
    print(src.shape)
    res, x, y, l_ag, f_ag = detect_landmark(src)
    cv.namedWindow("result")
    cv.imshow("result", res)

    # import time
    # t_sum = 0
    #
    # for i in range(1, 101):
    #     src = cv.imread("../picture/1563035940/origpic/%d.jpg" % i)
    #
    #     t = time.time()
    #     res, x, y, l_ag, f_ag = detect_landmark(src)
    #     t_sum += (time.time() - t)
    #
    #     cv.imwrite("../picture/1563027600/test/%d.jpg" % i, res)
    #
    # print(t_sum / 100)
    cv.waitKey()
    cv.destroyAllWindows()
