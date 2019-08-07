import cv2 as cv
import numpy as np

src = cv.imread("../picture/1563014100/propic/42.jpg")
cv.imshow("image", src)
gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
cv.imshow("gray", gray)
gray1 = cv.equalizeHist(gray)
cv.imshow("equal", gray1)
qrcoder = cv.QRCodeDetector()
codeinfo, points, straight_qrcode = qrcoder.detectAndDecode(gray1)
if points is not None:
    print(points.shape)
    print(points)

    x = (points[0][0][0] + points[2][0][0]) / 2
    y = (points[0][0][1] + points[2][0][1]) / 2
    print(x, y)

    x1 = (points[1][0][0] + points[3][0][0]) / 2
    y1 = (points[1][0][1] + points[3][0][1]) / 2
    print(x1, y1)

    print(gray1.shape)

    x_bias = 320 - x
    y_bias = 240 - y
    print(x_bias)
    print(y_bias)
    result = np.copy(src)
    cv.drawContours(result, [np.int32(points)], 0, (0, 0, 255), 2)
    cv.line(result, (int(x), int(y)), (320, 240), (255, 0, 2), 2)
    print("qrcode : %s"% codeinfo)
    cv.imshow("result", result)

cv.waitKey(0)
cv.destroyAllWindows()