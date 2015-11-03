#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
import numpy as np
import pyqtgraph as pg
import random

from WLM import WLM
from M2 import M2
from PID import PID
import time

class WLMLockWorker(QtCore.QThread):
    # Channel number on wavemeter multiplexer
    CHANNEL = 7

    # IP address and port for M2 control
    M2_ADDR = ('128.138.107.135', 39933)

    # IP address of the computer running this script
    HOST_ADDR = '128.138.107.101'

    # Frequency setpoint [THz]
    FREQ_SETPOINT = 368.54265

    # Frequency to resonator tune percentage [THz/%]
    FREQ_TO_TUNE = 266.e-6

    # Default, aximum and minimum resonator tune percentage [%]
    DEFAULT, MAX, MIN = 50., 90., 10.

    # Digits for feedback on resonator tune
    PRECISION = 4

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

        self.step_duration = 1

        self.exiting = False
        self.engaged = False

        self.m2 = M2(self.M2_ADDR)

        self.wlm = WLM(channel=self.CHANNEL)

        self.pid = PID(
            setpoint=self.FREQ_SETPOINT,
            prop_gain=2.5e-1,
            int_gain=5e-2,
            diff_gain=0.0)

        self.plot_data_signal = QtCore.SIGNAL('plot_data')
        self.m2_status_signal = QtCore.SIGNAL('m2_status')
        self.wavemeter_status_signal = QtCore.SIGNAL('wavemeter_status')

    def __del__(self):
        self.wait()

    def run(self):
        if (self.m2.connect_from(self.HOST_ADDR)):
            self.emit(self.m2_status_signal, 1)
        else:
            self.emit(self.m2_status_signal, 0)

        while not self.exiting:
            start_time = time.clock()

            try:
                # Round to Wavemeter precision
                current_freq = round(self.wlm.get_frequency(), 6)
                self.emit(self.wavemeter_status_signal, 1)

                if (self.engaged):
                    feedback = self.pid.tick(current_value=current_freq)/self.FREQ_TO_TUNE + self.DEFAULT

                    if feedback > self.MAX: feedback = self.MAX
                    if feedback < self.MIN: feedback = self.MIN

                    feedback = round(feedback, self.PRECISION)

                    if (not self.m2.set('tune_resonator', feedback)):
                        print 'Error (M2): Couldn\'t set tune resonator value'

                    current_error = (self.pid.setpoint-current_freq)*1e9
                    self.emit(self.plot_data_signal, current_error*1e3)

            except Exception, e:
                self.emit(self.wavemeter_status_signal, 0)

                print 'Error (Wavemeter): %s' % e
                pass

            elapsed_time = (time.clock() - start_time)
            time.sleep(self.step_duration-elapsed_time)


        self.terminate()

    def on_update_step_duration(self, step_duration):
        self.step_duration = step_duration

    def on_update_pid(self, attr, val):
        setattr(self.pid, attr, val)

    def on_toggle_engage(self):
        self.engaged = (not self.engaged)

class WLMLockControl(QtGui.QWidget):
    ERROR_LABEL_STYLESHEET = 'QLabel { background-color : red; padding: 3px; color: white; }'
    OK_LABEL_STYLESHEET = 'QLabel { background-color : green; padding: 3px; color: white; }'
    DISABLED_LABEL_STYLESHEET = 'QLabel { background-color : gray; padding: 3px; color: white; }'

    def __init__(self, parent=None):
        super(WLMLockControl, self).__init__(parent)

        self.init_worker_thread()
        self.init_ui()

    def init_worker_thread(self):
        self.thread = WLMLockWorker()
        self.thread.start()

        self.thread_engage_toggle_signal = QtCore.SIGNAL('thread_engage_toggle_signal')
        self.thread_update_pid_signal = QtCore.SIGNAL('thread_update_pid_signal')
        self.thread_update_step_duration_signal = QtCore.SIGNAL('thread_update_step_duration_signal')

        self.thread.connect(self.thread, self.thread_engage_toggle_signal, self.thread.on_toggle_engage)
        self.thread.connect(self.thread, self.thread_update_pid_signal, self.thread.on_update_pid)
        self.thread.connect(self.thread, self.thread_update_step_duration_signal, self.thread.on_update_step_duration)

        self.connect(self.thread, self.thread.plot_data_signal, self.on_plot_data)
        self.connect(self.thread, self.thread.m2_status_signal, self.on_m2_status)
        self.connect(self.thread, self.thread.wavemeter_status_signal, self.on_wavemeter_status)

    def init_ui(self):
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.init_plot()

        pid_control_group_box = self.init_pid_control_ui()

        status_widget = self.init_status_ui()

        self.engage_button = QtGui.QPushButton('Engage', self)
        self.engage_button.setCheckable(1)
        self.engage_button.released.connect(self.on_engage_toggle)

        grid.addWidget(pid_control_group_box, 1, 0, 1, 3)

        grid.addWidget(self.plot_widget, 1, 0, 1, 3)
        grid.setRowMinimumHeight(2, 15)
        grid.addWidget(pid_control_group_box, 3, 0, 1, 3)
        grid.addWidget(status_widget, 4, 0, 1, 1)
        grid.addWidget(self.engage_button, 4, 2, 1, 1)

        self.setWindowTitle('WLM Lock Control')
        self.show()
        self.resize(365, 500)

    def init_plot(self):
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Error', units='Hz')
        self.plot_widget.setLabel('bottom', 'Step')

        self.plot_data = np.zeros(100)
        self.plot_curve = self.plot_widget.plot(pen='y')
        self.plot_curve.setData(x=np.arange(100))

    def init_status_ui(self):
        groupBox = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        groupBox.setLayout(grid)

        self.m2_label        = QtGui.QLabel('M2', self)
        self.wavemeter_label = QtGui.QLabel('Wavemeter', self)

        grid.addWidget(self.m2_label, 1, 1, 1, 1,
                              QtCore.Qt.AlignLeft)
        grid.addWidget(self.wavemeter_label, 1, 2, 1, 1,
                              QtCore.Qt.AlignLeft)

        self.wavemeter_label.setStyleSheet(self.DISABLED_LABEL_STYLESHEET);
        self.m2_label.setStyleSheet(self.DISABLED_LABEL_STYLESHEET);

        return groupBox


    def init_pid_control_ui(self):
        groupBox = QtGui.QGroupBox('PID Parameters')
        grid = QtGui.QGridLayout()
        groupBox.setLayout(grid)

        self.sp_spinbox = QtGui.QSpinBox()
        self.sp_spinbox.setAlignment(QtCore.Qt.AlignRight)
        self.sp_spinbox.valueChanged.connect(self.on_sp_change)
        self.sp_spinbox.setSingleStep(10)
        self.sp_spinbox.setRange(367e6,369e6)
        self.sp_spinbox.setSuffix(' MHz')

        self.ts_edit = QtGui.QLineEdit()
        self.p_edit  = QtGui.QLineEdit()
        self.i_edit  = QtGui.QLineEdit()
        self.d_edit  = QtGui.QLineEdit()

        for edit in [self.ts_edit, self.p_edit, self.i_edit, self.d_edit]:
            edit.setFixedWidth(65)
            edit.setAlignment(QtCore.Qt.AlignRight)
            edit.setDisabled(True)

        self.ts_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.ts_slider.valueChanged[int].connect(self.on_ts_change)

        self.p_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.p_slider.valueChanged[int].connect(self.on_p_gain_change)

        self.i_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.i_slider.valueChanged[int].connect(self.on_i_gain_change)

        self.d_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.d_slider.valueChanged[int].connect(self.on_d_gain_change)

        for slider in [self.ts_slider, self.p_slider, self.i_slider, self.d_slider]:
            #slider.setFixedWidth(150)
            slider.setTickPosition(QtGui.QSlider.TicksAbove)

        for slider in [self.p_slider, self.i_slider, self.d_slider]:
            slider.setTickInterval(250)
            slider.setMaximum(2e3)
            slider.setMinimum(0)

        self.ts_slider.setTickInterval(1000)
        self.ts_slider.setMaximum(10000)
        self.ts_slider.setMinimum(150)

        grid.addWidget(QtGui.QLabel('Time Step', self), 3, 0, 1, 1,
                              QtCore.Qt.AlignRight)

        sep = QtGui.QFrame()
        sep.setFrameShape(QtGui.QFrame.HLine)
        sep.setFrameShadow(QtGui.QFrame.Sunken)

        grid.addWidget(sep, 2, 0, 1, 3)
        grid.setRowMinimumHeight(2, 15)

        sep2 = QtGui.QFrame()
        sep2.setFrameShape(QtGui.QFrame.HLine)
        sep2.setFrameShadow(QtGui.QFrame.Sunken)

        grid.addWidget(sep2, 4, 0, 1, 3)
        grid.setRowMinimumHeight(3, 15)

        grid.addWidget(QtGui.QLabel('Setpoint', self), 1, 0, 1, 1,
                              QtCore.Qt.AlignLeft)
        grid.addWidget(QtGui.QLabel('P Gain', self), 5, 0, 1, 1,
                              QtCore.Qt.AlignLeft)
        grid.addWidget(QtGui.QLabel('I Gan', self), 6, 0, 1, 1,
                              QtCore.Qt.AlignLeft)
        grid.addWidget(QtGui.QLabel('D Gain', self), 7, 0, 1, 1,
                              QtCore.Qt.AlignLeft)

        grid.addWidget(self.ts_slider, 3, 1, 1, 1)
        grid.addWidget(self.p_slider, 5, 1, 1, 1)
        grid.addWidget(self.i_slider, 6, 1, 1, 1)
        grid.addWidget(self.d_slider, 7, 1, 1, 1)

        grid.addWidget(self.sp_spinbox, 1, 1, 1, 2)

        grid.addWidget(self.ts_edit, 3, 2, 1, 1)
        grid.addWidget(self.p_edit, 5, 2, 1, 1)
        grid.addWidget(self.i_edit, 6, 2, 1, 1)
        grid.addWidget(self.d_edit, 7, 2, 1, 1)

        return groupBox

    def on_sp_change(self):
        sp = self.sp_spinbox.value()/1.e6

        self.thread.emit(self.thread_update_pid_signal, 'setpoint', sp)

    def on_ts_change(self, value):
        ts = value/1.e3
        self.ts_edit.setText('%.0f ms' % (ts*1e3))

        self.thread.emit(self.thread_update_step_duration_signal, ts)

    def on_p_gain_change(self, value):
        p = value / 1.e3
        self.p_edit.setText('%.2f' % p)

        self.thread.emit(self.thread_update_pid_signal, 'prop_gain', p)

    def on_i_gain_change(self, value):
        i = value / 1.e3
        self.i_edit.setText('%.2f' % i)

        self.thread.emit(self.thread_update_pid_signal, 'int_gain', i)

    def on_d_gain_change(self, value):
        d = value / 1.e3
        self.d_edit.setText('%.2f' % d)

        self.thread.emit(self.thread_update_pid_signal, 'diff_gain', d)

    def on_engage_toggle(self):
        self.thread.emit(self.thread_engage_toggle_signal)

        if self.engage_button.isChecked():
            self.engage_button.setText('Stop')
        else:
            self.engage_button.setText('Engage')

    def on_plot_data(self, data):
        self.plot_data = np.roll(self.plot_data, -1)
        self.plot_data[-1] = data

        xx = np.arange(100)
        self.plot_curve.setData(y=self.plot_data, x=xx)

    def on_m2_status(self, status):
        if status == 1:
            self.m2_label.setStyleSheet(self.OK_LABEL_STYLESHEET)
        else:
            self.m2_label.setStyleSheet(self.ERROR_LABEL_STYLESHEET)

    def on_wavemeter_status(self, status):
        if status == 1:
            self.wavemeter_label.setStyleSheet(self.OK_LABEL_STYLESHEET)
        else:
            self.wavemeter_label.setStyleSheet(self.ERROR_LABEL_STYLESHEET)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    widget = WLMLockControl()
    sys.exit(app.exec_())
