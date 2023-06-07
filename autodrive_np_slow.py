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

def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    front_cam.set(3, 160)
    front_cam.set(4, 120)
    back_cam = cv2.VideoCapture('/dev/video3')
    # set back_cam resolution to 160*120
    back_cam.set(3, 160)
    back_cam.set(4, 120)

    speed_pid = PID(Kp=0, Ki=0, Kd=0, outmax=50, outmin=0)
    turn_pid = PID(Kp=0, Ki=0, Kd=0, outmax=100, outmin=-100)
    robot = robotPi()

   
    start_time = time.time()  # 开始时间
    obszone_time = 11  # 越过障碍区的时间
    now_time = start_time  # 当前时间
    enter_stop_zone = False  # 是否进入停止区
    banner_adjust = False  # 是否调整靶子
    stop_count = 0
    flagr = 0
    i = 0.0
    adj = False
    robot.movement.reset()

    while True:
        if sys.stdin.read(1) == ' ':
            break
    start_time = time.time()
    while time.time() - start_time < 2.0:
        
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
        print("P0:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        if diff > 300:
            print("left")
            robot.movement.left_ward(speed=0, turn=180, times=400)
        elif diff < -300:
            print("right")
            robot.movement.right_ward(speed=0, turn=-180, times=100)
        else:    
            print("forward")

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
    
    # 未通过障碍区
    while now_time - start_time < 9.0: 
        _, frame = front_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[65:110, :]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
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
        print("P1:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        if diff > 150:
            print("left")
            robot.movement.left_ward(angle=0,speed=50, turn=180, times=200)
        elif diff < -150:
            print("right")
            robot.movement.right_ward(angle=0,speed=50, turn=-180, times=200)
        else:
            robot.movement.move_forward(speed=50, times=200)
            print("forward")
        now_time = time.time()


        # 进入障碍区
    while now_time - start_time < 11.0: 
        _, frame = front_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        if now_time - start_time < 9.5:
            frame = frame[70:115, :]
            print("--",end=" ")
        else:
            frame = frame[45:90, :]
            print("++",end=" ")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
        kernel = np.ones((7,7),np.uint8)
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
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
        print("P2:left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        if diff > 300:
            print("left")
            robot.movement.left_ward(angle=0,speed=50, turn=180, times=200)
        elif diff < -300:
            print("right")
            robot.movement.left_ward(angle=0,speed=50, turn=-180, times=200)
        else:
            robot.movement.move_forward(speed=50, times=200)
            print("forward")
        now_time = time.time()
    # 通过障碍区
    while time.time() - start_time < 13.0:
        _, frame = front_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[60:105, :]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5),np.uint8)
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
        #cv2.imshow("binary", binary)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 非0元素转换为1
        binary[binary != 0] = 1
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
        if diff > 300:
            print("left")
            robot.movement.left_ward(angle=0,speed=50, turn=200, times=200)
        elif diff < -300:
            print("right")
            robot.movement.left_ward(angle=0,speed=50, turn=-180, times=200)
        else:
            robot.movement.move_forward(speed=50, times=200)
            print("forward")

    #robot.movement.hit()
    # 来到停止区
    while enter_stop_zone is False:
        _, frame = front_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[65:110, :]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        #cv2.imshow("binary", binary)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 非0元素转换为1
        binary[binary != 0] = 1
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
        #print("left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        print(left_count,right_count,up_count,down_count,up_ratio,down_ratio)
        if up_ratio >= 2.8 and down_ratio >= 1.0:
            enter_stop_zone = True
        robot.movement.move_forward(speed=50, times=120)

        # if diff > 500:
        #     if up_ratio > 1.3:
        #         robot.movement.move_forward(speed=150, times=200)
        #         print("forward")
        #     else:
        #         print("left")
        #         robot.movement.left_ward(speed=150, turn=250, times=200)
        # elif diff < -500:
        #     print("right")
        #     robot.movement.left_ward(speed=150, turn=-250, times=200)
        # else:
        #     robot.movement.move_forward(speed=150, times=200)
        #     print("forward")
    
    robot.movement.prepare()
    robot.movement.move_forward(speed=25, times=600)
    time.sleep(1)
    now_time = time.time()
    # 打靶
    while time.time() - now_time < 3.0:
        _, frame = back_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[35:80, :]
        frame = cv2.flip(frame,1)
        frame = cv2.flip(frame,0)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        ret, binary = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
        #cv2.imshow("binary", binary)
        # 转换为二维数组
        binary = np.array(binary, dtype=np.uint8)
        # 非0元素转换为1
        binary[binary != 0] = 1
        # 分割成上下左右四部分
        left = binary[:, :width // 2]
        right = binary[:, width // 2:]
        # 计算上下左右四部分的白色像素点个数
        left_count = np.sum(left == 1)
        right_count = np.sum(right == 1)
        # 计算左右两部分的白色像素点个数之差
        # 计算比例
        if left_count == 0:
            left_ratio = 0
            if adj is False:
                robot.movement.right_ward(angle=270,speed=15, turn=0, times=80)

        else :
            left_ratio = 3600 / left_count
            if left_ratio < 6:
                robot.movement.left_ward(angle=95,speed=15, turn=0, times=80)
                adj = True
        # 输出信息
        print(left_count,left_ratio)
    robot.movement.hit()
    robot.movement.move_forward(speed=25, times=550)


    #time.sleep(0.1)
    #robot.movement.move_forward(speed=30, times=250)
    print(time.time() - start_time)

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
