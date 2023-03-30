#!/usr/bin/env python3
import cv2
import numpy as np
from tracker_base import TrackerBase


class Camshift(TrackerBase):
    def __init__(self, window_name):
        super(Camshift, self).__init__(window_name)
        self.detect_box = None
        self.track_box = None

    def process_image(self, frame):
        try:
            if self.detect_box is None:
                return frame
            src = frame.copy()
            if self.track_box is None or not self.is_rect_nonzero(self.track_box):
                self.track_box = self.detect_box
                x, y, w, h = self.track_box
                self.roi = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2HSV)
                roi_hist = cv2.calcHist([self.roi], [0], None, [16], [0, 180])
                self.roi_hist = cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
                self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            else:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                back_project = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
                ret, self.track_box = cv2.CamShift(back_project, self.track_box, self.term_crit)
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                cv2.polylines(frame, [pts], True, 255, 1)
        except:
            pass
        return frame


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    camshift = Camshift('camshift')
    while True:
        ret, frame = cap.read()
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y / 2), int(x / 2)))
        camshift.rgb_image_callback(small_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()