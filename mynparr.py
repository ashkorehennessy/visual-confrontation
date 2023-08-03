import numpy as np
import cv2


class Mynparr:
    def __init__(self):
        self.width = 160
        self.height = 45
        self.crop_top = 75
        self.crop_bottom = 120
        self.threshold = 120
        self.ksize = (5, 5)
        self.show = False
        self.morphology = False
        self.print = True
        self.left_white_pixel = 0
        self.right_white_pixel = 0
        self.up_white_pixel = 0
        self.down_white_pixel = 0
        self.diff = 0

    def process(self, image):
        frame = image[self.crop_top:self.crop_bottom, :]  # crop
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale
        ret, frame = cv2.threshold(frame, self.threshold, 1, cv2.THRESH_BINARY)  # threshold
        if self.morphology is True:
            frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, np.ones(self.ksize, np.uint8))  # morphology close
        if self.show is True:
            cv2.imshow('frame', frame * 255)
            cv2.waitKey(1)
        # calculate white pixels
        self.left_white_pixel = np.sum(frame[:, :self.width // 2])
        self.right_white_pixel = np.sum(frame[:, self.width // 2:])
        self.up_white_pixel = np.sum(frame[:self.height // 2, :])
        self.down_white_pixel = np.sum(frame[self.height // 2:, :])
        # calculate left right diff
        self.diff = int(self.left_white_pixel) - self.right_white_pixel
        if self.print is True:
            print(self.left_white_pixel, self.right_white_pixel, self.diff)
