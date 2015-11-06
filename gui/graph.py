import time, os
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot, pyqtSignal
import pyqtgraph as pg
from collections import deque
from widgets import SaveFileSelectWidget

class WLGraphLoggingWorker(QtCore.QObject):
    logging_line_added = pyqtSignal(str)

    def __init__(self, parent=None):
        super(WLGraphLoggingWorker, self).__init__(parent)

        self.logging_file_path = ''
        self.logging_line_added.connect(self.flush_logging_line)

    @pyqtSlot(str)
    def flush_logging_line(self, line):
        file_path = self.logging_file_path

        if (os.access(os.path.dirname(file_path), os.W_OK)):
            f = None

            if (os.path.exists(file_path)):
                print 'append'
                f = open(file_path, 'a')
            else:
                print 'new file'
                f = open(file_path, 'w')
                f.write('# unix timestamp, value\n')

            f.write('%s\n' % line)
            f.close()

class WLGraph(QtGui.QWidget):
    def __init__(self, buffer_length=100, parent=None):
        super(WLGraph, self).__init__(parent)

        self.buffer_length = buffer_length
        self.rbuffer = deque(maxlen=buffer_length)

        self.init_ui()

        # turn off logging by default
        self.is_logging = False
        self.toggle_logging(0)

        self.worker_thread = QtCore.QThread(self)
        self.worker = WLGraphLoggingWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    #def __del__(self):
        #self.worker_thread.quit()
        #self.worker_thread.wait()

    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setLabel('left', units='Hz')
        self.plot_curve = self.plot_widget.plot(pen='w')
        self.plot_curve.setData(x=range(self.buffer_length))
        vbox.addWidget(self.plot_widget)

        log_group_box = QtGui.QGroupBox()
        log_group_box.setTitle('Logging')

        gbgrid = QtGui.QGridLayout()
        gbgrid.setAlignment(QtCore.Qt.AlignVCenter)
        log_group_box.setLayout(gbgrid)

        self.log_file_select_widget = SaveFileSelectWidget(description='Save to:', parent=self.parent())
        self.log_file_select_widget.changed.connect(self.update_logging_file_path)
        gbgrid.addWidget(self.log_file_select_widget, 1, 1, 1, 1)

        self.log_check_box = QtGui.QCheckBox('Enable Logging')
        self.log_check_box.stateChanged.connect(self.toggle_logging)
        gbgrid.addWidget(self.log_check_box, 1, 0, 2, 1)

        help_label = QtGui.QLabel('Values are appended to log file, format: #unix timestamp#,#value# (CSV)')
        help_label.setAlignment(QtCore.Qt.AlignCenter)
        help_label.setDisabled(True)
        help_label.setWordWrap(True)
        gbgrid.addWidget(help_label, 2, 1, 1, 1)

        gbgrid.setColumnStretch(1, 2)
        gbgrid.setHorizontalSpacing(30)

        vbox.addWidget(log_group_box)

    @pyqtSlot(str)
    def update_logging_file_path(self, file_path):
        self.worker.logging_file_path = str(file_path)
        print 'logging to: %s' % file_path

    @pyqtSlot(int)
    def toggle_logging(self, state):
        if (state == 2):
            self.is_logging = True
            self.log_file_select_widget.enable()
        else:
            self.is_logging = False
            self.log_file_select_widget.disable()

    @pyqtSlot(float)
    def push_value(self, value):
        if (self.is_logging):
            line = '%f,%f' % (time.time(), value)
            self.worker.logging_line_added.emit(line)

        self.rbuffer.append(value)
        self.plot_curve.setData(y=list(self.rbuffer))


