import cv2
from Welcome_face_detector import Face_Detector
from rev_cam import rev_cam
from robotPi import robotPi





# give the name of the input video file
class welguy():
    def __init__(self):
        self.CAM_NUM = 0
        self.cap = cv2.VideoCapture(self.CAM_NUM)
        self.face = Face_Detector()
        self.robot = robotPi()

        while self.cap.isOpened():
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            frame = rev_cam(frame)
            faceflow, faces = self.face.find_faces(frame, ret)

            # Display the resulting frame
            cv2.imshow('Video', faceflow)
            if len(faces) != 0:
                print("Aholla~!!")
                self.robot.movement.wave_hands()
            elif len(faces) == 0:
                # print("move left and right to find people")
                self.robot.movement.turn_right(speed=3)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything is done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    welcome_guy = welguy()
    exit(0)
