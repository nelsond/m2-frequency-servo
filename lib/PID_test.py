from pid import PID

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

pid = PID(sampling_interval=0.01, prop_gain=0.88, int_gain=0.02, diff_gain=0.0)
def time_response(setpoints):
    pid.reset()

    m = len(setpoints)

    current_value = 0.
    values        = np.zeros(m)

    for i in xrange(m):
        values[i] = current_value

        pid.setpoint = setpoints[i]
        current_value += pid.tick(current_value)

    return values

# --

n = 2000
setpoints = np.ones(n)
setpoints[0:(n/2-1)] = 0.

fig = plt.figure(figsize=(15, 6))
ax  = fig.add_subplot(111)
plt.subplots_adjust(bottom=0.25)

plt.title('Step response')

step_response = time_response(setpoints)
tt = np.linspace(1, n, n)
ax.plot(tt, setpoints, 'k')
response_line, = ax.plot(tt, step_response, 'k', linewidth=2)
ax.set_xlabel('Time [steps]')

def update_prop_gain(val):
    pid.set_params(prop_gain=val)
    pid.reset()
    response_line.set_ydata(time_response(setpoints))

def update_int_gain(val):
    pid.set_params(int_gain=val)
    pid.reset()
    response_line.set_ydata(time_response(setpoints))

def update_diff_gain(val):
    pid.set_params(diff_gain=val)
    pid.reset()
    response_line.set_ydata(time_response(setpoints))

prop_gain_slider = Slider(
        plt.axes([0.125, 0.075, 0.2, 0.05]),
        'P', 0, 5, valinit=0.1)

int_gain_slider = Slider(
        plt.axes([0.4, 0.075, 0.2, 0.05]),
        'I', 0, 1, valinit=0.1)

diff_gain_slider = Slider(
        plt.axes([0.4 + 0.4 - 0.125, 0.075, 0.2, 0.05]),
        'D', 0, 0.01, valinit=0)

prop_gain_slider.on_changed(update_prop_gain)
int_gain_slider.on_changed(update_int_gain)
diff_gain_slider.on_changed(update_diff_gain)

plt.show()
