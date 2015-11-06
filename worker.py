import time
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot, pyqtSignal

from lib import PID, M2, WLM

import random

class WLWorker(QtCore.QObject):

    SLEEPING_STATE = 0
    WORKING_STATE  = 1

    ticked                = pyqtSignal(float, float)
    vendor_status_changed = pyqtSignal(int, int)

    def __init__(self, config, parent=None):
        super(WLWorker, self).__init__(parent)

        self.pid_enabled = False
        self.exiting     = False
        self.config      = config
        self.state       = self.WORKING_STATE

        self.pid = PID()

        self.load_config()

        self.m2 = None
        self.reconnect_m2()

        self.wlm_channel = 1
        self.wlm = None

    def reconnect_m2(self):
        ip   = self.config['m2']['ip_address']
        port = self.config['m2']['port']

        try:
            if (self.m2):
                self.m2.close()
                del self.m2

            self.m2 = M2((ip, port))

            ok = self.m2.start_connection()
            if (not ok): raise Exception

        except:
            self.m2 = None
            pass

    def update_m2(self, value):
        try:
            ok = self.m2.set('tune_resonator', value)

            if (not ok): raise Exception

            self.vendor_status_changed.emit(1, -1)

        except:
            self.vendor_status_changed.emit(0, -1)
            self.reconnect_m2()

    def read_wavemeter(self):
        value = None

        try:
            value = self.wlm.get_frequency_from_switcher(self.wlm_channel)
            #value = round(value, 5)
            self.vendor_status_changed.emit(-1, 1)
        except:
            self.vendor_status_changed.emit(-1, 0)
            pass

        return value

    def load_config(self):
        setpoint               = self.config['pid']['setpoint']
        overall_gain           = self.config['pid']['overall_gain']
        min_max                = (self.config['m2']['resonator_min'], self.config['m2']['resonator_max'])
        offset                 = self.config['m2']['resonator_center']
        self.sampling_interval = self.config['pid']['T']
        prop_gain              = self.config['pid']['P']
        int_gain               = self.config['pid']['I']
        diff_gain              = self.config['pid']['D']

        wlm_channel  = self.config['wlm']['channel']

        self.pid.setpoint     = setpoint
        self.pid.min_max      = min_max
        self.pid.offset       = offset
        self.pid.set_params(sampling_interval=self.sampling_interval,
                overall_gain = overall_gain*-1,
                prop_gain=prop_gain,
                int_gain=int_gain,
                diff_gain=diff_gain)

        self.wlm_channel = wlm_channel

    def exit(self):
        if (self.m2): self.m2.close_connection()
        self.exiting = True

    def toggle(self):
        self.pid_enabled = not self.pid_enabled

    @pyqtSlot()
    def run(self):
        current_value = 0
        start_time    = time.time()

        # init wavemeter
        try:
            self.wlm = WLM()
            self.vendor_status_changed.emit(-1, 1)
        except:
            self.vendor_status_changed.emit(-1, 0)
            print 'WARNING: Wavemeter software not installed or wrong platform'
            pass

        while not self.exiting:

            if (self.m2):
                self.vendor_status_changed.emit(1, -1)
            else:
                self.vendor_status_changed.emit(0, -1)
                self.reconnect_m2()
                time.sleep(1)
                pass

            if (self.state == self.WORKING_STATE):
                if (self.pid_enabled and self.m2 and self.wlm):

                    current_value = self.read_wavemeter()

                    if (current_value):
                        feedback = self.pid.tick(current_value)
                        self.update_m2(feedback)

                        # error in MHz (THz -> MHz: 1e6)
                        self.ticked.emit((current_value-self.pid.setpoint)*1e6, feedback)

                self.state = self.SLEEPING_STATE

                if (not self.pid_enabled):
                    self.pid.reset()

            else:
                duration = time.time() - start_time
                if (duration >= self.sampling_interval):
                    start_time = time.time()
                    self.state = self.WORKING_STATE
                else:
                    time.sleep(0.01)
