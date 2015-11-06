from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot

class LEDWidget(QtGui.QWidget):
    green_color        = Qt.QColor(50,213,18)
    green_border_color = Qt.QColor(43,176,16)

    red_color          = Qt.QColor(255,18,18)
    red_border_color   = Qt.QColor(168,20,20)

    def __init__(self, status=True, size=20, parent=None):
        super(LEDWidget, self).__init__(parent)

        self.status = status
        self.size = size

        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

        self.pixmap_label = QtGui.QLabel()

        vbox.addWidget(self.pixmap_label)

        self.update(self.status)

    @pyqtSlot(bool)
    def update(self, status=True):
        self.status = status

        border_color = self.green_border_color if self.status else self.red_border_color
        fill_color   = self.green_color if self.status else self.red_color

        pm = QtGui.QPixmap(QtCore.QSize(self.size + 1, self.size + 1))
        pm.fill(Qt.QColor('transparent'))

        qp = QtGui.QPainter(pm)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        qp.setPen( QtGui.QPen(border_color) )
        qp.setBrush( QtGui.QBrush(fill_color) )
        qp.drawEllipse(1, 1, self.size-2, self.size-2)
        del  qp

        self.pixmap_label.setPixmap(pm)
