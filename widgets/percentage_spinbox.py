from PyQt4 import QtGui, QtCore

class PercentageSpinBox(QtGui.QSpinBox):
    def __init__(self, parent=None):
        super(PercentageSpinBox, self).__init__(parent)

        self.setRange(0, 100)
        self.setSingleStep(1)
        self.setSuffix(' %')
        self.setAlignment(QtCore.Qt.AlignRight)
