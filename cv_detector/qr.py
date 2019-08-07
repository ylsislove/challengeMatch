# -*- coding:utf-8 -*-
#
# 偏角问题：
# @return qr_angle：表示二维码正向和飞机正向角度的偏差，取值范围（-45，45）
# 例如，-30度表示飞机正向向左（逆时针）偏移30度到达二维码正向
# @return forward_angle：表示飞机正向和图像中心的和二维码中心点连线的偏差，取值范围（-180，180）
# 一四象限取值范围（0，180），二三象限取值范围（0，-180）
#

import cv2 as cv
import numpy as np
import math

image_center = (240, 320)


def detect_qr(src):
    # 图像逆时针旋转90度
    image = cv.flip(cv.transpose(src), 0)
    # 转换为灰度的色彩空间
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # 得到二值图像
    _, binary = cv.threshold(gray, 80, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
    # 得到二进制轮廓，建立轮廓的层级关系，仅保存轮廓的拐点信息
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # 第三个参数表示要绘制轮廓的编号，若为-1，则绘制所有轮廓
    # cv.drawContours(image, contours, -1, (255, 0, 0), 1)
    # cv.imshow('contours', image)
    if hierarchy is None or len(hierarchy) <= 0:
        return image, None, None, None, None

    # 识别二维码中的回形定位符
    hierarchy = hierarchy[0]
    found = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if c >= 2 and len(contours[i]) < 230:
            found.append(i)

    if len(found) > 3:
        found = found[:3]
    if len(found) > 2:
        cnt = contours[found[0]]
        for i in found[1:]:
            cnt = np.append(cnt, contours[i], axis=0)
        # 得到回形定位符的最小外接矩形，返回矩形的中心（x，y），（宽度，高度），旋转角度
        rect = cv.minAreaRect(cnt)
        qr_center = tuple(np.int0(rect[0]))
        qr_size = tuple(np.int0(rect[1]))
        # print(rect)
        # 绘制二维码中心点和图像中心点
        cv.circle(image, qr_center, 2, (255, 255, 255), 2)
        cv.circle(image, image_center, 2, (255, 255, 255), 2)
        cv.line(image, image_center, qr_center, (255, 0, 0), 2)
        # 得到外接矩形的四个顶点坐标并向下取整
        box = np.int0(cv.boxPoints(rect))
        # 绘制二维码轮廓
        cv.drawContours(image, [box], -1, (0, 255, 0), 2)
        # # 绘制三个回形定位符的中心点
        # x1, y1, w1, h1 = cv.boundingRect(contours[found[0]])
        # x2, y2, w2, h2 = cv.boundingRect(contours[found[1]])
        # x3, y3, w3, h3 = cv.boundingRect(contours[found[2]])
        # a = (int(x1 + w1 / 2), int(y1 + h1 / 2))
        # b = (int(x2 + w2 / 2), int(y2 + h2 / 2))
        # c = (int(x3 + w3 / 2), int(y3 + h3 / 2))
        # cv.circle(image, a, 2, (0, 0, 255), 2)
        # cv.circle(image, b, 2, (0, 0, 255), 2)
        # cv.circle(image, c, 2, (0, 0, 255), 2)

        # 简单的判断方法，如果二维码的轮廓的长和宽相差较大，判为检测二维码失败，返回标记后的图像
        if abs(qr_size[0] - qr_size[1]) > 20:
            return image, None, None, None, None

        # 二维码中心减图像中心，得到x偏差和y偏差
        x_bias = qr_center[0] - image_center[0]
        y_bias = qr_center[1] - image_center[1]
        # print(x_bias)
        # print(y_bias)

        # 计算二维码偏角
        qr_angle = round(rect[2])
        if qr_angle < -45:
            qr_angle = 90 + qr_angle

        # 计算forward_angle
        x_abs = abs(x_bias)
        y_abs = abs(y_bias)
        if x_bias == 0 or y_bias == 0:
            return image, x_bias, y_bias, qr_angle, 0

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
        else:
            forward_angle = 180 - forward_angle

        return image, x_bias, y_bias, qr_angle, forward_angle
    else:
        return image, None, None, None, None


def detect_small_qr(src):
    # 深拷贝一份图像
    copy_src = np.copy(src)
    # 尝试检测完整的二维码
    img, x_bias, y_bias, qr_angle, forward_angle = detect_qr(copy_src)
    if x_bias is not None:
        return img, x_bias, y_bias, qr_angle

    # 检测不到完整的二维码，则检测一个回形区域
    image = cv.flip(cv.transpose(src), 0)
    # 转换为灰度的色彩空间
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # 得到二值图像
    _, binary = cv.threshold(gray, 80, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
    # 得到二进制轮廓，建立轮廓的层级关系，仅保存轮廓的拐点信息
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if hierarchy is None or len(hierarchy) <= 0:
        return image, None, None, None

    # 识别二维码中的回形定位符
    hierarchy = hierarchy[0]
    found = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if c >= 2 and len(contours[i]) < 230:
            found.append(i)

    if len(found) > 0:
        distance = 2147483647
        qr_center = (240, 320)
        for i in found:
            x1, y1, w1, h1 = cv.boundingRect(contours[i])
            c = (int(x1 + w1 / 2), int(y1 + h1 / 2))
            cv.circle(image, c, 2, (0, 0, 255), 2)
            d = math.pow((c[0] - image_center[0]), 2) + math.pow((c[1] - image_center[1]), 2)
            if d < distance:
                distance = d
                qr_center = c
        cv.circle(image, image_center, 2, (255, 255, 255), 2)
        cv.line(image, image_center, qr_center, (255, 0, 0), 2)
        # print(qr_center)

        x_bias = qr_center[0] - image_center[0]
        y_bias = qr_center[1] - image_center[1]
        # print(x_bias, y_bias)
        return image, x_bias, y_bias, 0

    else:
        return image, None, None, None


def test(src):
    image = cv.flip(cv.transpose(src), 0)
    # 转换为灰度的色彩空间
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # 得到二值图像
    _, binary = cv.threshold(gray, 80, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
    # 得到二进制轮廓，建立轮廓的层级关系，仅保存轮廓的拐点信息
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if hierarchy is None or len(hierarchy) <= 0:
        return image, None

    # 识别二维码中的回形定位符
    hierarchy = hierarchy[0]
    found = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if c >= 2 and len(contours[i]) < 230:
            found.append(i)

    if len(found) > 2:
        cnt = contours[found[0]]
        for i in found[1:]:
            cnt = np.append(cnt, contours[i], axis=0)
        # 得到回形定位符的最小外接矩形，返回矩形的中心（x，y），（宽度，高度），旋转角度
        rect = cv.minAreaRect(cnt)
        # 得到外接矩形的四个顶点坐标并向下取整
        box = np.int0(cv.boxPoints(rect))
        # 绘制二维码轮廓
        cv.drawContours(image, [box], -1, (0, 255, 0), 2)
        # 计算二维码偏角
        angle = round(rect[2])
        if angle < -45:
            angle = 90 + angle

        return image, angle
    else:
        return image, None


if __name__ == "__main__":

    src = cv.imread("../picture/1563027480/origpic/53.jpg")
    # res, alpha = test(src)
    # cv.imshow("result", res)
    # print(alpha)
    image, x_bias, y_bias, qr_angle, forward_angle = detect_qr(src)
    print(x_bias)
    cv.imshow("result", image)

    cv.waitKey()
    cv.destroyAllWindows()
