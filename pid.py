class PID:
    def __init__(self,Kp=1,Kd=0,outmax=100,outmin=-100):
        self.Kp = 0.2
        self.Kd = 0
        self.last_error = 0
        self.outmax = 250
        self.outmin = -250

    def update(self, input_value, setpoint):
        error = setpoint - input_value
        derivative = error - self.last_error
        self.last_error = error
        output = max(min(self.Kp * error + self.Kd * derivative, self.outmax), self.outmin)
        return int(output)
