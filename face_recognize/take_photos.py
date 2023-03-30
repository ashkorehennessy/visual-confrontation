import cv2
import numpy as np
import os
from rev_cam import rev_cam


def generate_img(dirname):
    face_cascade = cv2.CascadeClassifier('./face_detect/haarcascade_frontalface_default.xml')
    if (not os.path.isdir(dirname)):	#创建目录
        os.makedirs(dirname)
    cap = cv2.VideoCapture(0)
    count = 0
    while True:
        ret, frame = cap.read()
        frame = rev_cam(frame)
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y/2), int(x/2)))
        result = small_frame.copy()
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            result = cv2.rectangle(result, (x, y), (x+w, y+h), (255, 0, 0), 2)
            f = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            if count<20:
                cv2.imwrite(dirname + '%s.pgm' % str(count), f)
                print(count)
                count += 1
        cv2.imshow('face', result)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    generate_img("./data/guo/")
