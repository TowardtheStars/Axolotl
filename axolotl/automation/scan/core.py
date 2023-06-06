


import time
from concurrent import futures
from typing import Dict, List, Optional, Type
import logging
from datetime import datetime
from copy import deepcopy

import numpy as np

from ..task import *
from axolotl.instrument import *

from .events import *
from .data import *

logger = logging.getLogger(__name__)

__accessable_numpy_names = [
    'sin', 'cos', 'tan', 'sinc', 'sinh', 'cosh', 'tanh',
    'arcsin', 'arccos', 'arctan', 'arctan2', 'arcsinh', 'arccosh', 'arctanh',
    'abs', 'power', 'sqrt', 'log', 'log10', 'log2',
    'add', 'subtract', 'multiply', 'divide',
]
accessable_functions = {
    name: np.__dict__[name] for name in __accessable_numpy_names
}

logger.debug(accessable_functions)
    
class ScanError(RuntimeError): 
    def __init__(self, exec:'ScanExecutor', *args: object) -> None:
        self.exec = exec
        self.plan: ScanPlan = exec.plan
        super().__init__(*args)

class ScanTargetError(ScanError): ...

class ScanExecutor(Task):
    def __init__(self, instrument_manager:InstrumentManager, scan_plan:ScanPlan) -> None:
        self.__manager: InstrumentManager = instrument_manager
        self.plan: ScanPlan = scan_plan
        self._running: bool = False

        self._max_pass_data_layer: int = 2
        self.__timestamp: datetime = None
        self.__progress: int = 0

    @property
    def progress(self):
        return self.__progress

    @property
    def max_pass_data_layer(self) -> int:
        return max(0, self._max_pass_data_layer)

    @property
    def manager(self)->InstrumentManager:
        return self.__manager

    def fire_event(self, event_type:Type[ScanEvent], **kwargs):
        SCAN_EVENT_BUS.fire_event(event_type(task=self, scan_plan=self.plan, instrument_manager=self.manager, timestamp=self.__timestamp, progress=self.progress, **kwargs))

    @property
    def running(self):
        return self._running


    def on_start(self):
        self._running = True
        logger.info('Start Scan Task')
        self.__timestamp = datetime.now()
        
        
        self.__scan_channel:List[Channel] = [
                self.manager.get_channel_strong(idx)
                for idx in self.plan.scan_channel
                ]
        self.__argument_channel_formula:Dict[Channel, str] = {
            self.manager.get_channel_strong(idx): formula
            for idx, formula in self.plan.channel_formula.items()
        }
        self.__progress = 0
        self.__validate()
        self.fire_event(ScanStartEvent)
        

    def __validate(self):
        # region Validate Channels exist
        argument_channel_flag = all([
            channel is not None and channel.writable()
            for channel in self.__argument_channel_formula.keys()
        ])
        record_env_channel_flag = all([
            self.manager.get_channel(idx) is not None and self.manager.get_channel_strong(idx).readable()
            for idx in self.plan.record_env_channel
        ])
        scan_channel_flag = all([
            channel is not None and channel.writable()
            for channel in self.__scan_channel
        ])
        
        
        if not all([argument_channel_flag, record_env_channel_flag, scan_channel_flag]):
            raise ScanError(self, 'Invalid Channel in plan!')
        if not len([
            channel is not None and channel.writable()
            for channel in self.__scan_channel
        ]) > 0:
            raise ScanError(self, 'No scan channel in plan!')
        # endregion

        # region axes
        axis_channel_flag = self.plan.axes_count() > 0
        if not axis_channel_flag:
            raise ScanError(self, 'No axes in plan!')
        
        for axis in self.plan.axes:
            if axis.step == 0:
                raise ScanError(self, axis.name, '步长为 0!')
        # endregion

        save_path_flag = len(self.plan.save_path) > 0
        if not save_path_flag:
            raise ScanError(self, 'Save path not set!')
        

        
    def cancel(self) -> bool:
        self._running = False
        return super().cancel()
    
    def set_channels(self, axis_values:List[float]):
        self.fire_event(PreChangeChannelEvent,
            target_axis_stack=np.array(axis_values)
        )
        ext_axis_values = {
            'x_{0:d}'.format(self.plan.axes_count() - i): v
            for i, v in enumerate(axis_values)
        }
        ext_axis_values['x'] = axis_values[-1]
        if self.plan.axes_count() >= 2:
            ext_axis_values['y'] = axis_values[-2]
        if self.plan.axes_count() >= 3:
            ext_axis_values['z'] = axis_values[-3]

        future_tasks:List[futures.Future] = []
        for channel, formula in self.__argument_channel_formula.items():
            value = eval(formula, accessable_functions, ext_axis_values)
            future_tasks.append(channel.write(value=value, race_policy=ChannelWriteRacePolicy.CHANGE_ENDPOINT))
        
        all_done_and_not_done_futures = futures.wait(future_tasks, return_when=futures.ALL_COMPLETED) # wait till all done
        # results = [v.result() for v in futures.as_completed(future_tasks, timeout=10)]

        if len(all_done_and_not_done_futures.not_done) > 0:
            # Error: set channel failed
            # Gather data
            raise ScanError('Cannot set argument channel')
        self.fire_event(PostChangeChannelEvent,
            current_axis_stack=np.array(axis_values)
        )

    def run(self) -> None:
        current_x_stack:List[float] = []

        def complement_with_init_value(x_stack:List[float]):
            result = deepcopy(x_stack)
            result.extend([
                self.plan.axes[i].start
                for i in range(self.plan.axes_count() - len(result))
            ])
            return result

        def __iterate_scan(layer:int) -> Optional[ScanData]:
            if not self._running:
                return None
            current_axis = self.plan.axes[layer]
            self.fire_event(AxisPreIterateEvent, 
                axis_stack_id=layer, 
                axis=current_axis,
                current_axis_stack=np.array(current_x_stack)
            )
            should_pass_data = layer < self._max_pass_data_layer
            data:List[ScanData] = []
            if layer > 0:
                for v in current_axis.get_range():
                    if self._running:
                        self.fire_event(AxisChangeEvent, 
                            axis_stack_id=layer, 
                            axis=current_axis,
                            target_value=v
                        )
                        current_x_stack.append(v)
                        self.set_channels(complement_with_init_value(current_x_stack))
                        time.sleep(current_axis.interval)
                        data_entry = __iterate_scan(layer=layer - 1)
                        if data_entry and self._running: # stop scan
                            if should_pass_data:
                                data.append(data_entry)
                        else:
                            return None
                        current_x_stack.pop()
            else:
                for v in current_axis.get_range():
                    if self._running:
                        self.fire_event(AxisChangeEvent, 
                            axis_stack_id=layer, 
                            axis=current_axis,
                            target_value=v
                        )
                        current_x_stack.append(v)

                        
                        self.set_channels(current_x_stack)
                        time.sleep(current_axis.interval)   
                        self.__progress += 1
                        self.fire_event(PreMeasureEvent,
                            current_axis_stack=np.array(current_x_stack)
                        )
                        data_entry = ScanData(x=np.array(current_x_stack), data=np.array([
                            channel.read() for channel in self.__scan_channel
                        ]))
                        self.fire_event(PostMeasureEvent,
                            current_axis_stack=data_entry.x,
                            data=data_entry
                            )
                        if should_pass_data:
                            data.append(data_entry)
                        current_x_stack.pop()

            sdata = ScanData(x=np.array(current_x_stack), data=tuple(data))
            self.fire_event(AxisPostIterateEvent,
                axis_stack_id=layer, 
                axis=current_axis,
                current_axis_stack=current_x_stack,
                has_data=should_pass_data,
                data=sdata
                )
            return sdata
        
        try:
            data = __iterate_scan(self.plan.axes_count() - 1)
        except:
            logger.error('An error occurred during scan.', exc_info=True)
            self._running = False

        self.fire_event(ScanEndEvent,
            complete = self._running,
            pass_data = data is not None,
            data = data
            )
        self._running = False
        return None
        
    def get_name(self) -> str:
        return self.plan.name


    pass

