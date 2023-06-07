class PID:
    def __init__(self,Kp=1,Kd=0,outmax=100,outmin=-100):
        self.Kp = Kp
        self.Kd = Kd
        self.last_error = 0
        self.outmax = outmax
        self.outmin = outmin

    def update(self, input_value, setpoint):
        error = setpoint - input_value
        derivative = error - self.last_error
        self.last_error = error
        output = max(min(self.Kp * error + self.Kd * derivative, self.outmax), self.outmin)
        return int(output)
