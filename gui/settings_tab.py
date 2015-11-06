# -*- coding: utf-8 -*-

import socket
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from widgets import SliderWithDisplayWidget

class WLPercentageSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self, parent=None):
        super(WLPercentageSpinBox, self).__init__(parent)

        self.setRange(0, 100)
        self.setSingleStep(1)
        self.setDecimals(4)
        self.setSuffix(' %')
        self.setAlignment(QtCore.Qt.AlignRight)

class WLSettingsTabs(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(WLSettingsTabs, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)

        self.pid_tab = WLPIDSettingsTab(self)
        self.m2_tab  = WLM2SettingsTab(self)

        self.setMinimumSize(270, 350)

        self.addTab(self.pid_tab, 'PID Controller')
        self.addTab(self.m2_tab, u'M²-ICE')

class WLM2SettingsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WLM2SettingsTab, self).__init__(parent)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setContentsMargins(10, 10, 10, 10)

        self.networking_group = WLM2NetworkingSettings()
        self.resonator_group = WLM2ResonatorSettings()

        vbox.addStretch(2)
        vbox.addWidget(self.networking_group)
        vbox.addSpacing(20)
        vbox.addWidget(self.resonator_group)
        vbox.addStretch(2)

class WLM2NetworkingSettings(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLM2NetworkingSettings, self).__init__(parent)

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

class WLPIDSettingsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WLPIDSettingsTab, self).__init__(parent)

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


class WLM2ResonatorSettings(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLM2ResonatorSettings, self).__init__(parent)

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

        self.center_spin_box = WLPercentageSpinBox()
        grid.addWidget(self.center_spin_box, 1, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        min_label = QtGui.QLabel('Minimum:')
        grid.addWidget(min_label, 2, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(min_label)

        self.min_spin_box = WLPercentageSpinBox()
        grid.addWidget(self.min_spin_box, 2, 1, 1, 1,
                QtCore.Qt.AlignVCenter)

        max_label = QtGui.QLabel('Maximum:')
        grid.addWidget(max_label, 3, 0, 1, 1,
                QtCore.Qt.AlignVCenter)
        labels.append(max_label)

        self.max_spin_box = WLPercentageSpinBox()
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
