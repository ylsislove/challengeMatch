# -*- coding:utf-8 -*-
#
# 检测道路
#

import cv2
import numpy as np
import time
import math

# 定位道路交点
def locCross(img):
    x_center =320
    y_center =180
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(gray,100,150,apertureSize=3)
    lines=cv2.HoughLines(edges,1,np.pi/180,125)
    result = img.copy()
    if (lines is not None) and len(lines) >0:
        line_v1 =[]
        line_v2 =[]
        line_h1 =[]
        line_h2 =[]
        for line in lines[0]:
            rho=line[0]
            theta = line[1]
            if  (theta < (np.pi/4. )) or (theta > (3.*np.pi/4.0)):
                pt1 = (int(rho/np.cos(theta)),0)
                pt2 = (int((rho-result.shape[0]*np.sin(theta))/np.cos(theta)),result.shape[0])
                cv2.line(result,pt1,pt2,(255,0,0),1)
                line_v1.append(pt1)
                line_v2.append(pt2)
            else:
                pt1 = (0,int(rho/np.sin(theta)))
                pt2 = (result.shape[1], int((rho-result.shape[1]*np.cos(theta))/np.sin(theta)))
                line_h1.append(pt1)
                line_h2.append(pt2)
        if len(line_v1) >3 and len(line_h1) >3: #当水平和垂直的线都超过两条时，认为检测到路口
            xs1 = [ pt[0] for pt in line_v1]
            x1 = int(np.mean(xs1))
            xs2 = [ pt[0] for pt in line_v2]
            x2 = int(np.mean(xs2))
            x_center =int((x1+x2)/2)
            #水平线
            ys1 = [ pt[1] for pt in line_h1]
            y1 = int(np.mean(ys1))
            ys2 = [ pt[1] for pt in line_h2]
            y2 = int(np.mean(ys2))
            y_center = int((y1+y2)/2)
            #sign the cross on the picture
            cv2.circle(result,(x_center,y_center),3,(255,0,0),5)
            return result,x_center,180,1
        elif len(line_v1) >0 :
            xs1 = [ pt[0] for pt in line_v1]
            ys1 = [ pt[1] for pt in line_v1]
            x1 = int(np.mean(xs1))
            y1 = int(np.mean(ys1))
            xs2 = [ pt[0] for pt in line_v2]
            ys2 = [ pt[1] for pt in line_v2]
            x2 = int(np.mean(xs2))
            y2 = int(np.mean(ys2))
            cv2.line(result,(x1,y1),(x2,y2),(0,0,255),1)
            return result,x1,180,0
    return result,320,180,0

#检测垂直方向的路，返回道路中心线
def detect_road(img):
    result = np.copy(img)
    # detect lines on image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 150, apertureSize=3)
    lines_tem = cv2.HoughLines(edges, 1, np.pi / 180, 125)
    # return values,the angle and x bias of line
    # and the x and y bias of corner if it exists
    lines = None
    if lines_tem is not None:
        # opencv3.1
        lines = lines_tem[:, 0, :]
        # opencv2.4
        # lines = lines_tem[0,:,:] #
    angle_all = []
    line_angle = None
    x_bias = None
    if (lines is not None) and len(lines) > 0:
        line_v1 = []
        line_v2 = []
        line_h1 = []
        line_h2 = []
        for line in lines:
            rho = line[0]
            theta = line[1]
            if (theta < (np.pi / 4.0)) or (theta > (3. * np.pi / 4.0)):
                pt1 = (int(rho / np.cos(theta)), 0)
                pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
                cv2.line(result, pt1, pt2, (255, 0, 0), 1)
                line_v1.append(pt1)
                line_v2.append(pt2)
                theta = theta * 180 / np.pi
                theta = theta if theta < 90 else theta - 180
                angle_all.append(theta)
            else:
                pt1 = (0, int(rho / np.sin(theta)))
                pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
                cv2.line(result, pt1, pt2, (0, 0, 255), 1)
                line_h1.append(pt1)
                line_h2.append(pt2)
        # if detected certical lines are more 1,we think road has been detected
        if len(line_v1) > 1:
            xs1 = [pt[0] for pt in line_v1]
            ys1 = [pt[1] for pt in line_v1]
            x1 = int(np.mean(xs1))
            y1 = int(np.mean(ys1))
            xs2 = [pt[0] for pt in line_v2]
            ys2 = [pt[1] for pt in line_v2]
            x2 = int(np.mean(xs2))
            y2 = int(np.mean(ys2))
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 4)
            #compute the center of line
            center_x = int((x1 + x2) / 2)
            cv2.circle(result, (int(result.shape[1] / 2), int(result.shape[0] / 2)), 3, (0, 0, 255), 2)
            cv2.line(result, (int(result.shape[1] / 2), int(result.shape[0] / 2)), (center_x, int(result.shape[0] / 2)),
                     (0, 0, 255), 2)
            x_bias = center_x - result.shape[1] / 2
            line_angle = np.mean(angle_all)
    return result, line_angle, x_bias

if __name__=='__main__':
    capture = cv2.VideoCapture(0)
    # cv2.namedWindow('input_image', cv2.WINDOW_AUTOSIZE)
    while(1):
        ret, frame = capture.read()
        result, line_angle, x_bias = detect_road(frame)
        # cv2.imshow('input_image', result)
        print(line_angle, x_bias)
        # if cv2.waitKey(100) & 0xFF == ord('q'):
        #     break
        # cv2.destroyAllWindows()
