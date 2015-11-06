import os
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSlot, pyqtSignal

class FileSelectWidget(QtGui.QWidget):

    changed = pyqtSignal(str)

    def __init__(self, description='', parent=None):
        super(FileSelectWidget, self).__init__(parent)

        self.description = description
        self.selected_file_path = None
        self.last_folder_path = os.path.dirname(__file__)

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        grid = QtGui.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)

        self.description_label = QtGui.QLabel(self.description)
        self.file_path_edit = QtGui.QLineEdit()
        self.file_path_edit.setDisabled(True)
        self.browse_button = QtGui.QPushButton('Browse...')

        grid.addWidget(self.description_label, 1, 0, 1, 1)
        grid.addWidget(self.file_path_edit, 1, 2, 1, 1)
        grid.addWidget(self.browse_button, 1, 3, 1, 1)

    def connect_signals(self):
        self.browse_button.clicked.connect(self.browse_file)

    def enable(self):
        self.browse_button.setDisabled(False)
        self.description_label.setDisabled(False)

    def disable(self):
        self.browse_button.setDisabled(True)
        self.description_label.setDisabled(True)

    @pyqtSlot()
    def browse_file(self):
        file_path = str(QtGui.QFileDialog.getOpenFileName(self.parent(), 'Select File', self.last_folder_path))

        if (len(file_path) > 0):
            self.set_file_path(file_path)
            self.changed.emit(file_path)

    def set_file_path(self, file_path=''):
        self.last_folder_path = os.path.dirname(file_path)
        self.selected_file_path = file_path
        self.file_path_edit.setText(file_path)
