import serial


class UPComBotControll():
    ser = serial.Serial(port = "/dev/ttyUSB0",baudrate = 115200,bytesize = 8,parity = 'E',stopbits = 1,timeout = 2)
    isOpen = True
    
    def __int__(self):
        self.isOpen = True
        
    def open(self):
        self.ser.open()
        if (ser.isOpen):
            self.isOpen = True
            print("open")
        else:
            self.isOpen = False
    
    
    def setMoveAction(self,angle = 0,speed = 0,turn = 0,time = 5500):
        if (self.isOpen):
            data = [0]*8
            data[0] =  angle&0xFF
            data[1] = (angle>>8)&0xFF
            data[2] = speed&0xFF
            data[3] = (speed>>8)&0xFF
            data[4] = turn&0xFF
            data[5] = (turn>>8)&0xFF
            data[6] = time&0xFF
            data[7] = (time>>8)&0xFF
            buffer,len = self.GenerateCmd(0x08,0x02,0x08,data)
            self.ser.write(buffer)
            return True
        return False
    
    def GenerateCmd(self,device,cmd,len,data):
        buffer = [0]*(len+6)
        buffer[0] = 0xF5
        buffer[1] = 0x5F
        buffer[2] = device&0xFF
        check = buffer[2]
        buffer[3] = cmd&0xFF
        check = check+buffer[3]
        buffer[4] = len&0xFF
        check = check+buffer[4]
        for i in range(len):
            buffer[5+i] = data[i]
            check = check+buffer[5+i]
        buffer[len+5] = (~check)&0xFF
        return buffer,len+6
    
if __name__ == '__main__':
    controll = UPComBotControll()
#    controll.open()
    controll.setMoveAction(0,0,100)
        
        
        
        
        
        
        
        
        
        
        