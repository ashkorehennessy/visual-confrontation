import cv2
import numpy as np
import sys
record = sys.argv[1] + '.npy'
record_bin = sys.argv[1] + '_bin.npy'
size = np.load(record).shape[0]
for i in range(210, size):
    frame = np.load(record)[i]
    frame_bin = np.load(record_bin)[i]
    cv2.imshow('frame', frame)
    cv2.imshow('frame_bin', frame_bin * 255)
    cv2.waitKey(1000)

# show specific frame
frame_count = 215
frame = np.load(record)[frame_count]
frame_bin = np.load(record_bin)[frame_count]
cv2.imshow('frame', frame)
cv2.imshow('frame_bin', frame_bin * 255)
cv2.waitKey(10000)
