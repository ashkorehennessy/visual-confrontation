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

    threshold_p1 = 120  # target: 3000
    threshold_p2 = 65
    threshold_p3 = 70  # target: 6100
    threshold_p5 = 86  # target: 2400
    threshold_p6 = 145  # target: 3260 high: 110 low: 155

    target_white_pixel = 2740

    end_delay_offset = 33


    # init PID
    start_pid = PID(Kp=2, Kd=0, outmax=400, outmin=-400)
    end_pid = PID(Kp=0.15, Kd=0, outmax=200, outmin=-200)

    # flags
    part = 1
    flag_specify_start_toward = False
    if len(sys.argv) == 1:
        start_toward = 0
    else:
        start_toward = int(sys.argv[1])
        if start_toward == 1:
            start_toward = 0
        flag_specify_start_toward = True
    start_ready = 0
    process_frame = True

    # time and counter
    start_time = time.time()
    now_time = start_time
    part1_time = 0.0
    part2_count = 0
    time_offset = 0.0
    frame_count = 0
    draw_count = 10
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
        if (start_ready > 1) or (now_time - start_time > 0.05):
            if second_diff == 0:
                second_diff = mynparr.diff
            mynparr.crop_top = 55
            mynparr.crop_bottom = 100
            nonlocal part1_time
            nonlocal start_toward
            nonlocal time_offset
            part1_time = now_time - start_time
            # predict start toward
            if first_diff < -350:
                print("second diff:" + str(second_diff) + "first diff" + str(first_diff))
                if second_diff - first_diff < 0:
                    if abs(mynparr.diff) > 20:
                        if not flag_specify_start_toward:
                            start_toward = 0
                    else:
                        if not flag_specify_start_toward:
                            start_toward = 1
                else:
                    if not flag_specify_start_toward:
                        start_toward = 2
            elif -350 <= first_diff <= 350:
                print("process extra frame")
                mynparr.process(autopilot_image.value)
                print("second diff:" + str(second_diff) + "first diff" + str(first_diff))
                if mynparr.diff < -150:
                    if not flag_specify_start_toward:
                        start_toward = 3
                else:
                    if not flag_specify_start_toward:
                        start_toward = 4
            elif first_diff > 350:
                print("second diff:" + str(second_diff) + "first diff" + str(first_diff))
                if mynparr.diff > 2200:
                    if not flag_specify_start_toward:
                        start_toward = 5
                else:
                    if not flag_specify_start_toward:
                        start_toward = 6
            time_offset = time_offsets[start_toward]
            mynparr.threshold = threshold_p2
            print("part1 finished, time: ", part1_time)
            print("start toward: ", start_toward)
            return 2
        return 1

    def part2():
        """part2: before obstacle zone"""
        nonlocal part2_count
        nonlocal start_toward
        pid_output = start_pid.Calc(mynparr.diff, 0)
        if part2_count < 20:
            if start_toward == 0 or start_toward == 1:
                if part2_count < 1:
                    robot.movement.any_ward(angle=0, speed=0, turn=-400, times=200)
                else:
                    robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 120, times=200)
            elif start_toward == 2:
                if part2_count < 5:
                    robot.movement.any_ward(angle=0, speed=150, turn=0, times=200)
                else:
                    robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 120, times=200)
                    part2_count -= 0.5
            elif start_toward == 3:
                # if part2_count < 1:
                #     robot.movement.any_ward(angle=0, speed=0, turn=-300, times=200)
                # else:
                robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 120, times=200)
            elif start_toward == 4:
                if part2_count < 4:
                    robot.movement.any_ward(angle=0, speed=150, turn=0, times=200)
                else:
                    robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 120, times=200)
            elif start_toward == 5:
                if part2_count < 1 and mynparr.right_white_pixel > 3400 and not flag_specify_start_toward:
                    print("change start_toward to 6")
                    start_toward = 6
                    robot.movement.any_ward(angle=0, speed=150, turn=40, times=200)
                    return 2
                robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 140, times=200)
                part2_count -= 0.2
            elif start_toward == 6:
                if part2_count < 8:
                    robot.movement.any_ward(angle=0, speed=150, turn=40, times=200)
                else:
                    robot.movement.any_ward(angle=0, speed=150, turn=-pid_output - 120, times=200)
                    part2_count -= 0.5
            else:
                robot.movement.any_ward(angle=0, speed=150, turn=-130, times=200)
        else:
            robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        part2_count += 1
        if now_time - start_time > 3.9 + time_offset:
            mynparr.crop_top = 60
            mynparr.crop_bottom = 105
            mynparr.threshold = threshold_p3
            mynparr.morphology = True
            print("part2 finished")
            return 3
        return 2

    def part3():
        """part3: entering obstacle zone"""
        pid_output = start_pid.Calc(mynparr.diff, 0)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 4.4 + time_offset:
            mynparr.crop_top = 50
            mynparr.crop_bottom = 95
            robot.movement.hit()
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
            mynparr.threshold = threshold_p5
            robot.movement.prepare()
            print("part4 finished")
            return 5
        return 4

    def part5():
        """part5: before end line"""
        nonlocal process_frame
        pid_output = end_pid.Calc(mynparr.left_white_pixel, target_white_pixel)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 7.4 + time_offset:
            mynparr.crop_top = 75
            mynparr.crop_bottom = 120
            mynparr.threshold = threshold_p6
            mynparr.morphology = False
            robot.movement.draw()
            process_frame = False
            print("part5 finished")
            return 6
        return 5

    def part6(_frame):
        nonlocal draw_count
        """part6: end line"""
        robot.movement.move_forward(speed=150, times=200)
        _frame = _frame[mynparr.crop_top:mynparr.crop_bottom, :]
        _frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(_frame, mynparr.threshold, 1, cv2.THRESH_BINARY)
        for i in range(15, 0, -1):
            summ = np.sum(binary[(i - 1) * 3: i * 3, :])
            if summ < 310:
                print("line detect in:", i, summ, frame_count)
                if i > 5:
                    end_delay = end_delays[i]
                    if end_delay < 0:
                        end_delay = 0
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
        0: -0.05,
        1: 0.25,
        2: 0.05,
        3: -0.05,
        4: -0.10,
        5: 0.05,
        6: 0.05
    }

    # end delays for different i
    end_delays = {
        6: 216 + end_delay_offset,
        7: 195 + end_delay_offset,
        8: 184 + end_delay_offset,
        9: 178 + end_delay_offset,
        10: 168 + end_delay_offset,
        11: 140 + end_delay_offset,
        12: 133 + end_delay_offset,
        13: 128 + end_delay_offset,
        14: 120 + end_delay_offset,
        15: 114 + end_delay_offset
    }

    # the action before start
    robot.movement.reset()

    # the crop area of part 1
    mynparr.crop_top = 75
    mynparr.crop_bottom = 120
    mynparr.threshold = threshold_p1
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
        # if process_frame:
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
    now_time = time.time()
    print("total time: ", now_time - start_time)
    print("fps: ", frame_count / (now_time - start_time))
    print("start toward: ", start_toward)
    print("part1 time: ", part1_time)
    print("first diff: ", first_diff)
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
