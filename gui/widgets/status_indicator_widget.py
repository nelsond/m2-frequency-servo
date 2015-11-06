from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from .led_widget import LEDWidget

class StatusIndicatorWidget(QtGui.QWidget):
    def __init__(self, status=True, size=12, description='', parent=None):
        super(StatusIndicatorWidget, self).__init__(parent)

        self.description = description
        self.status = status
        self.size = size

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(3)
        hbox.setAlignment(QtCore.Qt.AlignLeft);
        self.setLayout(hbox)

        self.description_label = QtGui.QLabel(self.description)
        self.led_indicator = LEDWidget(size=self.size, status=self.status)

        hbox.addWidget(self.led_indicator)
        hbox.addWidget(self.description_label)

    @pyqtSlot(bool)
    def update(self, status=True):
        self.led_indicator.update(status)
