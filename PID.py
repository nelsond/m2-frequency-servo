import numpy as np

class PID:
    def __init__(self, current_value=0., setpoint=0., prop_gain=1., int_gain=1., diff_gain=0.):
        self.reset()

        self.current_value  = current_value
        self.setpoint = setpoint

        self.prop_gain = prop_gain
        self.int_gain  = int_gain
        self.diff_gain = diff_gain

    def tick(self, current_value=False):
        old_value = self.current_value

        if (current_value):
            self.current_value = current_value

        self.error      = self.current_value - self.setpoint

        self.error_int     = np.roll(self.error_int, -1)
        self.error_int[-1] = self.error

        p = self.prop_gain * self.error
        i = self.int_gain  * np.sum(self.error_int)
        d = self.diff_gain * (current_value - old_value)

        self.output = -1 * (p + i + d)

        return self.output

    def reset(self):
        self.error         = 0.
        self.error_int     = np.zeros(1000)
        self.current_value = 0.
        self.output        = 0.

