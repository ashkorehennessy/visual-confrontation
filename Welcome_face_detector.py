import cv2
import os
class Face_Detector():
    def __init__(self):
        self.model_path = os.curdir + '/model/haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(self.model_path)

    def find_faces(self, frame, ret):
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if frame.any()!=None:
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

        return frame, faces


if __name__ == '__main__':
    import cv2
    f = Face_Detector()
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        faceflow, faces = f.find_faces(frame, ret)

        # Display the resulting frame
        cv2.imshow('Video', faceflow)
        if len(faces) != 0:
            print("Aholla~!!")

        elif len(faces) == 0:
            print("move left and right to find people")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

