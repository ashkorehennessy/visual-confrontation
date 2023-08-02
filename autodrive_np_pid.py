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
#import tensorflow as tf
from robotPi import robotPi
import cv2
import sys
import os
import subprocess
import multiprocessing
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
#inference_path = tf.Graph()
#filepath = os.getcwd() + '/model/0000_20230606_123822_small/-188'

resized_height = int(width * 0.75)

temp_image = np.zeros(width * height * channel, 'uint8')

def auto_pilot(image):
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    # front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    # front_cam.set(3, 160)
    # front_cam.set(4, 120)
    # back_cam = cv2.VideoCapture('/dev/video2')
    # set back_cam resolution to 160*120
    # back_cam.set(3, 160)
    # back_cam.set(4, 120)

    pid0 = PID(Kp=0.5, Kd=0, outmax=400, outmin=-400)
    pid1 = PID(Kp=2, Kd=0, outmax=400, outmin=-400)
    pid2 = PID(Kp=0.15, Kd=0.05, outmax=200, outmin=-200)
    robot = robotPi()

   
    start_time = time.time()  # 开始时间
    now_time = start_time  # 当前时间
    enter_stop_zone = False  # 是否进入停止区
    banner_adjust = False  # 是否调整靶子
    stop_count = 0
    flag = 0
    flagr = False
    flagl = False
    flag4 = False
    flag4et = False
    first_diff = 114514
    time_offset = 0.0
    thr = 120
    adj = 0
    last_image = None
    robot.movement.reset()
    start_time = time.time()
    while adj < 40:
        frame = image.value
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[75:, :]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #cv2.imshow("gray", gray)
        # 二值化

        ret, binary = cv2.threshold(gray, thr, 255, cv2.THRESH_BINARY)
        #cv2.imshow("binary", binary)
        binary[binary != 0] = 1
        cv2.waitKey(1)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 非0元素转换为1
        # 分割成左右两部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        # 计算左右两部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        # 计算左右两部分的白色像素点个数之差
        diff = left_count - right_count
        if first_diff == 114514:
            first_diff = diff
        # 输出信息
        print("P0:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        pid_output = pid0.update(diff, 0)
        if pid_output > 300:
            flagl = True
        spd = int(50 - (abs(diff) / 50)) 
        ang = int(-diff/15)
        if ang < 0:
            ang = max(-30, ang)
            ang = 360 + ang
            flagr = True
        else:
            ang = min(30, ang)
        if abs(diff) < 30:
            if flagr is False:
                pid_output = -100
                spd = 50
            else:
                spd = 50
                adj += 40
        robot.movement.left_ward(angle=ang, speed=spd, turn=-pid_output, times=150) 
        #robot.movement.left_ward(angle=ang, speed=0, turn=0, times=150)
        print(pid_output,spd,ang)
        if abs(diff) < 200:
            adj += 1
    time_offset = time.time() - start_time
    orig_time_offset = time_offset
    if time_offset > 0.5:
        if flagl == True:
            time_offset = 0.35
        else:
            time_offset = 0.3
    elif time_offset > 0.4:
        time_offset = 0.2
    elif time_offset > 0.3:
        time_offset = 0.20
    elif time_offset > 0.25:
        time_offset = 0.1
    elif time_offset > 0.1:
        time_offset = 0.05
    # 未通过障碍区
    while now_time - start_time < 3.8 + time_offset: 
        frame = image.value
        if (image.value == last_image).all():
            continue
        last_image = image.value
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[55:100, :]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化 
        ret, binary = cv2.threshold(gray, thr, 255, cv2.THRESH_BINARY)
        #cv2.imshow("binary", binary)
        binary[binary != 0] = 1
        cv2.waitKey(1)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 分割成左右两部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        # 计算左右两部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        # 计算左右两部分的白色像素点个数之差
        diff = left_count - right_count
        if flag4et == False and orig_time_offset < 0.23 and first_diff < 200:
            flag4et = True
            if diff > -30 and flag4 == False:
                time_offset -= 0.15
                flag4 = True
        # 输出信息
        print("P1:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        pid_output = pid1.update(diff, 0)
        robot.movement.left_ward(speed=150, turn=-pid_output, times=200)
        print("pid_output",pid_output)
        now_time = time.time()

        # 进入障碍区
    while now_time - start_time < 5.8 + time_offset: 
        frame = image.value
        if (image.value == last_image).all():
            continue
        last_image = image.value
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        if now_time - start_time < 4.4 + time_offset:
            frame = frame[55:100, :]
            print("--",end=" ")
        else:
            frame = frame[45:90, :]
            print("++",end=" ")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, thr*0.9, 255, cv2.THRESH_BINARY)
        kernel = np.ones((7,7),np.uint8)
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
        #cv2.imshow("binary", binary)
        binary[binary != 0] = 1
        cv2.waitKey(1)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 分割成左右两部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        # 计算左右两部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        # 计算左右两部分的白色像素点个数之差
        diff = left_count - right_count
        # 输出信息
        print("P2:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        pid_output = pid1.update(diff, 0)
        robot.movement.left_ward(speed=150, turn=-pid_output, times=200)
        print("pid_output",pid_output)
        now_time = time.time()
    # 通过障碍区
    robot.movement.prepare()
    while time.time() - start_time < 7.4 + time_offset:
        frame = image.value
        if (image.value == last_image).all():
            continue
        last_image = image.value
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[25:70, :]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值
        ret, binary = cv2.threshold(gray, thr*0.83, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5),np.uint8)
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
        #cv2.imshow("binary", binary)
        binary[binary != 0] = 1
        cv2.waitKey(1)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 非0元素转换为1
        # 分割成上下左右四部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        # 计算上下左右四部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        # 计算左右两部分的白色像素点个数之差
        diff = left_count - right_count
        # 输出信息
        print("left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        pid_output = pid2.update(left_count,2400)
        print("pid_output: ",pid_output)
        robot.movement.left_ward(angle=0,speed=150,turn=-pid_output,times=200)

    robot.movement.draw()
    # 来到停止区
    down_count = 0
    while enter_stop_zone is False:
        frame = image.value
        if (image.value == last_image).all():
            continue
        last_image = image.value
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[75:, :]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, thr*1.125, 255, cv2.THRESH_BINARY)
        #cv2.imshow("binary", binary)
        binary[binary != 0] = 1
        cv2.waitKey(1)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 分割成上下左右四部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        up = binary[:height // 2, :]
        down = binary[height // 2:, :]
        # 计算上下左右四部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        up_count = np.sum(up == 1)
        down_count = np.sum(down == 1)
        # 计算左右两部分的白色像素点个数之差
        diff = left_count - right_count
        # 计算比例
        up_ratio = 3600 / up_count
        down_ratio = 3680 / down_count
        # 输出信息
        print(left_count,right_count,up_count,down_count,up_ratio,down_ratio)
        if down_count < 2400:
            enter_stop_zone = True
        robot.movement.move_forward(speed=30, times=200)
    robot.movement.move_forward(speed=50, times=360)
    time.sleep(0.36)
    print("total time:", time.time() - start_time)
    print("time offset:", time_offset)
    print("orig time offset:", orig_time_offset)
    print("flag4 stat:", flag4)
    

def videocap(image,video_ok):
    front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    front_cam.set(3, 160)
    front_cam.set(4, 120)
    video_ok.value, image.value = front_cam.read()
    frames = 0
    while True:
        ret, image.value = front_cam.read()



if __name__ == '__main__':
    image = multiprocessing.Manager().Value(cv2.CV_8UC3, None)
    video_ok = multiprocessing.Manager().Value('i', 0)
    stop_event = multiprocessing.Event()
    proc1 = multiprocessing.Process(target=videocap, args=(image,video_ok))
    proc2 = multiprocessing.Process(target=auto_pilot, args=(image,))
    proc1.start()
    print("wait for video ok")
    while video_ok.value == 0:
        time.sleep(0.1)
    print("video ok")
    while True:
        if sys.stdin.read(1) == ' ':
            break
    proc2.start()
    proc2.join()
    stop_event.set()
    proc1.join()
