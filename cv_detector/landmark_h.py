# -*- coding:utf-8 -*-
#
# 检测降落标志"H"
#

import cv2 as cv
import numpy as np

image_center = (240, 424)


def detect_h(_src):
    # 图像逆时针旋转90度
    img = cv.flip(cv.transpose(_src), 0)
    # 转变为灰度图像
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(img_gray, 60, 255, cv.THRESH_BINARY)
    img_edge = cv.Canny(thresh, 60, 150)
    contours, hierarchy = cv.findContours(img_edge.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img, None, None, None

    c = sorted(contours, key=cv.contourArea, reverse=True)[0]
    rect = cv.minAreaRect(c)
    mark_center = tuple(np.int0(rect[0]))
    mark_size = tuple(np.int0(rect[1]))
    h_angle = rect[2]

    if mark_size[0] * mark_size[1] < 50 * 50:
        return img, None, None, None

    # 计算landmark偏角
    if h_angle < -45:
        h_angle = 90 + h_angle

    # 得到外接矩形的四个顶点坐标并向下取整
    box = np.int0(cv.boxPoints(rect))
    cv.circle(img, mark_center, 3, (0, 255, 0), 3)
    cv.circle(img, image_center, 2, (255, 255, 255), 2)
    cv.drawContours(img, [box], -1, (0, 255, 0), 2)
    x_bias = mark_center[0] - image_center[0]
    y_bias = mark_center[1] - image_center[1]
    return img, x_bias, y_bias, h_angle


if __name__ == "__main__":
    src = cv.imread("test.jpg")
    res, x, y = detect_h(src)
    print(x, y)
    cv.imshow("result", res)

    cv.waitKey()
    cv.destroyAllWindows()
