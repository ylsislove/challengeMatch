import cv2 as cv
import numpy as np

def check(src):
    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    qrcoder = cv.QRCodeDetector()
    codeinfo, points, straight_qrcode = qrcoder.detectAndDecode(gray)
    if points is not None:
        print(points)
        result = np.copy(src)
        cv.drawContours(result, [np.int32(points)], 0, (0, 0, 255), 2)
        print("qrcode : %s" % codeinfo)
        return result
    else:
        return None

capture = cv.VideoCapture(1)
height = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
width = capture.get(cv.CAP_PROP_FRAME_WIDTH)
count = capture.get(cv.CAP_PROP_FRAME_COUNT)
fps = capture.get(cv.CAP_PROP_FPS)
print(height, width, count, fps)

while True:
    ret, frame = capture.read()
    if ret is True:
        cv.imshow("video-input", frame)
        # result = check(frame)
        # if result is not None:
        #     cv.imshow("result", result)
        # else:
        #     cv.imshow("result", frame)
        c = cv.waitKey(50)
        if c == 27: # ESC
            break
    else:
        break

capture.release()
cv.destroyAllWindows()