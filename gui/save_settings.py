from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot, pyqtSignal

class WLSaveSettings(QtGui.QWidget):

    save_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(WLSaveSettings, self).__init__(parent)

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
