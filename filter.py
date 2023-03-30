import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:
    ret , frame = cap.read()
    cv2.imshow('video', frame)
    x, y = frame.shape[0:2]
    small_frame = cv2.resize(frame,(int(y/2), int(x/2)))
    cv2.imshow('small', small_frame)
    img_mean = cv2.blur(small_frame,(5,5))
    img_Guassian = cv2.GaussianBlur(small_frame,(5,5), 0)
    img_median = cv2.medianBlur(small_frame,5)
    img_bilater = cv2.bilateralFilter(small_frame,9,75,75)
    cv2.imshow('mean',img_mean)
    cv2.imshow('guassian',img_Guassian)
    cv2.imshow('median',img_median)
    cv2.imshow('bilater',img_bilater)
    if cv2.waitKey(1) & 0xff ==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()