#!/usr/bin/env python3
import cv2
from tracker_base import TrackerBase
import numpy as np


class GoodFeatures(TrackerBase):
    def __init__(self, window_name):
        super(GoodFeatures, self).__init__(window_name)
        self.feature_size = 1
        # Good features parameters
        self.gf_maxCorners = 200
        self.gf_qualityLevel = 0.02
        self.gf_minDistance = 7
        self.gf_blockSize = 10
        self.gf_useHarrisDetector = True
        self.gf_k = 0.04
        # Store all parameters together for passing to the detector
        self.gf_params = dict(maxCorners=self.gf_maxCorners, qualityLevel=self.gf_qualityLevel,
                              minDistance=self.gf_minDistance, blockSize=self.gf_blockSize,
                              useHarrisDetector=self.gf_useHarrisDetector, k=self.gf_k)
        self.keypoints = list()
        self.detect_box = None
        self.mask = None

    def process_image(self, frame):
        try:
            if not self.detect_box:
                return frame
            src = frame.copy()
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            keypoints = self.get_keypoints(gray, self.detect_box)
            if keypoints is not None and len(keypoints) > 0:
                for x, y in keypoints:
                    cv2.circle(self.marker_image, (x, y), self.feature_size, (0, 255, 0), -1)
        except:
            pass
        return frame

    def get_keypoints(self, input_image, detect_box):
        self.mask = np.zeros_like(input_image)
        try:
            x, y, w, h = detect_box
        except:
            return None
        self.mask[y:y + h, x:x + w] = 255
        keypoints = list()
        kp = cv2.goodFeaturesToTrack(input_image, mask=self.mask, **self.gf_params)
        if kp is not None and len(kp) > 0:
            for x, y in np.float32(kp).reshape(-1, 2):
                keypoints.append((x, y))
        return keypoints


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    goodfeatures = GoodFeatures('good_feature')
    while True:
        ret, frame = cap.read()
        x, y = frame.shape[0:2]
        small_frame = cv2.resize(frame, (int(y / 2), int(x / 2)))
        goodfeatures.rgb_image_callback(small_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
