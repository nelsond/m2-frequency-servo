# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from widgets import StatusIndicatorWidget

class WLStatusBar(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WLStatusBar, self).__init__(parent)

        self.setTitle('Status')

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(20, 10, 20, 10)
        self.setLayout(hbox)

        self.m2_status_indicator   = StatusIndicatorWidget(description=u'M²-ICE',   status=False)
        self.wlm_status_indicator  = StatusIndicatorWidget(description='Wavemeter', status=False)

        hbox.addStretch(2)
        hbox.addWidget(self.m2_status_indicator)
        hbox.addStretch(2)
        hbox.addWidget(self.wlm_status_indicator)
        hbox.addStretch(2)

    def set_status(self, m2_status, wlm_status):
        if (m2_status  != -1): self.m2_status_indicator.update(m2_status == 1)
        if (wlm_status != -1): self.wlm_status_indicator.update(wlm_status == 1)
