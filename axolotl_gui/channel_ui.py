
import json
import os
from itertools import product
from os.path import join as pathjoin
from threading import Timer
from typing import Dict, Optional
import logging

from PyQt5.QtWidgets import QFrame, QGroupBox, QStackedLayout

from axolotl.instrument import *
from axolotl.util import *

from .assets.ui_channel_ctrl import Ui_ChannelCtrl
from .assets.ui_channel_layout import Ui_ChannelWidget
from .controller import *
from .mediator import CHANNEL_EVENT_MEDIATOR

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChannelWidget(Ui_ChannelWidget, QFrame):
    def __init__(self, enabled, parent, manager):
        super(QFrame, self).__init__(parent)
        super(Ui_ChannelWidget, self).__init__()
        w = 90
        h = 120
        self.setMaximumSize(w, h)
        self.setMinimumSize(w, h)
        self._manager = manager
        
        
        self.enabled = enabled
        if self.enabled:
            self.setupUi(self)
            self.stacked_layout = QStackedLayout(self.stacked_stepping)
            self.stacked_layout.setContentsMargins(0,0,0,0)
            self.stacked_stepping.setLayout(self.stacked_layout)
            self.stacked_layout.addWidget(self.stepping_spinbox)
            self.stacked_layout.addWidget(self.stepping_label)
            self.stacked_layout.setCurrentIndex(0)

            logger.debug('Widget set')

            # Connect callbacks
            self.channel_selection_combo_box.currentIndexChanged.connect(self.__change_channel)
            update_channel_comboboxes.append(self.channel_selection_combo_box)

            self.stepping_spinbox.valueChanged.connect(self.__edit_stepping)
            GlobalSignals.refresh_signal.connect(self.refresh)

            logger.debug('Refresh connected')

            @CHANNEL_EVENT_MEDIATOR.event_listener(ChannelWriteDoneEvent)
            def on_set_finished(event:ChannelWriteDoneEvent):   
                if event.channel == self.channel:
                    self.set_value_lineedit.setText('')
                    self.refresh()
                return

            
            @CHANNEL_EVENT_MEDIATOR.event_listener(ChannelWriteStepEvent)
            def on_set_step(event:ChannelWriteStepEvent):
                if self.auto_refresh_checkbox.isChecked():
                    if event.channel == self.channel:
                        self.current_channel_readout.setText(formatter(event.value))
            logger.debug('Registered callbacks')

    @property
    def channel(self) -> Optional[Channel]:
        """Current channel for this widget.

        Returns:
            Optional[Channel]: When not selected, return None. Refer to axolotl.gui.controller.update_channel_list
        """
        try:
            return self.manager.get_channel(self.channel_selection_combo_box.currentData())
        except Exception:
            return None
        
    @property
    def manager(self) -> InstrumentManager:
        return self._manager
    
    def __change_channel(self):
        if self.enabled and self.channel:

            if self.channel.readable():
                self.current_channel_readout.setText(formatter(self.channel.read()))
            else:
                self.current_channel_readout.setText('Write only')
            
            if self.channel.writable():
                self.stepping_spinbox.setEnabled(True)
                self.stepping_spinbox.setValue(self.channel.stepping)
                self.set_value_lineedit.setEnabled(True)
                self.stacked_layout.setCurrentIndex(0)
                self.set_value_lineedit.setText('')
            else:
                self.set_value_lineedit.setText('Read only')
                self.stepping_label.setText('Read only')
                self.stacked_layout.setCurrentIndex(1)
                self.set_value_lineedit.setEnabled(False)
                self.stepping_spinbox.setEnabled(False)
    
    def serialize(self) -> Dict:
        if self.channel:
            return {
                'channel_id': self.channel.id,
                'stepping': self.channel.stepping
            }
        return {
            'channel_id': '',
            'stepping': 0
        }
    
    
    def deserialize(self, d:Dict):
        channel = self.manager.get_channel(d['channel_id'])
        if channel:
            self.channel_selection_combo_box.setCurrentIndex(channel.index)
            channel.stepping = d['stepping']
            self.refresh()
        
    def refresh(self):
        if self.enabled and self.channel:
            if self.channel.readable():
                self.stepping_spinbox.setValue(self.channel.stepping)
                self.current_channel_readout.setText(formatter(self.channel.read()))
                self.stacked_layout.setCurrentIndex(0)
            else:
                self.stepping_label.setText('Write Only')
                self.stacked_layout.setCurrentIndex(1)
                self.current_channel_readout.setText('Write Only')
        return
    
    def should_auto_refresh(self):
        result = self.enabled and self.channel and self.auto_refresh_checkbox.isChecked()
        return result

    def __edit_stepping(self):
        if self.enabled and self.channel:
            try:
                step = np.abs(self.stepping_spinbox.value())
                self.channel.stepping = step
            except Exception as e:
                self.stepping_spinbox.setValue(self.channel.stepping)
                # TODO: popup msgbox to show exception
            
    def set_value(self):
        if self.channel:
            if self.channel.writable():
                v = silent_float(self.set_value_lineedit.text())
                if v is not None:
                    logger.debug('%s -> %f', self.channel.name, v)
                    self.__ft = self.channel.write(v)

            else:
                self.set_value_lineedit.setText('Read only')

    

def silent_float(f:str) -> Optional[float]:
    try:
        v = float(f)
        return v        
    except ValueError as e:
        return None




class ChannelCtrl(Ui_ChannelCtrl, QGroupBox):
    __channel_data_path = pathjoin(data_root, 'gui', 'channel.json')

    def __init__(self, manager, *args, **kwargs):
        super(QGroupBox, self).__init__(*args, **kwargs)
        super(Ui_ChannelCtrl, self).__init__()

        self.max_col = 12
        self.max_row = 4
        self._manager = manager

        self.setupUi(self)
        logger.info('Background finished')
        
        self._build_channel_widget()
        
        self.show()
        return

    def _build_channel_widget(self) -> None:
        logger.info('Build Channel Widget')
        __layout_cfg_path = pathjoin(config_root, 'layout.txt')
        # Read layout settings for GUI, if not exists, default to enable all and create file
        if os.path.exists(__layout_cfg_path):
            with open(__layout_cfg_path, 'r', encoding='utf8') as file:
                lines = file.readlines()
                ui_mat = [[c == 'O' for c in l] for l in lines]
        else:
            ui_mat = [[True] * self.max_col] * self.max_row
            with open(__layout_cfg_path, 'w', encoding='utf8') as file:
                file.writelines([''.join([('O' if v else 'X')  for v in c]) + '\n' for c in ui_mat])
        
        # Load layout settings for GUI
        self.channel_ui = [
                [
                    ChannelWidget(
                        enabled=row in range(len(ui_mat)) and col in range(len(ui_mat[0])) and ui_mat[row][col],
                        parent=self, manager=self.manager
                    ) 
                    for col in range(self.max_col)
                ] 
                for row in range(self.max_row)
            ]
        # Add widget to layout
        for row, col in product(range(self.max_row), range(self.max_col)):
            self.channel_layout.addWidget(self.channel_ui[row][col], row, col)  # type: ignore
        
        return
    
    def connect_callbacks(self):
        self._auto_refresh = True
        self.auto_refresh_checkbox.setChecked(True)
        self.refresh_button.clicked.connect(self.refresh_all)
        self.set_button.clicked.connect(self.set_all)
        self.auto_refresh_checkbox.stateChanged.connect(self.change_auto_refresh_setting)
        self.refresh_interval_spinbox.valueChanged.connect(self.change_auto_refresh_setting)

        self.timer = Timer(1, self.__auto_refresh)

        for row in self.channel_ui:
            for widget in row:
                widget.channel_selection_combo_box.currentIndexChanged.connect(self.save_channel_ui)

        return
    
    
    def refresh_all(self, all:bool=True):
        GlobalSignals.refresh_signal.emit()
        # for row, col in product(range(self.max_row), range(self.max_col)):
        #     if all or self.channel_ui[row][col].should_auto_refresh():
        #         self.channel_ui[row][col].refresh()
            
    def set_all(self):
        for row, col in product(range(self.max_row), range(self.max_col)):
            self.channel_ui[row][col].set_value()

    def change_auto_refresh_setting(self):
        self._auto_refresh = self.auto_refresh_checkbox.isChecked()
        self._auto_refresh_interval = self.refresh_interval_spinbox.value()
        if self._auto_refresh:
            if not self.timer.is_alive():
                self.auto_refresh()
        else:
            self.timer.cancel()

    @property
    def manager(self)->InstrumentManager:
        return self._manager

    def __auto_refresh(self):
        self.refresh_all()
        self.timer = Timer(function=self.auto_refresh, interval=self._auto_refresh_interval)
        self.timer.start()

    def save_channel_ui(self):
        result = []
        for row, col in product(range(self.max_row), range(self.max_col)):
            content = self.channel_ui[row][col].serialize()
            d = {
                'row': row,
                'col': col,
                'widget': content
            }
            result.append(d)
        os.makedirs(os.path.dirname(self.__channel_data_path), exist_ok=True)
        with open(self.__channel_data_path, mode='w', encoding='utf8') as file:
            json.dump(result, file, indent=2)

    def load_channel_ui(self):
        os.makedirs(os.path.dirname(self.__channel_data_path), exist_ok=True)
        # Read channel settings for GUI
        if os.path.exists(self.__channel_data_path):
            try:
                with open(self.__channel_data_path, mode='r', encoding='utf8') as file:
                    cfg = json.load(file)
                    for item in cfg:
                        try:
                            self.channel_ui[item['row']][item['col']].deserialize(item['widget'])
                        except:
                            logger.warning('Unable to load widget from data %s. Missing instrument?', item, exc_info=True)
            except:
                logger.warning('Channel record file exists but cannot be read, corrupted file?', exc_info=True)
        else: # If not exists, create default
            logger.info('Cannot find record file, create default')
            with open(self.__channel_data_path, mode='w', encoding='utf8') as file:
                json.dump([], file)


__all__ = ['ChannelWidget', 'ChannelCtrl']



