from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot, pyqtSignal

class SliderWithDisplayWidget(QtGui.QWidget):

    changed = pyqtSignal()

    def __init__(self, description='', decimals=2, minimum=0, maximum=1, step_size=0.1, suffix='', parent=None):
        super(SliderWithDisplayWidget, self).__init__(parent)

        self._value    = 0.0
        self.decimals = decimals
        self.suffix   = suffix

        hbox = QtGui.QHBoxLayout()
        hbox.setStretch(1, 2)
        hbox.setAlignment(QtCore.Qt.AlignVCenter)
        self.setLayout(hbox)

        label = QtGui.QLabel(description)
        label.setAlignment(QtCore.Qt.AlignRight)
        hbox.addWidget(label)

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(int(minimum*10**self.decimals), int(maximum*10**self.decimals))
        self.slider.setSingleStep(step_size*10**self.decimals)
        hbox.addWidget(self.slider)

        self.value_label = QtGui.QLabel('%.*f %s' % (self.decimals, self._value, self.suffix))
        self.value_label.setAlignment(QtCore.Qt.AlignRight)
        hbox.addWidget(self.value_label)

        self.slider.valueChanged.connect(self.update_value)

    def setValue(self, value):
        value = int(value*(10.**self.decimals))
        self.update_value(value)
        self.slider.setValue(value)

    def value(self):
        return self._value

    @pyqtSlot(int)
    def update_value(self, value):
        value = int(value)/(10.**self.decimals)

        self._value = value
        self.value_label.setText('%.*f %s' % (self.decimals, self._value, self.suffix))
        self.changed.emit()
