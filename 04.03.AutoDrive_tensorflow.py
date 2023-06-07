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
import sys
import os
import subprocess
from rev_cam import rev_cam
from pid import PID
#subprocess.check_call("v4l2-ctl -d /dev/video2 -c contrast=55 -c saturation=0 -c sharpness=5", shell=True)
# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 160
height = 45
channel = 1
inference_path = tf.Graph()
filepath = os.getcwd() + '/model/0000_20230606_123822_small/-188'

resized_height = int(width * 0.75)

temp_image = np.zeros(width * height * channel, 'uint8')

def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    front_cam.set(3, 160)
    front_cam.set(4, 120)
    back_cam = cv2.VideoCapture('/dev/video0')
    # set back_cam resolution to 160*120
    #back_cam.set(3, 160)
    #back_cam.set(4, 120)

    speed_pid = PID(Kp=0, Ki=0, Kd=0, outmax=50, outmin=0)
    turn_pid = PID(Kp=0, Ki=0, Kd=0, outmax=100, outmin=-100)
    robot = robotPi()

    def back():
        robot.movement.move_forward(speed=25, times=4000)
        time.sleep(4)
        robot.movement.left_ward(angle=90, speed=25, turn=0, times=8000)
        time.sleep(8)
        robot.movement.left_ward(angle=180, speed=25, turn=0, times=4000)
        time.sleep(4)
        robot.movement.left_ward(angle=270, speed=25, turn=0, times=800)
        time.sleep(1)
        robot.movement.left_ward(angle=0, speed=0, turn=-180, times=1000)
        time.sleep(1)
        robot.movement.left_ward(angle=0, speed=25, turn=0, times=2000)



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
        obszone_time = 11  # 越过障碍区的时间
        now_time = start_time  # 当前时间
        enter_stop_zone = False  # 是否进入停止区
        banner_adjust = False  # 是否调整靶子
        stop_count = 0
        flagr = 0
        #robot.movement.prepare()

        while True:
            if sys.stdin.read(1) == ' ':
                break
        start_time = time.time()
        while time.time() - start_time < 0.6:
            
            _, frame = front_cam.read()
            # 计算缩放比例
            #frame = cv2.resize(frame, (width, resized_height))
            frame = frame[resized_height - height:, :]

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("gray", gray)
            # 二值化
            ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            #cv2.imshow("binary", binary)
            # 转换为二维数组
            binary = np.array(binary, dtype=np.uint8)
            # 非0元素转换为1
            binary[binary != 0] = 1
            # 分割成左右两部分
            left = binary[:, :width // 2]
            right = binary[:, width // 2:]
            # 计算左右两部分的白色像素点个数
            left_count = np.sum(left == 1)
            right_count = np.sum(right == 1)
            # 计算左右两部分的白色像素点个数之差
            diff = left_count - right_count
            # 输出信息
            print("left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
            if diff > 300:
                print("left")
                robot.movement.left_ward(speed=0, turn=320, times=160)
            elif diff < -300:
                print("right")
                robot.movement.left_ward(speed=0, turn=-320, times=160)
            else:
                print("ready!")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        # 未通过障碍区
        while now_time - start_time < obszone_time:
            ret, frame = front_cam.read()
            # 计算缩放比例
            #frame = cv2.resize(frame, (width, resized_height))
            #frame = cv2.flip(frame,1)
            #frame = cv2.flip(frame,0)
            #frame = rev_cam(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #ret, frame = cv2.threshold(frame, 150, 255, cv2.THRESH_BINARY)

            # slice the lower part of a frame
            frame = frame[resized_height - height:, :]

            # cv2.imshow("frame", res)
            # cv2.waitKey(1)
            frame = np.array(frame, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)
            now_time = time.time()  # 更新当前时间


            if value == 0:
                print("forward")
                robot.movement.move_forward(speed=60, times=200)
                flagr = 0
            elif value == 1:
                print("left")
                robot.movement.left_ward(speed=55, turn=280, times=200)
                flagr = -1
            elif value == 2:
                print("right")
                flagr += 1
                if flagr > 1:
                    robot.movement.right_ward(speed=55, turn=-280, times=200)
                else:
                    robot.movement.move_forward(speed=60, times=200)
            else:
                print("stop sign, but forward")
                robot.movement.move_forward(speed=50, times=200)
                flagr = 0

        # 通过障碍区
        while enter_stop_zone is False:
            ret, frame = front_cam.read()
            # 计算缩放比例
            #frame = cv2.resize(frame, (width, resized_height))
            #frame = cv2.flip(frame,1)
            #frame = cv2.flip(frame,0)
            #frame = rev_cam(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # slice the lower part of a frame
            frame = frame[resized_height - height:, :]
            ret, frame = cv2.threshold(frame, 150, 255, cv2.THRESH_BINARY)


            # cv2.imshow("frame", res)
            # cv2.waitKey(1)
            frame = np.array(frame, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)
            now_time = time.time()  # 更新当前时间

            if value == 0:
                print("forward")
                robot.movement.move_forward(speed=60, times=200)
                flagr = 0
                stop_count = 0
            elif value == 1:
                print("left")
                robot.movement.left_ward(speed=55, turn=120, times=200)
                flagr = -1
                stop_count = 0
            elif value == 2:
                print("right")
                flagr += 1
                if flagr > 1:
                    robot.movement.right_ward(speed=55, turn=-120, times=200)
                else:
                    robot.movement.move_forward(speed=60, times=200)
                stop_count = 0
            elif value == 3:
                print("stop sign")
                robot.movement.right_ward(speed=50, turn=-60, times=200)
                flagr = 0
                stop_count += 1
                #enter_stop_zone = True
            else:
                robot.movement.move_forward(speed=50, times=200)
                flagr = 0 
                stop_count = 0
            if stop_count == 2:
                enter_stop_zone = True
            if time.time() - start_time < 12:
                stop_count = 0

        robot.movement.prepare()
        start_time = time.time()
        while time.time() - start_time < 1.5:
            ret, frame = front_cam.read()
            # 计算缩放比例
            #frame = cv2.resize(frame, (width, resized_height))
            #frame = cv2.flip(frame,1)
            #frame = cv2.flip(frame,0)
            #frame = rev_cam(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # slice the lower part of a frame
            frame = frame[resized_height - height:, :]

            # cv2.imshow("frame", res)
            # cv2.waitKey(1)
            frame = np.array(frame, dtype=np.float32)
            value = prediction.eval(feed_dict={tf_X: np.reshape(frame, [-1, height, width, channel])})
            print('img_out:', value)
            now_time = time.time()  # 更新当前时间

            if value == 5:
                print("banner left")
                robot.movement.left_ward(angle=90, speed=10, turn=20, times=100)
                banner_adjust = True
            elif value == 6:
                print("banner right")
                robot.movement.left_ward(angle=270, speed=10, turn=0, times=100)
                banner_adjust = True
            #elif value == 0:
            #    if banner_adjust is False:
            #        print("banner left")
            #        robot.movement.left_ward(angle=90 ,speed=15, turn=40, times=1000)
            #        time.sleep(1)
            #        banner_adjust = True
            elif value == 1:
                print("banner left")
                robot.movement.left_ward(angle=90 ,speed=20, turn=50, times=100)
 
            else:
                print("banner hit ready")

       # hit the target
        #time.sleep(1)
        #robot.movement.prepare()

        robot.movement.move_forward(speed=25, times=500)
        robot.movement.hit()
        robot.movement.move_forward(speed=25, times=1800)
        #back()


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
