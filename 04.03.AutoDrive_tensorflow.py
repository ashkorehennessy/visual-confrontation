import numpy as np
import time
import tensorflow as tf
from robotPi import robotPi
import cv2
import os
from rev_cam import rev_cam
# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 480
height = 180
channel = 1
inference_path = tf.Graph()
filepath = os.getcwd() + '/model/auto_drive_model/-476'

resized_height = int(width * 0.75)

temp_image = np.zeros(width * height * channel, 'uint8')


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

        start_time = time.time() #开始时间
        obszone_time = 27 #越过障碍区的时间

        while cap.isOpened():
            ret, frame = cap.read()
            frame = rev_cam(frame)
            # 计算缩放比例
            frame = cv2.resize(frame, (width, resized_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # slice the lower part of a frame
            res = frame[resized_height - height:, :]
            #cv2.imshow("frame", res)
            #cv2.waitKey(1)
            frame = np.array(res, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)
            if time.time() - start_time < 1:
                robot.movement.move_forward(speed=25, times=120)
                continue

            if value == 0:
                if time.time() - start_time < obszone_time:
                    print("forward")
                    robot.movement.move_forward(speed=25, times=120)
                else:
                    print("forward")
                    robot.movement.move_forward(speed=25, times=120)
            elif value == 1:
                if time.time() - start_time < obszone_time:
                    print("left")
                    robot.movement.left_ward(speed=10, turn=150, times=120)
                else:
                    print("left")
                    robot.movement.left_ward(speed=23, turn=80, times=120)
            elif value == 2:
                if time.time() - start_time < obszone_time:
                    print("right")
                    robot.movement.right_ward(speed=10, turn=-180, times=120)
                else:
                    print("right")
                    robot.movement.right_ward(speed=23, turn=-80, times=120)
            elif value == 3:
                if time.time() - start_time < obszone_time:
                    print("stop sign, but did not pass the obszone, so forward")
                    robot.movement.move_forward(speed=30, times=150)
                else:
                    print("stop sign")
                    # robot.movement.hit()
            elif value == 4:
                if time.time() - start_time < obszone_time:
                    print("Banner forward, but did not pass the obszone, so forward")
                    robot.movement.move_forward(speed=20, times=120)
                else:
                    print("Banner forward")
                    # robot.movement.move_forward(times=300)				
            elif value == 5:
                if time.time() - start_time < obszone_time:
                    print("Banner left, but did not pass the obszone, so forward")
                    robot.movement.move_forward(speed=20, times=120)
                else:
                    print("Banner left")
                    # robot.movement.left_ward()				
            elif value == 6:
                if time.time() - start_time < obszone_time:
                    print("Banner right, but did not pass the obszone, so forward")
                    robot.movement.move_forward(speed=20, times=120)
                else:
                    print("Banner right")
                # robot.movement.right_ward()				
            #elif cv2.waitKey(1) & 0xFF ==ord('q'):
            #   break
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






