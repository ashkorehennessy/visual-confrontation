from robotPi import robotPi
from robotpi_serOp import serOp
from Sodiers_client import Client

class Soldiers(robotPi):
    def __init__(self):
        print("Sir, yes sir!")
        super().__init__()
        
        self.ser = serOp()

    def attention(self):
        while True:
            print("Waiting commands!")
            self.client = Client()
            #print("888")
            self.order = self.client.listening()
            #print("1111")
            print(self.order)
            if 'goodbye' in self.order:
                break
            self.take_commands(self.order)
        soldier.movement.wave_hands()

    def take_commands(self, order):
        
        if 'forward' in order:
            soldier.movement.move_forward()
        elif 'move_left' in order:
            soldier.movement.move_left()
        elif 'move_right' in order:
            soldier.movement.move_right()
        elif 'backward' in order:
            soldier.movement.move_backward()
        elif 'turn_left' in order:
            soldier.movement.turn_left()
        elif 'turn_right' in order:
            soldier.movement.turn_right()
        

    


if __name__ == "__main__":
    soldier = Soldiers()
    soldier.attention()
    exit(0)
