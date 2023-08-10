# calculate the time of modprobe
import subprocess
import time
start_time = time.time()
subprocess.check_call("sudo modprobe -r uvcvideo", shell=True)
now_time = time.time() - start_time
print("modprobe -r uvcvideo: ", now_time)
start_time = time.time()
subprocess.check_call("sudo modprobe uvcvideo", shell=True)
now_time = time.time() - start_time
print("modprobe uvcvideo: ", now_time)
