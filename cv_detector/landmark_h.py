# -*- coding:utf-8 -*-
#
# 检测降落标志"H"
#

import math
import cv2 as cv
import numpy as np

image_center = (240, 424)


def detect_h(_src):
    # 图像逆时针旋转90度
    _src = cv.flip(cv.transpose(_src), 0)
    # 通过颜色范围检测提取ROI区域
    roi = cv.inRange(_src, (85, 20, 0), (130, 80, 60))
    # cv.imshow("roi", roi)
    # # 膨胀操作
    se = np.ones((27, 27), dtype=np.uint8)
    dilate = cv.dilate(roi, se, None, (-1, -1), 1)
    # cv.imshow("dilate", dilate)
    # 收缩操作
    # se = np.ones((5, 5), dtype=np.uint8)
    # erode = cv.erode(roi, se, None, (-1, -1), 1)
    # cv.imshow("erode", erode)
    # 检测边缘
    canny = cv.Canny(dilate, 60, 150)
    # canny = cv.Canny(erode, 60, 150)
    # cv.imshow("canny", canny)
    # 寻找轮廓
    # contours = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours, h = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # print(contours)

    # cv.drawContours(_src, contours, -1, (0, 255, 0), 1)

    if len(contours) == 0:
        return _src, None, None, None, None

    # 找到面积最大的轮廓
    c = sorted(contours, key=cv.contourArea, reverse=True)[0]
    # cv.drawContours(_src, [c], 0, (0, 255, 0), 2)
    # 计算轮廓的面积
    area = cv.contourArea(c)
    if area < 2500:
        return _src, None, None, None, None

    # 计算最小外接矩形
    rect = cv.minAreaRect(c)
    # 得到最小外接矩形的中心点
    cx, cy = rect[0]
    # 轮廓的偏角
    h_angle = rect[2]
    # 计算最小外接矩形的顶点信息
    box = cv.boxPoints(rect)
    # 绘制最小外接矩形
    cv.drawContours(_src, [np.int0(box)], 0, (0, 255, 0), 2)

    # H中心减图像中心，得到x偏差和y偏差
    cx = round(cx)
    cy = round(cy)
    x_bias = cx - image_center[0]
    y_bias = cy - image_center[1]

    # 计算H偏角
    if h_angle < -45:
        h_angle = 90 + h_angle

    # 计算forward_angle
    x_abs = abs(x_bias)
    y_abs = abs(y_bias)
    if x_bias == 0 or y_bias == 0:
        return _src, x_bias, y_bias, h_angle, 0

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

    return _src, x_bias, y_bias, round(h_angle), round(forward_angle)


if __name__ == "__main__":

    # for i in range(1, 101, 1):
    #     src = cv.imread("../picture/1563045900/origpic/%d.jpg" % i)
    #     res, x, y, angle, f_angle = detect_h(src)
    #     if x is not None:
    #         cv.putText(res, "x: %d | y: %d | h_ag: %d | for_ag: %d" %
    #                    (x, y, angle, f_angle),
    #                    (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    #     cv.imwrite("../picture/1563045900/origpic/%d.jpg" % i, res)

    src = cv.imread("../picture/1563053640/origpic/10.jpg")
    cv.imshow("input", src)
    res, x, y, angle, f_angle = detect_h(src)
    if x is not None:
        cv.putText(res, "x: %d | y: %d | h_ag: %d | for_ag: %d" %
                   (x, y, angle, f_angle),
                   (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv.imshow("res", res)

    cv.waitKey()
    cv.destroyAllWindows()
