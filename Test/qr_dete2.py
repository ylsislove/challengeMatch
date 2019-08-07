import cv2 as cv
import numpy as np
import math


def detect_qr(image):

    image = cv.flip(cv.transpose(image), 0)

    # cv.imshow("src", image)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, 80, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
    # cv.imshow("binary", binary)

    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # cv.drawContours(image, contours, -1, (255, 0, 0), 1)

    # cv.imshow('contours', image)

    if hierarchy is None or len(hierarchy) <= 0:
        return image, None, None, None
    hierarchy = hierarchy[0]
    found = []

    # 识别二维码中的回形定位符
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if c >= 2 and len(contours[i]) < 230:
            found.append(i)

    # print(found)

    if len(found) >= 2:
        cnt = contours[found[0]]
        # print found
        for i in found[1:]:
            cnt = np.append(cnt, contours[i], axis=0)
        rect = cv.minAreaRect(cnt)
        # opencv3 change the function to cv2.boxPoints()
        box = np.int0(cv.boxPoints(rect))
        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        Xmin = np.min(Xs)
        Ymin = np.min(Ys)
        Xmax = np.max(Xs)
        Ymax = np.max(Ys)
        box_area = (box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2
        # print('box_area', box_area)
        # recognize the box wether it is close to cubic
        # if (Ymax - Ymin)/(Xmax - Xmin) < 1.2 and (Ymax - Ymin)/(Xmax - Xmin) > 0.8:
        objectX = int((Xmin + Xmax) / 2)
        objectY = int((Ymin + Ymax) / 2)
        # cv2.line(image,(Xs[0],Ys[0]),(Xs[1],Ys[1]),(0,0,255),1)
        cv.circle(image, (objectX, objectY), 3, (255, 255, 255), 2)
        cv.circle(image, (240, 320), 3, (255, 255, 255), 2)
        cv.drawContours(image, [box], -1, (0, 255, 0), 2)
        # compute the bias between box center and img center
        x_bia = objectX - image.shape[1] / 2
        y_bia = objectY - image.shape[0] / 2
        angle = None
        if len(found) >= 3:
            for i in range(len(found)):
                x, y, w, h = cv.boundingRect(contours[found[i]])
                a = (x + w / 2, y + h / 2)
                cv.circle(image, (int(a[0]), int(a[1])), 3, (0, 0, 255), 2)
            # recongnition the three rect depending on the area ratio
            sub_square = [None for i in range(3)]
            sub_cnt = 0
            for i in range(len(found)):
                x, y, w, h = cv.boundingRect(contours[found[i]])
                if abs((w * h * 1.0) / box_area - 0.108) < 0.05 and sub_cnt < 3:
                    sub_square[sub_cnt] = found[i]
                    sub_cnt += 1
            if sub_cnt != 3:
                return image, None, None, None

            x1, y1, w1, h1 = cv.boundingRect(contours[sub_square[0]])
            x2, y2, w2, h2 = cv.boundingRect(contours[sub_square[1]])
            x3, y3, w3, h3 = cv.boundingRect(contours[sub_square[2]])
            a = (int(x1 + w1 / 2), int(y1 + h1 / 2))
            b = (int(x2 + w2 / 2), int(y2 + h2 / 2))
            c = (int(x3 + w3 / 2), int(y3 + h3 / 2))

            cv.circle(image, a, 3, (255, 0, 0), 2)
            cv.circle(image, b, 3, (255, 0, 0), 2)
            cv.circle(image, c, 3, (255, 0, 0), 2)
            # compute the direction of qrcode
            list = []
            list.append(abs((a[0] - b[0]) * (a[0] - c[0]) + (a[1] - b[1]) * (a[1] - c[1])))
            list.append(abs((b[0] - a[0]) * (b[0] - c[0]) + (b[1] - a[1]) * (b[1] - c[1])))
            list.append(abs((c[0] - a[0]) * (c[0] - b[0]) + (c[1] - a[1]) * (c[1] - b[1])))
            index = np.argmin(list)
            line = None
            center = [0, 0]
            point = None
            # judge the middle back shape
            if index == 0:
                line = [a[0] - (b[0] + c[0]) / 2, a[1] - (b[1] + c[1]) / 2]
                point = a
                center = [int((b[0] + c[0]) / 2), int((b[1] + c[1]) / 2)]
            elif index == 1:
                line = [b[0] - (a[0] + c[0]) / 2, b[1] - (a[1] + c[1]) / 2]
                point = b
                center = [int((a[0] + c[0]) / 2), int((a[1] + c[1]) / 2)]
            else:
                line = [c[0] - (a[0] + b[0]) / 2, c[1] - (a[1] + b[1]) / 2]
                point = c
                center = [int((b[0] + a[0]) / 2), int((b[1] + a[1]) / 2)]

            # compute the direction of qrcode
            line = [line[0], -line[1]]
            angle = math.atan2(line[1], line[0]) / math.pi * 180 - 45
            # angle = angle if angle > 0 else angle + 360
            # draw line
            cv.line(image, (240, 320), tuple(center), (255, 0, 0), 2)

        return image, x_bia, y_bia, angle
    else:
        return image, None, None, None



if __name__ == "__main__":

    for i in range(14):
        src = cv.imread("pic/%d.jpg" % (36+int(i)))
        if src is not None:
            res, x, y, a = detect_qr(src)
            if x is not None:
                # cv.imwrite("pic/%d_ok.jpg" % (36+int(i)), res)
                print("序号：%d，偏角：%.2f" % (36+int(i), a))

    cv.waitKey()
    cv.destroyAllWindows()
