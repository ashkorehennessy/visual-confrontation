import cv2
import multiprocessing
import time
import sys
import signal
import subprocess
from robotPi import robotPi
from pid import PID
from mynparr import Mynparr


def signal_handler(signal, frame):
    robot = robotPi()
    robot.movement.reset()
    exit(0)


def videocap(image, image_ok):
    # subprocess.check_call("v4l2-ctl -d /dev/video0 -c contrast=55 -c saturation=0 -c sharpness=5", shell=True)
    video = cv2.VideoCapture('/dev/video0')
    # set camera resolution
    video.set(3, 160)
    video.set(4, 120)
    ret, image.value = video.read()
    # if video is not opened, raise error
    if not ret:
        raise Exception("video error")
    # let camera be steady
    for _ in range(10):
        video.read()
    print("video steady")
    # start video capture
    while True:
        image_ok.value, image.value = video.read()


def autopilot(image, video_ok):
    robot = robotPi()
    mynparr = Mynparr()

    # init PID
    start_pid = PID(Kp=2, Kd=0, outmax=400, outmin=-400)
    end_pid = PID(Kp=0.15, Kd=0, outmax=200, outmin=-200)

    # flags
    part = 1
    start_toward = 0
    start_ready = 0

    # time and counter
    start_time = time.time()
    now_time = start_time
    part1_time = 0.0
    time_offset = 0.0
    frame_count = 0

    def part1():
        """part1: start line"""
        nonlocal start_ready
        mynparr.crop_top = 75
        mynparr.crop_bottom = 120
        pid_output = start_pid.Calc(mynparr.diff, 0)
        if abs(mynparr.diff) < 200:
            ang = -20
        else:
            ang = 0
        robot.movement.left_ward(angle=-ang, speed=0, turn=-pid_output, times=200)
        if first_diff > 200:
            start_ready = 1
        if -200 < mynparr.diff < 2100:
            start_ready += 1
        if -200 < first_diff < 200:
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
                if part1_time > 0.35:
                    start_toward = 1
                else:
                    start_toward = 2
            elif -150 <= first_diff <= 150:
                mynparr.process(image.value)
                if mynparr.diff < -150:
                    start_toward = 3
                else:
                    start_toward = 4
            elif first_diff > 2000:
                start_toward = 5
            else:
                start_toward = 6
            time_offset = time_offsets[start_toward]
            print("part1 finished, time: ", part1_time)
            return 2
        return 1

    def part2():
        """part2: before obstacle zone"""
        pid_output = start_pid.Calc(mynparr.diff, 0)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 3.8 + time_offset:
            mynparr.crop_top = 50
            mynparr.crop_bottom = 95
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
        if now_time - start_time > 5.7 + time_offset:
            mynparr.crop_top = 25
            mynparr.crop_bottom = 70
            mynparr.threshold = 100
            robot.movement.prepare()
            print("part4 finished")
            return 5
        return 4

    def part5():
        """part5: before end line"""
        pid_output = end_pid.Calc(mynparr.left_white_pixel, 2450)
        robot.movement.any_ward(speed=150, turn=-pid_output, times=200)
        if now_time - start_time > 7.4 + time_offset:
            mynparr.crop_top = 75
            mynparr.crop_bottom = 120
            mynparr.threshold = 135
            robot.movement.draw()
            mynparr.morphology = False
            print("part5 finished")
            return 6
        return 5

    def part6():
        """part6: end line"""
        robot.movement.any_ward(speed=30, times=200)
        if mynparr.down_white_pixel < 2400:
            robot.movement.move_forward(speed=50, times=360)
            print("part6 finished")
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
        1: 0.35,
        2: 0.15,
        3: 0.05,
        4: -0.1,
        5: 0.15,
        6: 0.20
    }

    # the action before start
    robot.movement.reset()

    # the crop area of part 1
    mynparr.crop_top = 75
    mynparr.crop_bottom = 120
    mynparr.process(image.value)
    first_diff = mynparr.diff

    while part < 7:
        # check if new frame is ready
        if video_ok.value == 1:
            frame = image.value
            video_ok.value = 0
        else:
            continue

        # process frame
        mynparr.process(frame)
        frame_count += 1

        # update now time
        now_time = time.time()

        # run part
        part_function = part_functions.get(part)
        part = part_function()

    # print info
    print("total time: ", now_time - start_time)
    print("fps: ", frame_count / (now_time - start_time))
    print("start toward: ", start_toward)
    print("part1 time: ", part1_time)
    print("first diff: ", first_diff)
    print("time offset: ", time_offset)
    mynparr.record_save = True
    mynparr.process(image.value)


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
    print("video ok")
    while True:
        if sys.stdin.read(1) == ' ':
            break
    autopilot_proc.start()
    autopilot_proc.join()
    videocap_proc.join()
