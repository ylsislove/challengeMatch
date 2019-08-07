# -*- coding:utf-8 -*-
#
# 检测红十字
#

import cv2
import numpy as np

'''
@doc function:detect the red end box
@doc x, y: the distance between the center of detect box and the center of initial image,
when x_bia > 0,the box center is on the right of the image
when y_bia > 0,the box center is on the below of the image
@param img: image on which detected box was drawing
@return img, x_bia, y_bia
'''
def detect_redcross(img):
    result = np.copy(img)
    # lower_red=np.array([0,162,142])
    # upper_red=np.array([179,209,162])
    lower_red=np.array([0,150,120])
    upper_red=np.array([179,220,182])
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_red,upper_red)
    _,contours,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    rect_cnt = 0
    center_x = 0
    center_y = 0
    max_w = 0
    max_h = 0
    for cnt in contours:
        if len(cnt) > 50:
            x, y, w, h = cv2.boundingRect(cnt)
            if max_h * max_w < w * h:
                max_w = w
                max_h = h
                center_x = x
                center_y = y
            rect_cnt += 1
    # print(contours)
    # print(img)
    cv2.rectangle(result, (center_x, center_y), (center_x + max_w, center_y + max_h), (0, 255,0), 3)
    cv2.circle(result, (center_x + max_w / 2, center_y + max_h / 2), 2, (0, 0, 255), 2)
    if center_x != 0 and center_y != 0:
        x_bia = center_x - img.shape[1] / 2
        y_bia = center_y - img.shape[0] / 2
        return result,x_bia,y_bia
    else:
        return result,None,None
