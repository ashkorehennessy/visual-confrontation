import cv2
import multiprocessing
import time
import sys
import signal
import subprocess
import numpy as np
from robotPi import robotPi
from pid import PID
from mynparr import Mynparr


def signal_handler(handler_signal, handler_frame):
    # SIGINT handler
    robot = robotPi()
    robot.movement.reset()
    exit(0)


def videocap(videocap_image, videocap_image_ok):
    # subprocess.check_call("v4l2-ctl -d /dev/video0 -c contrast=55 -c saturation=0 -c sharpness=5", shell=True)
    video = cv2.VideoCapture('/dev/video0')
    # set camera resolution
    video.set(3, 160)
    video.set(4, 120)
    ret, videocap_image.value = video.read()
    # if video is not opened, raise error
    if not ret:
        raise Exception("video error")
    # let camera be steady
    for _ in range(10):
        video.read()
    print("video ok")
    # start video capture
    while True:
        ret, videocap_image.value = video.read()
        if ret is False:
            # use blank image instead
            videocap_image.value = np.zeros((160, 120, 3), np.uint8)
            # reconnect to camera
            video.release()
            time.sleep(0.1)
            print("reconnect to camera")
            subprocess.check_call("sudo modprobe -rf uvcvideo", shell=True)
            time.sleep(0.4)
            subprocess.check_call("sudo modprobe uvcvideo", shell=True)
            time.sleep(0.2)
            video = cv2.VideoCapture('/dev/video0')
            video.set(3, 160)
            video.set(4, 120)
            ret, videocap_image.value = video.read()
            print("video reconnected")
        videocap_image_ok.value = ret



def autopilot(autopilot_image, autopilot_video_ok):
    robot = robotPi()
    mynparr = Mynparr()

    # init PID
    start_pid = PID(Kp=2, Kd=0, outmax=400, outmin=-400)
    end_pid = PID(Kp=0.15, Kd=0.01, outmax=200, outmin=-200)

    # flags
    part = 1
    start_toward = 0
    start_ready = 0
    process_frame = True

    # time and counter
    start_time = time.time()
    now_time = start_time
    part1_time = 0.0
    time_offset = 0.0
    frame_count = 0
    part2_count = 0
    second_diff = 0

    def part1():
        """part1: start line"""
        nonlocal start_ready
        nonlocal second_diff
        mynparr.crop_top = 75
        mynparr.crop_bottom = 120
        pid_output = start_pid.Calc(mynparr.diff, 0)
        robot.movement.any_ward(speed=0, turn=-pid_output, times=200)
        if first_diff > 200:
            start_ready = 1
        if abs(mynparr.diff - first_diff) > 5:
            if second_diff == 0:
                second_diff = mynparr.diff
            start_ready += 1
        if abs(mynparr.diff - first_diff) > 300:
            start_ready += 2
        if -400 < first_diff < 400:
            start_ready += 1
        if start_ready > 1:
            mynparr.crop_top = 55
            mynparr.crop_bottom = 100
            nonlocal part1_time
            nonlocal start_toward
            nonlocal time_offset
            part1_time = now_time - start_time
            # predict start toward
            if first_diff < -150:
                print(second_diff, first_diff)
                if second_diff - first_diff < 100:
                    if abs(mynparr.diff) > 20:
                        start_toward = 0
                    else:
                        start_toward = 1
                else:
                    start_toward = 2
            elif -150 <= first_diff <= 150:
                mynparr.process(autopilot_image.value)
                if mynparr.diff < -150:
                    start_toward = 3
                else:
                    start_toward = 4
            elif first_diff > 150:
                mynparr.process(autopilot_image.value)
                print(second_diff, first_diff)
                if mynparr.diff > 2200:
                    robot.movement.any_ward(angle=0, speed=150, turn=-230, times=200)
                    start_toward = 5
                else:
                    start_toward = 6
            time_offset = time_offsets[start_toward]
            print("part1 finished, time: ", part1_time)
            return 2
        return 1

    def part2():
        """part2: before obstacle zone"""
        nonlocal part2_count
        pid_output = start_pid.Calc(mynparr.diff, 0)
        if part2_count < 10:
            if start_toward == 0:
                if pid_output > 0:
                    pid_output = 0
                    print("reset pid_output")
                robot.movement.any_ward(angle=25, speed=150, turn=-pid_output, times=200)
            elif start_toward == 2:
                if pid_output > 0:
                    pid_output = 0
                    print("reset pid_output")
                robot.movement.any_ward(angle=18, speed=150, turn=-pid_output, times=200)
            elif start_toward == 3:
                robot.movement.any_ward(angle=0, speed=150, turn=-pid_output-180, times=200)
            elif start_toward == 4:
                robot.movement.any_ward(angle=-10, speed=150, turn=-pid_output-250, times=200)
            elif start_toward == 5:
                robot.movement.any_ward(angle=0, speed=150, turn=-pid_output-230, times=200)
            elif start_toward == 6:
                robot.movement.any_ward(angle=0, speed=150, turn=-pid_output-230, times=200)
            else:
                robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        else:
            robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        part2_count += 1
        if now_time - start_time > 3.9 + time_offset:
            mynparr.crop_top = 60
            mynparr.crop_bottom = 105
            mynparr.threshold = 105
            mynparr.morphology = True
            print("part2 finished")
            return 3
        return 2

    def part3():
        """part3: entering obstacle zone"""
        pid_output = start_pid.Calc(mynparr.diff, 0)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 4.4 + time_offset:
            mynparr.crop_top = 45
            mynparr.crop_bottom = 90
            print("part3 finished")
            return 4
        return 3

    def part4():
        """part4: leaving obstacle zone"""
        pid_output = start_pid.Calc(mynparr.diff, 0)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 6.0 + time_offset:
            mynparr.crop_top = 25
            mynparr.crop_bottom = 70
            mynparr.threshold = 100
            robot.movement.prepare()
            print("part4 finished")
            return 5
        return 4

    def part5():
        """part5: before end line"""
        nonlocal process_frame
        pid_output = end_pid.Calc(mynparr.left_white_pixel, 2450)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 7.4 + time_offset:
            mynparr.crop_top = 75
            mynparr.crop_bottom = 120
            mynparr.threshold = 155
            robot.movement.draw()
            mynparr.morphology = False
            process_frame = False
            print("part5 finished")
            return 6
        return 5

    def part6(_frame):
        """part6: end line"""
        robot.movement.move_forward(speed=150, times=200)
        _frame = _frame[mynparr.crop_top:mynparr.crop_bottom, :]
        _, binary = cv2.threshold(_frame, mynparr.threshold, 1, cv2.THRESH_BINARY)
        for i in range(15, 0, -1):
            if np.sum(binary[(i - 1) * 3: i * 3, :]) < 440:
                print("line detect in:", i)
                if i > 5:
                    end_delay = end_delays[i]
                    robot.movement.move_forward(speed=150, times=end_delay)
                    print("part6 finished")
                    print("end delay: ", end_delay, i)
                    return 7
        return 6

    # part functions
    part_functions = {
        1: part1,
        2: part2,
        3: part3,
        4: part4,
        5: part5,
        6: part6
    }

    # time offset for different start toward
    time_offsets = {
        0: 0.00,
        1: 0.35,
        2: 0.05,
        3: 0.00,
        4: -0.10,
        5: 0.00,
        6: 0.05
    }

    # end delays for different i
    end_delays = {
        6: 191,
        7: 175,
        8: 161,
        9: 153,
        10: 140,
        11: 100,
        12: 100,
        13: 100,
        14: 100,
        15: 100
    }

    # the action before start
    robot.movement.reset()

    # the crop area of part 1
    mynparr.crop_top = 75
    mynparr.crop_bottom = 120
    mynparr.process(autopilot_image.value)
    first_diff = mynparr.diff

    while part < 7:
        # check if new frame is ready
        if autopilot_video_ok.value == 1:
            frame = autopilot_image.value
            autopilot_video_ok.value = 0
        else:
            continue

        # process frame
        if process_frame:
            mynparr.process(frame)
            frame_count += 1

        # update now time
        now_time = time.time()

        # run part
        part_function = part_functions.get(part)
        if process_frame:
            part = part_function()
        else:
            part = part_function(frame)

    # print info
    print("total time: ", now_time - start_time)
    print("fps: ", frame_count / (now_time - start_time))
    print("start toward: ", start_toward)
    print("part1 time: ", part1_time)
    print("first diff: ", first_diff)
    print("second diff: ", second_diff)
    print("time offset: ", time_offset)
    mynparr.record_save = True
    mynparr.process(autopilot_image.value)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    image = multiprocessing.Manager().Value(cv2.CV_8UC3, None)
    video_ok = multiprocessing.Manager().Value('i', 0)
    videocap_proc = multiprocessing.Process(target=videocap, args=(image, video_ok))
    autopilot_proc = multiprocessing.Process(target=autopilot, args=(image, video_ok))
    videocap_proc.start()
    print("wait for video ok")
    while video_ok.value == 0:
        time.sleep(0.1)
    while True:
        if sys.stdin.read(1) == ' ':
            break
    autopilot_proc.start()
    autopilot_proc.join()
    videocap_proc.join()
