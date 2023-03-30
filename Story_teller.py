from robotpi_movement import Movement
from barcode_scanner_video import QRscan
from imutils.video import VideoStream
from rev_cam import rev_cam
import time
import imutils
import cv2


QR = QRscan()
robot = Movement()
vs = VideoStream(src=0, resolution=(160, 120), framerate=10).start()
time.sleep(2.0)
name_old = ""

while True:
    frame = vs.read()
    frame = rev_cam(frame)
    frame = imutils.resize(frame, width=400)

    name, bbox = QR.scan(frame)
    if name != name_old:
        robot.set_volume(30)
        if 'liubei' in name:
            robot.play_sound(255, 1)
        elif 'guanyu' in name:
            robot.play_sound(255, 2)
        elif 'zhangfei' in name:
            robot.play_sound(255,  3)
        name_old = name

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()
