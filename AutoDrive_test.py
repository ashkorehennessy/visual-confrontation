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
#from robotPi import robotPi
import cv2
import sys
import os
#import subprocess
from rev_cam import rev_cam
from pid import PID

# 1:[1,0,0,0] 前
# 2:[0,1,0,0] 左
# 3:[0,0,1,0] 右
# 4:[0,0,0,1] 后


width = 160
height = 45
channel = 1
resized_height = int(width * 0.75)


def auto_pilot():
    # a = np.array(frame, dtype=np.float32)
    # _, prediction = model.predict(a.reshape(1, width * height))
    front_cam = cv2.VideoCapture('/dev/video0')
    # set front_cam resolution to 160*120
    front_cam.set(3, 160)
    front_cam.set(4, 120)
    back_cam = cv2.VideoCapture('/dev/video2')
    # set back_cam resolution to 160*120
    back_cam.set(3, 160)
    back_cam.set(4, 120)
    start_time = time.time()  # 开始时间
    obszone_time = 100  # 越过障碍区的时间
    now_time = start_time  # 当前时间
    enter_stop_zone = False  # 是否进入停止区
    banner_adjust = False  # 是否调整靶子
    ##robot.movement.prepare()



    # 未通过障碍区
    while now_time - start_time < obszone_time:
        _, frame = front_cam.read()
        # 计算缩放比例
        #frame = cv2.resize(frame, (width, resized_height))
        frame = frame[75:, :]
        #frame = cv2.flip(frame,1)
        #frame = cv2.flip(frame,0)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray", gray)
        # 二值化
        otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]
        ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        #kernel = np.ones((5,5),np.uint8)
        #binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel)
        cv2.imshow("binary", binary)
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
        left_ratio = 3600 / left_count
        right_ratio = 3600 / right_count
        up_ratio = 3600 / up_count
        down_ratio = 3600 / down_count
        # 输出信息
        #print("left_count:" + str(left_count) + " right_count:" + str(right_count) + " diff:" + str(diff) + " result:",end=" ")
        print(left_count,right_count,up_count,down_count,left_ratio,right_ratio,up_ratio,down_ratio)
           #print("forward")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



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
