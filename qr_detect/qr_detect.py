
import cv2
import numpy as np
import zbar
from PIL import Image


def detect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)

    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 195, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    closed = cv2.erode(closed, None, iterations=6)
    closed = cv2.dilate(closed, None, iterations=6)

    cv2.imshow('gray', closed)

    result, contours, hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None

    c = sorted(contours, key=cv2.contourArea, reverse=True)[0]
    rect = cv2.minAreaRect(c)
    box = np.int0(cv2.boxPoints(rect))
    # cv2.polylines(image,[box],True,255,1)

    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    font = cv2.FONT_HERSHEY_SIMPLEX

    min = np.min(box, axis=0)
    max = np.max(box, axis=0)
    roi = image[min[1] - 10:max[1] + 10, min[0] - 10:max[0] + 10]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(image).convert('L')
    width, height = pil.size
    raw = pil.tobytes()

    zbarimage = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(zbarimage)
    for symbol in zbarimage:
        cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
        cv2.putText(image, symbol.data, (20, 100), font, 1, (255, 0, 0), 4)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y / 2), int(x / 2)))
        detect(small_frame)
        cv2.imshow('zbar', small_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
cv2.destroyAllWindows()
