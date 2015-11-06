from PyQt4 import QtGui, QtCore

class MeasurementDisplayWidget(QtGui.QWidget):
    def __init__(self, value=0.0, unit= '', description='Unknown', decimals=1, parent=None):
        super(MeasurementDisplayWidget, self).__init__(parent)

        self.value = value
        self.unit = unit
        self.description = description

        self.init_ui()
        self.update()

    def init_ui(self):
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.value_label = QtGui.QLabel('', self)
        font = self.value_label.font()
        font.setPointSize(40);
        self.value_label.setFont(font)

        self.unit_label = QtGui.QLabel(self.unit, self)
        font = self.unit_label.font()
        font.setPointSize(20);
        self.unit_label.setFont(font)

        self.description_label = QtGui.QLabel(self.description, self)
        font = self.description_label.font()
        font.setPointSize(16);
        self.description_label.setFont(font)

        grid.addWidget(self.value_label, 1, 0, 1, 4, QtCore.Qt.AlignRight)
        grid.addWidget(self.unit_label, 1, 4, 1, 1, QtCore.Qt.AlignLeft)
        grid.addWidget(self.description_label, 2, 0, 1, 5, QtCore.Qt.AlignCenter)

        self.labels = [self.value_label, self.unit_label, self.description_label]

        grid.setContentsMargins(30, 10, 30, 10)

    def disable(self):
        for label in self.labels: label.setDisabled(True)

    def enable(self):
        for label in self.labels: label.setDisabled(False)

    def update(self, value=False):
        if (value): self.value = value
        self.value_label.setText('%.1f' % self.value )

        return True
