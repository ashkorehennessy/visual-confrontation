class PID:
    def __init__(self, Kp, Ki, Kd, outmax, outmin):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.outmax = outmax
        self.outmin = outmin
        self.last_error = 0

    def update(self, input_value, setpoint, dt):
        error = setpoint - input_value
        pout = self.Kp * error
        iout = self.Ki * error * dt
        dout = self.Kd * (error - self.last_error) / dt
        output = pout + iout + dout
        output = max(min(output, self.outmax), self.outmin)
        self.last_error = error
        return output
