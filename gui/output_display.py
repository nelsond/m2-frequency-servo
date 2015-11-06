from PyQt4 import QtGui, QtCore

class WLOutputDisplay(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLOutputDisplay, self).__init__(parent)

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
