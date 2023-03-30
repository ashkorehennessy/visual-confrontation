import socket
from Sodiers_voice import Voice
class Server:
    def __init__(self):
        self.host = '' #监听所有的ip
        self.port = 13141 #接口必须一致
        self.bufsize = 1024
        self.addr = (self.host, self.port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.network = '<broadcast>'
        self.s.bind(('', self.port)) #开始监听
 
        self.voice = Voice()
        self.message = 'waiting for connection....'
        # self.sending(self.message)

    def sending(self):
        while True:
            if 'goodbye' not in self.message:
                print('Waiting for connection...')
                # data, addr = self.udpServer.recvfrom(self.bufsize)  #接收数据和返回地址
                # print(data)
                # #处理数据
                # self.message  = data.decode(encoding='utf-8')
                # print("data:", self.message)
                # data = "at %s :%s"%(ctime(),data)
                self.message = self.voice.getword()
                if '再见' in self.message:
                    self.message = 'goodbye'
                elif '前进' in self.message:
                    self.message = 'forward'
                elif '向左' in self.message:
                    self.message = 'move_left'
                elif '向右' in self.message:
                    self.message = 'move_right'
                elif '后退' in self.message:
                    self.message = 'backward'
                elif '左转' in self.message:
                    self.message = 'turn_left'
                elif '右转' in self.message:
                    self.message = 'turn_right'
                self.s.sendto(self.message.encode(encoding='utf-8'), (self.network, self.port))
                #发送数据
                print('...send message to :', self.addr)
            else:
                break
        self.s.close()

if __name__ == '__main__':
    s = Server()
    s.sending()
