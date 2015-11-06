# -*- coding: utf-8 -*-

import sys, math
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot

from helpers import JSONConfig

from worker import WLWorker

from gui import WLSettingsTabs
from gui import WLOutputDisplay
from gui import WLMainControl
from gui import WLStatusBar
from gui import WLSaveSettings
from gui import WLGraph

class WLMainWidget(QtGui.QWidget):
    def __init__(self, parent=None, config_file_path=''):
        super(WLMainWidget, self).__init__(parent)

        self.init_ui()
        self.setWindowTitle(u'M²-ICE Wavemeter Lock')

        self.config = JSONConfig('config.json')
        self.load_config()

        self.worker_thread = QtCore.QThread(self)
        self.worker = WLWorker(config=self.config)
        self.worker.moveToThread(self.worker_thread)

        self.connect_signals()

        self.worker_thread.start()

    def closeEvent(self, x):
        self.worker.exit()
        self.worker_thread.quit()
        self.worker_thread.wait()

    def init_ui(self):
        self.setMinimumHeight(730)

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(15, 15, 15, 15)
        grid.setColumnStretch(2, 2)
        grid.setColumnMinimumWidth(2, 650)
        grid.setVerticalSpacing(20)
        self.setLayout(grid)

        self.status_bar     = WLStatusBar(self)
        self.output_display = WLOutputDisplay(self)
        self.main_control   = WLMainControl(self)
        self.settings_tabs  = WLSettingsTabs(self)
        self.graph          = WLGraph(parent=self)
        self.save_settings  = WLSaveSettings(self)

        grid.addWidget(self.status_bar, 1, 0, 1, 1)
        grid.addWidget(self.output_display, 2, 0, 1, 1)
        grid.addWidget(self.main_control, 3, 0, 1, 1)
        grid.addWidget(self.settings_tabs, 4, 0, 1, 1)
        grid.addWidget(self.save_settings, 5, 0, 1, 1)

        grid.addWidget(self.graph, 1, 1, 5, 2)

    def connect_signals(self):
        self.worker_thread.started.connect(self.worker.run)
        self.worker.ticked.connect(self.process_ticked)
        self.worker.vendor_status_changed.connect(self.update_status_bar)

        self.save_settings.save_clicked.connect(self.save_config)
        self.main_control.enable_clicked.connect(self.toggle_worker)

        pid_tab      = self.settings_tabs.pid_tab
        m2_tab       = self.settings_tabs.m2_tab
        main_control = self.main_control

        pid_tab.sampling_interval_slider.changed.connect(self.update_config)
        pid_tab.p_gain_slider.changed.connect(self.update_config)
        pid_tab.i_gain_slider.changed.connect(self.update_config)
        pid_tab.d_gain_slider.changed.connect(self.update_config)
        pid_tab.gain_spin_box.valueChanged.connect(self.update_config)

        m2_tab.resonator_group.max_spin_box.valueChanged.connect(self.update_config)
        m2_tab.resonator_group.min_spin_box.valueChanged.connect(self.update_config)
        m2_tab.resonator_group.center_spin_box.valueChanged.connect(self.update_config)

        main_control.setpoint_spin_box.valueChanged.connect(self.update_config)
        main_control.read_button.clicked.connect(self.read_setpoint_from_wavemeter)

    @pyqtSlot(float, float)
    def process_ticked(self, error, feedback):
        self.graph.push_value(error)
        s = math.trunc(feedback*1e4)/1.e4
        i = (feedback - s)*1e4*1e2
        self.output_display.value_label.setText('<b>%.4f</b>%i %%' % (s,i))
        self.output_display.value_label.setDisabled(False)

    @pyqtSlot()
    def read_setpoint_from_wavemeter(self):
        value = self.worker.read_wavemeter()

        if (value):
            self.main_control.setpoint_spin_box.setValue(value)
            self.update_config()

    @pyqtSlot(int, int)
    def update_status_bar(self, m2_status, wlm_status):
        self.status_bar.set_status(m2_status, wlm_status)

        if (wlm_status == 1):
            self.main_control.read_button.setDisabled(False)

        if (wlm_status == 0):
            self.main_control.read_button.setDisabled(True)

    @pyqtSlot()
    def update_config(self):
        data = self.config.data

        pid_config = data['pid']
        m2_config  = data['m2']

        pid_tab      = self.settings_tabs.pid_tab
        m2_tab       = self.settings_tabs.m2_tab
        main_control = self.main_control

        pid_config['overall_gain'] = float(pid_tab.gain_spin_box.value())
        pid_config['T'] = float(pid_tab.sampling_interval_slider.value())
        pid_config['P'] = float(pid_tab.p_gain_slider.value())
        pid_config['I'] = float(pid_tab.i_gain_slider.value())
        pid_config['D'] = float(pid_tab.d_gain_slider.value())

        m2_config['ip_address'] = str(m2_tab.networking_group.ip_address_line_edit.text())
        m2_config['port']       = int(m2_tab.networking_group.port_line_edit.text())
        m2_config['resonator_max']    = int(m2_tab.resonator_group.max_spin_box.value())
        m2_config['resonator_min']    = int(m2_tab.resonator_group.min_spin_box.value())
        m2_config['resonator_center'] = int(m2_tab.resonator_group.center_spin_box.value())

        c = main_control.channel_combo_box
        data['wlm']['channel'] = int(c.currentIndex()) + 1
        pid_config['setpoint'] = float(main_control.setpoint_spin_box.value())

        self.worker.load_config()

    @pyqtSlot()
    def toggle_worker(self):
        self.worker.toggle()

    @pyqtSlot()
    def save_config(self):
        self.update_config()
        self.config.save()

    def load_config(self):
        data = self.config.data

        pid_config = data['pid']
        m2_config  = data['m2']

        pid_tab      = self.settings_tabs.pid_tab
        m2_tab       = self.settings_tabs.m2_tab
        main_control = self.main_control

        pid_overall_gain_value = float(pid_config['overall_gain'])
        pid_T_value = float(pid_config['T'])
        pid_P_value = float(pid_config['P'])
        pid_I_value = float(pid_config['I'])
        pid_D_value = float(pid_config['D'])

        m2_ip_address_value = m2_config['ip_address']
        m2_port_value       = str(m2_config['port'])
        m2_resonator_center_value = int(m2_config['resonator_center'])
        m2_resonator_min_value    = int(m2_config['resonator_min'])
        m2_resonator_max_value    = int(m2_config['resonator_max'])

        pid_tab.gain_spin_box.setValue(pid_overall_gain_value)
        pid_tab.sampling_interval_slider.setValue(pid_T_value)
        pid_tab.p_gain_slider.setValue(pid_P_value)
        pid_tab.i_gain_slider.setValue(pid_I_value)
        pid_tab.d_gain_slider.setValue(pid_D_value)

        m2_tab.networking_group.ip_address_line_edit.setText(m2_ip_address_value)
        m2_tab.networking_group.port_line_edit.setText(m2_port_value)
        m2_tab.resonator_group.max_spin_box.setValue(m2_resonator_max_value)
        m2_tab.resonator_group.min_spin_box.setValue(m2_resonator_min_value)
        m2_tab.resonator_group.center_spin_box.setValue(m2_resonator_center_value)

        channel_combo_box_value = int(data['wlm']['channel'])
        setpoint_spin_box_value = float(pid_config['setpoint'])

        main_control.channel_combo_box.setCurrentIndex(channel_combo_box_value-1)
        main_control.setpoint_spin_box.setValue(setpoint_spin_box_value)

if __name__ == '__main__':
    app = QtGui.QApplication([])

    widget = WLMainWidget()
    widget.show()

    sys.exit(app.exec_())
