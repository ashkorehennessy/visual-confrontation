import socket

class Client():
    def __init__(self):
        self.message = '>>>'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.PORT = 13141

        self.s.bind(('', self.PORT))
        print('Listening for broadcast at ', self.s.getsockname())

        

    def listening(self):
        #print(self.s.recvfrom(65535))
        self.message, address = self.s.recvfrom(65535)
        self.s.close()
        #if 'goodbye' not in self.message:
            

        return self.message.decode('utf-8')


if __name__ == '__main__':
    client = Client()
    client.listening()