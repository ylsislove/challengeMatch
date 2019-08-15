# -*- coding:utf-8 -*-
#
# 检测降落标志"H"
#

import cv2 as cv
import math


image_center = (180, 320)


def detect_h(_src):
    # 图像逆时针旋转90度
    _src = cv.flip(cv.transpose(_src), 0)
    # 通过颜色范围检测提取ROI区域
    roi = cv.inRange(_src, (85, 20, 0), (130, 80, 60))
    # cv.imshow("roi", roi)

    M = cv.moments(roi)
    if M['m00'] == 0:
        return _src, None, None, None
    cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']

    # H中心减图像中心，得到x偏差和y偏差
    cx = round(cx)
    cy = round(cy)
    x_bias = cx - image_center[0]
    y_bias = cy - image_center[1]

    # 计算forward_angle
    x_abs = abs(x_bias)
    y_abs = abs(y_bias)
    if x_bias == 0 or y_bias == 0:
        return _src, x_bias, y_bias, 0

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

    return _src, x_bias, y_bias, round(forward_angle)


if __name__ == "__main__":

    # for i in range(1, 101, 1):
    #     src = cv.imread("../picture/1563045900/origpic/%d.jpg" % i)
    #     res, x, y, angle, f_angle = detect_h(src)
    #     if x is not None:
    #         cv.putText(res, "x: %d | y: %d | h_ag: %d | for_ag: %d" %
    #                    (x, y, angle, f_angle),
    #                    (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    #     cv.imwrite("../picture/1563045900/origpic/%d.jpg" % i, res)

    src = cv.imread("../picture/1563053640/origpic/49.jpg")
    cv.imshow("input", src)
    res, x, y, angle, f_angle = detect_h(src)
    if x is not None:
        cv.putText(res, "x: %d | y: %d | h_ag: %d | for_ag: %d" %
                   (x, y, angle, f_angle),
                   (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv.imshow("res", res)

    cv.waitKey()
    cv.destroyAllWindows()
