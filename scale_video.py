import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:
    ret , frame = cap.read()
    cv2.imshow('video', frame)
    x, y = frame.shape[0:2]
    small_frame = cv2.resize(frame,(int(y/2), int(x/2)))
    cv2.imshow('small', small_frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()