import cv2
from aip import AipBodyAnalysis
from robotpi_movement import Movement
from rev_cam import rev_cam
class gesture:

    APP_ID = '15558450'
    API_KEY = 'bcsRknl309ZL7KE7revBlmqU'
    SECRET_KEY = 'MRUkTuTP6ZFNx3Bjygzj6Uk4ecXZSWGR'

    def __init__(self):
        self.robotpi_movement = Movement()

    def get_image(self):
        # cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        cap = cv2.VideoCapture(0)
        cap.set(3, 320)
        cap.set(4, 240)
        while cap.isOpened():
            ret, image = cap.read()
            image = rev_cam(image)
            cv2.imshow('Video', image)
            if cv2.waitKey(1) & 0xFF == ord(' '):
                self.parseimage(image)
        cap.release()
        cv2.destroyAllWindows()

    def parseimage(self, image):
        filename = 'images/gesture.png'
        cv2.imwrite(filename, image)
        myimage = self.get_file_content(filename)
        client = AipBodyAnalysis(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        result = client.gesture(myimage)
        print(result)
        if result["result_num"] > 0:
            data = result['result']
            print(data[0]["classname"])
            if data[0]['classname'] == 'Heart_single' or 'Heart_1' or 'Heart_2' or 'Heart_3':
                self.robotpi_movement.turn_right(speed=10)
            if data[0]['classname'] == 'Fist':
                self.robotpi_movement.wave_hands()
            if data[0]['classname'] == 'Rock':
                self.robotpi_movement.play_sound(2, 16)
        else:
            print("暂无结果")
            self.robotpi_movement.play_sound(2, 4)

    def get_file_content(self, filepath):
        with open(filepath, 'rb') as fp:
            return fp.read()

if __name__ == '__main__':
    gesture = gesture()
    gesture.get_image()


