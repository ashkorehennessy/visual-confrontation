import cv2
import numpy as np
import sys
record = sys.argv[1] + '.npy'
record_bin = sys.argv[1] + '_bin.npy'
size = np.load(record).shape[0]
for i in range(0, size):
    frame = np.load(record)[i]
    # reverse
    frame = 1 - frame
    frame_bin = np.load(record_bin)[i]
    cv2.imshow('frame', frame * 255)
    cv2.imshow('frame_bin', frame_bin * 255)
    cv2.waitKey(100)