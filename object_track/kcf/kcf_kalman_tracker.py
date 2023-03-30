#!/usr/bin/env python3
import cv2
import numpy as np
from tracker_base import TrackerBase


class KcfKalmanTracker(TrackerBase):
    def __init__(self, window_name):
        super(KcfKalmanTracker, self).__init__(window_name)
        self.tracker = cv2.TrackerKCF_create()
        self.detect_box = None
        self.track_box = None
        ####init kalman####
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                                               np.float32) * 0.03
        self.measurement = np.array((2, 1), np.float32)
        self.prediction = np.array((2, 1), np.float32)

    def process_image(self, frame):
        try:
            if self.detect_box is None:
                return frame
            src = frame.copy()
            if self.track_box is None or not self.is_rect_nonzero(self.track_box):
                self.track_box = self.detect_box
                if self.tracker is None:
                    raise Exception("tracker not init")
                status = self.tracker.init(src, self.track_box)
                if not status:
                    raise Exception("tracker initial failed")
            else:
                self.track_box = self.track(frame)
        except:
            pass
        return frame

    def track(self, frame):
        status, coord = self.tracker.update(frame)
        center = np.array([[np.float32(coord[0] + coord[2] / 2)], [np.float32(coord[1] + coord[3] / 2)]])
        self.kalman.correct(center)
        self.prediction = self.kalman.predict()
        cv2.circle(frame, (int(self.prediction[0]), int(self.prediction[1])), 4, (255, 60, 100), 2)
        round_coord = (int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3]))
        return round_coord


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    kcfkalmantracker = KcfKalmanTracker('base')
    while True:
        ret, frame = cap.read()
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y / 2), int(x / 2)))
        kcfkalmantracker.rgb_image_callback(small_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
