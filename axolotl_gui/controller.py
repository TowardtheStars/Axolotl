
from os.path import dirname
from os.path import join as pathjoin
from typing import Iterable

import numpy as np
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import QObject, pyqtSignal

from axolotl.instrument import Channel, InstrumentManager
from axolotl.util import EventBus

update_channel_comboboxes = []

GUI_EVENTBUS = EventBus('GUI')


def update_channel_list(manager:InstrumentManager):
    data = manager.channel_list
    for cb in update_channel_comboboxes:
        if isinstance(cb, QComboBox):
            cb.clear()
            # cb.addItem('（空）', None)
            
            cb.setEditable(True)
            cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            
            for v in data:
                cb.addItem(v.name, v.id)

def expose(src, dst, namelist:Iterable[str]):
    for name in namelist:
        setattr(dst, name, getattr(src, name))



def formatter(readout) -> str:
    if readout is not None:
        if np.issubdtype(type(readout), np.number):
            return f'{readout:8.6g}'
        if np.issubdtype(type(readout), np.ndarray):
            if np.issubdtype(readout.dtype, np.number):
                return f'{readout:8.6g}'
            else:
                return str(readout)

    return str(readout)


class __GlobalSignals(QObject):
    refresh_signal = pyqtSignal()

GlobalSignals = __GlobalSignals()
