# 　　　　　      　 　_ooOoo_
# 　　　　　      　　o8888888o
# 　　　　　      　　88" . "88
# 　　　　      　　　(| -_- |)
# 　　　　      　　　O\  =  /O
# 　　　　      　____/`---'\____
# 　　　　      .'  \\|     |//  `.
# 　　      　/  \\|||  :  |||//  \
# 　　       /  _||||| -:- |||||-  \
# 　　       |   | \\\  -  /// |   |
# 　　       | \_|  ''\---/''  |   |
# 　       　\  .-\__  `-`  ___/-. /
# 　       ___`. .'  /--.--\  `. . __
# 　    ."" '<  `.___\_<|>_/___.'  >'"".
# 　   | | :  `- \`.;`\ _ /`;.`/ - ` : | |
# 　   \  \ `-.   \_ __\ /__ _/   .-` /  /
# ======`-.____`-.___\_____/___.-`____.-'======
# 　　　　　　　　      `=---='
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 　　　　　　　　佛祖保佑 代码无bug


import numpy as np
import time
import tensorflow as tf
from robotPi import robotPi
import cv2
import os
import subprocess
from pid import PID
subprocess.check_call("v4l2-ctl -d /dev/video0 -c contrast=85 -c saturation=0 -c sharpness=13", shell=True)
# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 480
height = 180
channel = 1
inference_path = tf.Graph()
filepath = os.getcwd() + '/model/auto_drive_model/-205'

resized_height = int(width * 0.75)

temp_image = np.zeros(width * height * channel, 'uint8')


def circles_xyr(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=30, minRadius=10, maxRadius=100)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, radius = i[0], i[1], i[2]
            return x, y, radius
    else:
        return None, None, None


def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    front_cam.set(3, 160)
    front_cam.set(4, 120)
    back_cam = cv2.VideoCapture('/dev/video1')
    # set back_cam resolution to 160*120
    back_cam.set(3, 160)
    back_cam.set(4, 120)

    speed_pid = PID(Kp=0, Ki=0, Kd=0, outmax=50, outmin=0)
    turn_pid = PID(Kp=0, Ki=0, Kd=0, outmax=100, outmin=-100)
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

        start_time = time.time()  # 开始时间
        obszone_time = 21  # 越过障碍区的时间
        now_time = start_time  # 当前时间
        enter_stop_zone = False  # 是否进入停止区

        while now_time - start_time < obszone_time:
            ret, frame = front_cam.read()
            # 计算缩放比例
            frame = cv2.resize(frame, (width, resized_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # slice the lower part of a frame
            res = frame[resized_height - height:, :]

            # cv2.imshow("frame", res)
            # cv2.waitKey(1)
            frame = np.array(res, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)
            now_time = time.time()  # 更新当前时间
            # if now_time - start_time < 2.5:
            #     robot.movement.move_forward(speed=25, times=120)
            #     continue

            if value == 0:
                print("forward")
                robot.movement.move_forward(speed=26, times=120)
            elif value == 1:
                print("left")
                robot.movement.left_ward(speed=22, turn=125, times=120)
            elif value == 2:
                print("right")
                robot.movement.right_ward(speed=22, turn=-125, times=120)
            elif value == 3:
                print("stop sign, but did not pass the obszone, so forward")
                robot.movement.move_forward(speed=22, times=120)
            else:
                continue

        while enter_stop_zone is False:
            ret, frame = back_cam.read()
            x, y, r = circles_xyr(frame)
            if x is None or y is None or r is None:
                continue
            print('x=', x, 'y=', y, 'r=', r)
            turn = turn_pid.update(input_value=x, setpoint=80, dt=1)
            speed = speed_pid.update(input_value=r, setpoint=40, dt=1)

            robot.movement.move_forward(speed=speed, turn=turn, times=120)

            if r > 40:
                enter_stop_zone = True

        # hit the target
        robot.movement.hit()
        time.sleep(1)
        robot.movement.move_forward(speed=25, times=500)


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
