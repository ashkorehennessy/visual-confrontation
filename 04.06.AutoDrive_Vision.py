import numpy as np
import time
import tensorflow as tf
from robotPi import robotPi
from color_bounding import ColorBounding
from Welcome_face_detector import Face_Detector
from barcode_scanner_video import QRscan

import cv2
import os

# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 180
height = 80
channel = 1
# 要寻找的目标 1: Color; 2: QR Code; 3: Face
tar = 2
inference_path = tf.Graph()
filepath = os.getcwd() + '/model/auto_drive_model/-49'
temp_image = np.zeros(width * height * channel, 'uint8')


def hit():
    pass


def find_qr(frame):
    qr = QRscan()
    name, bbox = qr.scan(frame)
    if "sword" in name:
        return bbox
    else:
        return -1, -1, 0, 0


def going(x, y):
    # 目标偏移的最大宽度与高度
    robot = robotPi()
    center_x, center_y = int(640 / 2), int(480 / 2)
    robot.movement.move_forward()
    vector_x = center_x - x
    vector_y = center_y - y
    if vector_x > 20:
        robot.movement.turn_right()
    if vector_x < -20:
        robot.movement.turn_left()


def target(number):
    '''
    Searching for target accroding to given number.
    :param number: 1: Color; 2: QR Code; 3: Face
    :return: None
    '''
    robot = robotPi()
    cap = cv2.VideoCapture(0)
    color_bounding = ColorBounding()
    x, y, w, h = -1, -1, 0, 0
    it = 0
    T = False  # 是否找到过目标
    while cap.isOpened():
        ret, frame = cap.read()
        # Finding
        if number == 1:
            robot.movement.turn_right(5, 500)
            x, y, w, h = color_bounding.bounding(frame)
            if x == 0 and y == 0:
                x, y = -1, -1
            else:
                T = True
        elif number == 2:
            print("finding QR code.")
            cv2.imshow("frame", frame)
            cv2.waitKey(1)
            robot.movement.turn_right(5, 500)
            x, y, w, h = find_qr(frame)
            if x !=-1:  # 检测到目标，累加器清零
                T = True
                it = 0
            elif x == -1:  # 未检测到目标，累加器加一
                it += 1
        elif number == 3:
            f = Face_Detector()
            _, faces = f.find_faces(frame, ret)
            if len(faces) != 0:
                x, y, w, h = faces
                T = True
        # Going to target
        going(x + w/2, y + h/2)
        if it == 100 and T is True:  # 找到目标后，连续100帧丢失目标，认为已经到达目的地
            print("hit.")
            hit()
            break


def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    cap = cv2.VideoCapture(0)
    robot = robotPi()

    with tf.Session(graph=inference_path) as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        saver = tf.train.import_meta_graph(filepath + '.meta')
        saver.restore(sess, filepath)

        tf_X = sess.graph.get_tensor_by_name('input:0')
        pred = sess.graph.get_operation_by_name('pred')
        number = pred.outputs[0]
        prediction = tf.argmax(number, 1)

        while cap.isOpened():
            ret, frame = cap.read()
            resized_height = int(width * 0.75)
            # 计算缩放比例
            frame = cv2.resize(frame, (width, resized_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # slice the lower part of a frame
            res = frame[resized_height - height:, :]
            frame = np.array(res, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)

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
                robot.movement.stop()
                break
    cap.release()
    cv2.destroyAllWindows()

    # Start find target
    target(tar)


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






