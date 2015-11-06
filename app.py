# -*- coding: utf-8 -*-
import sys, time, socket, math
from copy import deepcopy
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot, pyqtSignal

from widgets import StatusIndicatorWidget, RingBufferGraphWidget, PercentageSpinBox, SliderWithDisplayWidget
from helpers import JSONConfig
from worker import WLWorker

class WLPIDSettingsTabWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WLPIDSettingsTabWidget, self).__init__(parent)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addStretch(2)

        gain_widget = QtGui.QWidget()
        gwhbox = QtGui.QHBoxLayout()
        gain_widget.setLayout(gwhbox)

        gain_label = QtGui.QLabel('Gain Scaling:')
        gain_label.setAlignment(QtCore.Qt.AlignVCenter)
        gwhbox.addWidget(gain_label)

        self.gain_spin_box = QtGui.QDoubleSpinBox()
        self.gain_spin_box.setSuffix(' %/THz')
        self.gain_spin_box.setDecimals(0)
        self.gain_spin_box.setRange(100, 10000)
        self.gain_spin_box.setSingleStep(10)
        self.gain_spin_box.setAccelerated(True)
        self.gain_spin_box.setAlignment(QtCore.Qt.AlignRight)
        gwhbox.addWidget(self.gain_spin_box)

        vbox.addWidget(gain_widget)
        vbox.addSpacing(15)

        self.sampling_interval_slider = SliderWithDisplayWidget('T:',
                decimals=1, step_size=0.5,
                minimum=0.5, maximum=10,
                suffix='s')
        vbox.addWidget(self.sampling_interval_slider)

        sampling_interval_label = QtGui.QLabel('Sampling interval of PID loop filter')
        sampling_interval_label.setDisabled(True)
        sampling_interval_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(sampling_interval_label)

        vbox.addSpacing(20)

        self.p_gain_slider = SliderWithDisplayWidget('P:',
                decimals=3, step_size=0.01,
                minimum=0, maximum=1)
        vbox.addWidget(self.p_gain_slider)

        self.i_gain_slider = SliderWithDisplayWidget('I:',
                decimals=3, step_size=0.01,
                minimum=0, maximum=1)
        vbox.addWidget(self.i_gain_slider)

        self.d_gain_slider = SliderWithDisplayWidget('D:',
                decimals=3, step_size=0.01,
                minimum=0, maximum=1)
        vbox.addWidget(self.d_gain_slider)

        vbox.addStretch(2)

class WLM2NetworkingSettingsGroupBox(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLM2NetworkingSettingsGroupBox, self).__init__(parent)

        self.setTitle('Network')

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setColumnStretch(1, 2)

        labels = []

        host_ip_address_label = QtGui.QLabel(u'Host IP:')
        grid.addWidget(host_ip_address_label, 1, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(host_ip_address_label)

        self.host_ip_address_label = QtGui.QLabel(u'N/A')
        self.host_ip_address_label.setDisabled(True)
        grid.addWidget(self.host_ip_address_label, 1, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        ip_address_label = QtGui.QLabel(u'M²-ICE IP:')
        grid.addWidget(ip_address_label, 2, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(ip_address_label)

        self.ip_address_line_edit = QtGui.QLineEdit()
        self.ip_address_line_edit.setInputMask('000.000.000.000')
        grid.addWidget(self.ip_address_line_edit, 2, 1, 1, 1,
                QtCore.Qt.AlignVCenter)


        port_label = QtGui.QLabel('Port:')
        grid.addWidget(port_label, 3, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(port_label)

        self.port_line_edit = QtGui.QLineEdit()
        self.port_line_edit.setInputMask('00000')
        grid.addWidget(self.port_line_edit, 3, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        grid.addWidget(QtGui.QWidget(), 4, 1, 1, 2,
                QtCore.Qt.AlignVCenter)

        help_label = QtGui.QLabel('Restart application for the changes to take effect.')
        help_label.setWordWrap(True)
        help_label.setDisabled(True)
        help_label.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(help_label, 5, 0, 1, 2,
                QtCore.Qt.AlignCenter)

        for label in labels: label.setAlignment(QtCore.Qt.AlignRight)

        self.ip_address_line_edit.textChanged.connect(self.values_changed)
        self.port_line_edit.textChanged.connect(self.values_changed)

    @pyqtSlot(str)
    def values_changed(self, value):
        ip_address = str(self.ip_address_line_edit.text())
        port = self.port_line_edit.text()

        port = int(port) if (len(port) > 0) else 0

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)

        try:
            s.connect((ip_address, port))
            host_ip = s.getsockname()[0]
            s.close()

            self.host_ip_address_label.setText(host_ip)
            self.host_ip_address_label.setDisabled(False)

        except:
            self.host_ip_address_label.setText('N/A')
            self.host_ip_address_label.setDisabled(True)

            pass

class WLM2ResonatorSettingsGroupBox(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLM2ResonatorSettingsGroupBox, self).__init__(parent)

        self.setTitle('Resonator Tune')

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setColumnStretch(1, 2)

        labels = []

        center_label = QtGui.QLabel('Center:')
        grid.addWidget(center_label, 1, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(center_label)

        self.center_spin_box = PercentageSpinBox()
        grid.addWidget(self.center_spin_box, 1, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        min_label = QtGui.QLabel('Minimum:')
        grid.addWidget(min_label, 2, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(min_label)

        self.min_spin_box = PercentageSpinBox()
        grid.addWidget(self.min_spin_box, 2, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        max_label = QtGui.QLabel('Maximum:')
        grid.addWidget(max_label, 3, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(max_label)

        self.max_spin_box = PercentageSpinBox()
        grid.addWidget(self.max_spin_box, 3, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        for label in labels: label.setAlignment(QtCore.Qt.AlignRight)

        for spin_box in [self.min_spin_box, self.max_spin_box]:
            spin_box.valueChanged.connect(self.update_ranges)

        self.update_ranges()

    @pyqtSlot()
    def update_ranges(self):
        maxValue = self.max_spin_box.value()
        minValue = self.min_spin_box.value()

        self.center_spin_box.setRange(minValue, maxValue)
        self.min_spin_box.setRange(0, maxValue)
        self.max_spin_box.setRange(minValue, 100)

class WLM2SettingsTabWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WLM2SettingsTabWidget, self).__init__(parent)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setContentsMargins(10, 10, 10, 10)

        self.networking_group = WLM2NetworkingSettingsGroupBox()
        self.resonator_group = WLM2ResonatorSettingsGroupBox()

        vbox.addStretch(2)
        vbox.addWidget(self.networking_group)
        vbox.addSpacing(20)
        vbox.addWidget(self.resonator_group)
        vbox.addStretch(2)

class WLSettingsTabsWidget(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(WLSettingsTabsWidget, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)

        self.pid_tab = WLPIDSettingsTabWidget(self)
        self.m2_tab  = WLM2SettingsTabWidget(self)

        self.setMinimumSize(270, 350)

        self.addTab(self.pid_tab, 'PID Controller')
        self.addTab(self.m2_tab, u'M²-ICE')

class WLOutputGroupBox(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLOutputGroupBox, self).__init__(parent)

        self.setTitle('Output')

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        self.value_label = QtGui.QLabel('N/A')
        self.value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.value_label.setDisabled(True)
        font = self.value_label.font()
        font.setPointSize(16);
        self.value_label.setFont(font)
        hbox.addWidget(self.value_label)

class WLMainControlGroupBox(QtGui.QGroupBox):

    enable_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(WLMainControlGroupBox, self).__init__(parent)

        self.setTitle('Control')

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(1, 2)
        grid.setAlignment(QtCore.Qt.AlignVCenter)
        self.setLayout(grid)

        self.channel_combo_box = QtGui.QComboBox()
        for i in range(1, 8+1):
            self.channel_combo_box.addItem(str(i))
        grid.addWidget(self.channel_combo_box, 2, 0, 1, 1)

        channel_label = QtGui.QLabel('Channel')
        channel_label.setAlignment(QtCore.Qt.AlignCenter)
        channel_label.setWordWrap(True)
        grid.addWidget(channel_label, 3, 0, 1, 1)

        self.setpoint_spin_box = QtGui.QDoubleSpinBox()
        self.setpoint_spin_box.setSuffix(' THz')
        self.setpoint_spin_box.setDecimals(5)
        self.setpoint_spin_box.setRange(150.0, 1000.0)
        self.setpoint_spin_box.setSingleStep(1e-4)
        self.setpoint_spin_box.setAccelerated(True)
        self.setpoint_spin_box.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(self.setpoint_spin_box, 2, 1, 1, 1)

        self.read_button = QtGui.QPushButton('Read')
        grid.addWidget(self.read_button, 2, 2, 1, 1)

        setpoint_label = QtGui.QLabel('Setpoint')
        setpoint_label.setAlignment(QtCore.Qt.AlignCenter)
        setpoint_label.setWordWrap(True)
        grid.addWidget(setpoint_label, 3, 1, 1, 1)

        self.enable_button  = QtGui.QPushButton(u'Enable')
        self.enable_button.setCheckable(True)
        grid.addWidget(self.enable_button, 1, 0, 1, 3)

        self.enable_button.clicked.connect(self.propagate_signal)

    @pyqtSlot()
    def propagate_signal(self):
        self.enable_clicked.emit()

class WLStatusBarGroupBox(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLStatusBarGroupBox, self).__init__(parent)

        self.setTitle('Status')

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(20, 10, 20, 10)
        self.setLayout(hbox)

        self.m2_status_indicator   = StatusIndicatorWidget(description=u'M²-ICE',   status=False)
        self.wlm_status_indicator  = StatusIndicatorWidget(description='Wavemeter', status=False)

        hbox.addStretch(2)
        hbox.addWidget(self.m2_status_indicator)
        hbox.addStretch(2)
        hbox.addWidget(self.wlm_status_indicator)
        hbox.addStretch(2)

    def set_status(self, m2_status, wlm_status):
        if (m2_status  != -1): self.m2_status_indicator.update(m2_status == 1)
        if (wlm_status != -1): self.wlm_status_indicator.update(wlm_status == 1)

class WLSaveSettingsWidget(QtGui.QWidget):

    save_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(WLSaveSettingsWidget, self).__init__(parent)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        vbox.addStretch(8)

        help_label = QtGui.QLabel('All settings are written to config.json and automatically loaded at launch.')
        help_label.setWordWrap(True)
        help_label.setDisabled(True)
        help_label.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(help_label)

        self.save_button = QtGui.QPushButton('Save')
        self.save_button.clicked.connect(self.propagate_signal)
        vbox.addWidget(self.save_button)

    @pyqtSlot()
    def propagate_signal(self):
        self.save_clicked.emit()

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

        self.status_bar     = WLStatusBarGroupBox(self)
        self.output_display = WLOutputGroupBox(self)
        self.main_control   = WLMainControlGroupBox(self)
        self.settings_tabs  = WLSettingsTabsWidget(self)
        self.graph          = RingBufferGraphWidget(parent=self)
        self.save_settings  = WLSaveSettingsWidget(self)

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
