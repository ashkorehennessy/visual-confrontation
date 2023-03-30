import numpy as np
import time
from robotPi import robotPi
import cv2
from rev_cam import rev_cam
# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 480
height = 180
channel = 1


temp_image = np.zeros(width * height * channel, 'uint8')
model = cv2.ml.ANN_MLP_load('mlp_xml/mlp.xml')


def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    cap = cv2.VideoCapture(0)
    robot = robotPi()
    while cap.isOpened():
        ret, frame = cap.read()
        frame = rev_cam(frame)
        resized_height = int(width * 0.75)
        # 计算缩放比例
        frame = cv2.resize(frame, (width, resized_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # slice the lower part of a frame
        res = frame[resized_height - height:, :]
        cv2.imshow("frame", res)
        cv2.waitKey(1)
        frame = np.array(res, dtype=np.float32)
        _, prediction = model.predict(frame.reshape(1, width * height))
        value = prediction.argmax(-1)
       

        if value == 0:
            print("forward")
            robot.movement.move_forward(times=300)
        elif value == 1:
            print("left")
            robot.movement.left_ward()
        elif value == 2:
            print("right")
            robot.movement.right_ward()
        elif value == 3:
            print("stop sign")
            robot.movement.hit()
        elif value == 4:
            print("Banner forward")
                # robot.movement.move_forward(times=300)				
        elif value == 5:
            print("Banner left")
                # robot.movement.left_ward()				
        elif value == 6:
            print("Banner right")	
                # robot.movement.right_ward()				
        elif cv2.waitKey(1) & 0xFF ==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    ###############################################################
    # startTime=datetime.datetime.now()
    ###############################################################
    auto_pilot()
    # time.sleep(0.5)
    ##############################################################
    # endTime=datetime.datetime.now()
    # print(endTime-startTime)
    ###############################################################






