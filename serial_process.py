# encoding:utf-8
import threading
import time
import serial

class ComThread:
    def __init__(self, Port='/dev/ttyUSB0'):
        self.l_serial = None
        self.alive = False
        self.waitEnd = None
        self.port = Port
        self.data = None

    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()

    def SetStopEvent(self):
        if not self.waitEnd is None:
            self.waitEnd.set()
        self.alive = False
        self.stop()

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = 115200
        self.l_serial.timeout = 2
        self.l_serial.open()
        if self.l_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.FirstReader)
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True
        else:
            return False

    def SendData(self,i_msg,send):
        lmsg = ''
        isOK = False
        if isinstance(i_msg):
            lmsg = i_msg.encode()
        else:
            lmsg = i_msg
        try:
            # 发送数据到相应的处理组件
            self.l_serial.write(send)
        except Exception as ex:
            pass;
        return isOK

    def FirstReader(self):
        while self.alive:
            time.sleep(0.1)

            Data = ''
            Data = Data.encode()

            n = self.l_serial.inWaiting()
            if n:
                 Data = Data + self.l_serial.read(n)
                 # print('get data from serial port:', data)
                 # print(type(data))

            n = self.l_serial.inWaiting()
            if len(Data) > 0 and n == 0:
                break
        self.data = Data
        self.waitEnd.set()
        self.alive = False

    def stop(self):
        self.alive = False
        self.thread_read.join()
        if self.l_serial.isOpen():
            self.l_serial.close()
#调用串口，测试串口
def listen():
    rt = ComThread()
    # rt.sendport = '**1*80*'
    try:
        if rt.start():
            print(rt.l_serial.name)
            rt.waiting()
            print("The data is:%s"%(rt.data))
            rt.stop()
        else:
            pass
    except Exception as se:
        print(str(se))

    if rt.alive:
        rt.stop()

    print('')
    print ('End OK .')
    temp_data=rt.data
    del rt
    return temp_data


if __name__ == '__main__':

    data = listen()

    print("******")
    print(data)