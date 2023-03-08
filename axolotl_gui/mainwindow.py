
import os
from itertools import product
from os.path import dirname
from os.path import join as pathjoin
import logging

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

from axolotl.automation.task import getTaskManager
from axolotl.instrument import InstrumentManager
from axolotl.util import *
from . import controller
from .channel_ui import ChannelCtrl
from .scan_ctrl import ScanCtrl

from .assets.ui_main_window import Ui_mainwindow

logger = logging.getLogger(__name__)

class MainWindow(Ui_mainwindow, QMainWindow):

    def __init__(self, manager:InstrumentManager) -> None:
        super(Ui_mainwindow, self).__init__()
        super(QMainWindow, self).__init__()
        self._manager = manager
        self._scan_manager = None
        self.setupUi(self)

        self.initUI()
        self.move(0, 0)

        
        

    @property
    def manager(self):
        return self._manager
    

    def initUI(self):
        icon = QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'LOGO.png'))
        self.setWindowIcon(icon)

        logger.info('Init ChannelCtrl')
        self.channel_control = ChannelCtrl(self.manager, parent=self)
        
        logger.info('Init ScanCtrl')
        self.scan_control = ScanCtrl(manager=self.manager, parent=self)
        layout :QVBoxLayout = self.centralWidget().layout()  # type: ignore
        
        layout.addWidget(self.channel_control, stretch=2)
        layout.addWidget(self.scan_control, stretch=1)


        controller.update_channel_list(self.manager)

        self.channel_control.connect_callbacks()
        self.channel_control.load_channel_ui()
        self.scan_control.connect_callbacks()
        self.scan_control.load_plans()
        
        self.show()

    def closeEvent(self, event) -> None:
        result = QMessageBox.question(
            self, '确认关闭', '确定要关闭窗口吗？', 
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel, 
            defaultButton=QMessageBox.StandardButton.Cancel
            )
        if result == QMessageBox.StandardButton.Yes:
            getTaskManager().cancel_all()
            self.manager.close_all()
            event.accept()
        else:
            event.ignore()
        
        

