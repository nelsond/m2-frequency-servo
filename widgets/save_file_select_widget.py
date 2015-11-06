from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from . import FileSelectWidget

class SaveFileSelectWidget(FileSelectWidget):
    @pyqtSlot()
    def browse_file(self):
        file_path = str(QtGui.QFileDialog.getSaveFileName(self.parent(), 'Save to', self.last_folder_path))

        if (len(file_path) > 0):
            self.set_file_path(file_path)
            self.changed.emit(file_path)

