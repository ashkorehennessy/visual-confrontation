class PID:
    def __init__(self,Kp=1,Ki=0,Kd=0,outmax=100,outmin=-100,smooth_factor=0.0):
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki
        self.last_error = 0
        self.last_out = 0
        self.integral = 0
        self.outmax = outmax
        self.outmin = outmin
        self.smooth_factor = smooth_factor

    def Calc(self, input_value, setpoint):
        error = setpoint - input_value
        derivative = error - self.last_error
        self.integral += error
        self.last_error = error
        output = max(min(self.Kp * error + self.Ki * self.integral + self.Kd * derivative, self.outmax), self.outmin)
        if self.smooth_factor > 0:
            output = output * (1 - self.smooth_factor) + self.last_out * self.smooth_factor
        self.last_out = output
        return int(output)
