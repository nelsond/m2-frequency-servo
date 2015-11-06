from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot, pyqtSignal

class WLMainControl(QtGui.QGroupBox):

    enable_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(WLMainControl, self).__init__(parent)

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


