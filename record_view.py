import cv2
import numpy as np
import sys
record = sys.argv[1] + '.npy'
record_bin = sys.argv[1] + '_bin.npy'
size = np.load(record).shape[0]
for i in range(190, size):
    frame = np.load(record)[i]
    frame_bin = np.load(record_bin)[i]
    cv2.imshow('frame', frame)
    cv2.imshow('frame_bin', frame_bin * 255)
    for j in range(15, 0, -1):
        summ = np.sum(frame_bin[(j - 1) * 3: j * 3, :])
        if summ < 440:
            print("line detect in:", j, summ, i)
            if j > 5:
                print("end")
                break
    cv2.waitKey(1000)

# show specific frame
# frame_count = 240
# frame = np.load(record)[frame_count]
# frame_bin = np.load(record_bin)[frame_count]
# cv2.imshow('frame', frame)
# cv2.imshow('frame_bin', frame_bin * 255)
# cv2.waitKey(10000)
