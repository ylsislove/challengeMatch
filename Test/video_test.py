import cv2 as cv


capture = cv.VideoCapture(0)
height = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
width = capture.get(cv.CAP_PROP_FRAME_WIDTH)
count = capture.get(cv.CAP_PROP_FRAME_COUNT)
fps = capture.get(cv.CAP_PROP_FPS)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
print(height, width, count, fps)

while True:
    ret, frame = capture.read()
    if ret is True:
        cv.imshow("video-input", frame)
        c = cv.waitKey(50)
        if c == 27:     # ESC
            break
    else:
        break

capture.release()
cv.destroyAllWindows()
