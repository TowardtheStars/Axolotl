
from os.path import dirname
from os.path import join as pathjoin
from typing import Iterable

import numpy as np
from PyQt5.QtWidgets import QComboBox
from PyQt5.uic import loadUi

from axolotl.instrument import Channel, InstrumentManager
from axolotl.util import EventBus

update_channel_comboboxes = []

GUI_EVENTBUS = EventBus('GUI')

def load_ui(name, *args, **kwargs):
    path = pathjoin(dirname(__file__), 'assets', name + '.ui')
    return loadUi(path, *args, **kwargs)


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
    if isinstance(readout, str):
        return readout
    if np.issubdtype(type(readout), np.number):
        return '{0:11.6g}'.format(readout)
    return str(readout)
    
