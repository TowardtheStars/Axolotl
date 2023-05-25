from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime

import numpy as np

from axolotl.instrument import *
from axolotl.util import EventBus
from ..task import Task

from .data import *

SCAN_EVENT_BUS = EventBus('ScanEventBus')

@dataclass
class ScanEvent:
    '''扫描事件基类
    不直接使用
    '''
    scan_plan: 'ScanPlan'
    timestamp: datetime
    instrument_manager: 'InstrumentManager'
    progress: int
    task: 'Task'

    
@dataclass
class AxisEvent(ScanEvent):
    '''扫描轴事件的基类
    不直接使用
    '''
    axis: 'AxisInfo'


    axis_stack_id: int
    '''触发此事件的轴'''

    
@dataclass
class AxisChangeEvent(AxisEvent):
    '''扫描轴改变前事件
    改变轴的值之前触发
    '''
    target_value: float

    
@dataclass
class AxisPostIterateEvent(AxisEvent):
    has_data: bool
    data:ScanData
    current_axis_stack: np.ndarray
    

@dataclass
class AxisPreIterateEvent(AxisEvent):
    current_axis_stack: np.ndarray    

    
@dataclass
class PreMeasureEvent(ScanEvent):
    current_axis_stack: np.ndarray

    
@dataclass
class PostMeasureEvent(ScanEvent):
    ''' 获得数据后事件
    '''
    ''' 当前轴的值 '''
    current_axis_stack: np.ndarray
    ''' 当前所有轴的值 '''

    data: ScanData
    ''' 本次改变后获得的数据 '''
    

@dataclass
class ScanStartEvent(ScanEvent):
    ''' 扫描开始的事件 '''


@dataclass
class ScanEndEvent(ScanEvent):
    ''' 扫描结束事件 '''
    complete: bool
    ''' 扫描是否正常结束 '''
    pass_data: bool
    ''' 扫描结束后是否传递了数据 '''
    data: Optional[ScanData] = None
    ''' 传递的数据 '''

    
@dataclass
class PreChangeChannelEvent(ScanEvent):
    target_axis_stack: np.ndarray

    
@dataclass
class PostChangeChannelEvent(ScanEvent):
    current_axis_stack: np.ndarray


RequireDataEvent = Union[AxisPostIterateEvent, PostMeasureEvent, ScanEndEvent]

__all__ = ('SCAN_EVENT_BUS',
    'ScanEvent', 'AxisEvent', 
    'AxisPreIterateEvent', 'AxisChangeEvent', 'AxisPostIterateEvent', 
    'PreMeasureEvent', 'PostMeasureEvent', 
    'ScanStartEvent', 'ScanEndEvent',
    'PreChangeChannelEvent', 'PostChangeChannelEvent',
    'RequireDataEvent'
    )


