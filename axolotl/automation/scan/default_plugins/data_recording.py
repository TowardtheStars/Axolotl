
import os
from datetime import datetime
from enum import Enum
from typing import Union
import logging
from copy import deepcopy

import numpy as np
from matplotlib import pyplot as plt
import matplotlib

from axolotl.automation.scan.events import *
from axolotl.automation.scan.exceptions import *
from axolotl.instrument import *
from axolotl.util import *

from ..data import ScanData, ScanPlan


logger = logging.getLogger(__name__)
__template = {
    'time_format': ConfigEntry(str, '%Y-%m-%d %H.%M.%S'),
    'record_format': ConfigEntry(str, '%.9e'),
    'savetxt':{
        'encoding': ConfigEntry(str, 'utf8', '保存数据所用的字符集'),
        'fmt': ConfigEntry(str, '%.9e', 'C 语言风格的数据保存格式'),
        'delimiter': ConfigEntry(str, ' ', '数据间的分隔符'),
        'header': ConfigEntry(str, '', '文件头，不影响 loadtxt 函数的读取'),
        'footer': ConfigEntry(str, '', '文件尾，不影响 loadtxt 函数的读取'),
        'newline': ConfigEntry(str, '\n', '文件每一行末尾的字符')
    }
}


scan_config:Config = Config('scan', __template)
scan_config.load()

class MatplotlibBackendEnv:
    def __init__(self, env) -> None:
        
        self._env = env
        self._original = None

    def __enter__(self):
        self._original = matplotlib.get_backend()
        plt.switch_backend(self._env)

    def __exit__(self, type, value, trace):
        plt.switch_backend(self._original)


def __save_path_root(plan:ScanPlan, timestamp:datetime) -> str:
    """Return save path root for current plan

    Args:
        plan (ScanPlanInfo): Scan plan

    Returns:
        str: save path root
    """
    return os.path.join(plan.save_path, plan.name, timestamp.strftime(scan_config['time_format']), 'Data')

def current_save_path(event:RequireDataEvent) -> str:
    """Return current save path according to plan and current x stack
    """
    plan = event.scan_plan
    timestamp = event.timestamp
    path_stack = [__save_path_root(plan, timestamp)]
    current_x_stack = event.current_axis_stack
    axes = deepcopy(plan.axes)
    axes.reverse()
    for i in range(len(current_x_stack)):
        path_stack.append(' '.join([axes[i].name, str(scan_config['record_format']) % current_x_stack[i] ]))
    return os.path.join(*path_stack)

def env_channel_str(env_channel_list, instrument_manager) -> str:
    env_channels = [instrument_manager.get_channel_strong(idx) for idx in env_channel_list]
    env_channels = [('{0:s}={1:f}'.format(channel.name,channel.read())) for channel in env_channels]
    env_str = ', '.join(env_channels)
    return env_str

class SaveMode(Enum):
    FILE_PER_Y = 0 # default, each file after x axis finish
    FILE_PER_X = 1 # each file after x change

def save_mode(plan:ScanPlan, manager:InstrumentManager) -> SaveMode:
    return SaveMode.FILE_PER_X if any([manager.get_channel_strong(channel).dimension >= 2 for channel in plan.scan_channel]) else SaveMode.FILE_PER_Y
        


@SCAN_EVENT_BUS.event_listener(AxisPostIterateEvent)
def save_point_data(event:AxisPostIterateEvent):
    # FILE_PER_Y
    if event.axis_stack_id == 0 and save_mode(event.scan_plan, event.instrument_manager) == SaveMode.FILE_PER_Y:
        logger.debug('Save point data')
        plan = event.scan_plan
        path = current_save_path(event)
        if plan.axes_count() > 1:
            path = os.path.join(path + '.dat')
        else:
            path = os.path.join(path, '1.dat')
        
            
        shape = plan.axes_count() + len(plan.scan_channel)
        saved_data = np.ndarray((0, shape))
        for scan_data in event.data.data:
            if isinstance(scan_data.data, np.ndarray):
                data = scan_data.x[-1::-1] 
                data = np.concatenate((data, scan_data.data))
                data = np.atleast_2d(data)
                saved_data = np.concatenate((saved_data, data))
            else:
                raise ScanTargetError('Unable to convert scan data to ' + str(np.ndarray))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savetxt(fname=path, X=saved_data, **scan_config['savetxt'])
    return None


@SCAN_EVENT_BUS.event_listener(PostMeasureEvent)
def record_matrix_data(event:PostMeasureEvent):
    # FILE_PER_X
    if save_mode(event.scan_plan, event.instrument_manager) == SaveMode.FILE_PER_X:
        plan = event.scan_plan
        data = event.data
        
        path = current_save_path(event) + '.dat'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if isinstance(data.data, np.ndarray):
            rows = data.data.shape[0]
            saved_data = np.concatenate((np.array([data.x[-1::-1]] * rows), data.data), axis=1)
            np.savetxt(fname=path, X=saved_data, **scan_config['savetxt'])
        else:
            raise ScanTargetError('Unable to convert to ' + str(np.ndarray))
    return None



@SCAN_EVENT_BUS.event_listener(ScanStartEvent)
def record_parameter(event:ScanStartEvent):
    plan = event.scan_plan
    path = __save_path_root(plan, event.timestamp) 
    result = [f"{ax.name.capitalize()}:({ax.start}:{ax.step}:{ax.end})[{ax.interval}s]" for ax in plan.axes]
    result.append('')
    result.append('Channel formula:')
    result.extend([
        '{channel_name} = {formula}'.format(channel_name=k, formula=v)
        for k, v in plan.channel_formula.items()
    ])
    result.append('')
    result.append(f'Read @{datetime.now().strftime(scan_config["time_format"])}')
    
    result.append(', '.join(plan.scan_channel))
    result.append('')
    result.append('Extra Info:')
    result.append(plan.extra_info)
    result.append('')
    result.append('Recorded Channels:')
    result.extend([
        f"{event.instrument_manager.get_channel_strong(channel_id).name}={event.instrument_manager.get_channel_strong(channel_id).read()}"
            for channel_id in plan.record_env_channel
    ])
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'parameter.txt'), 'w', encoding='utf8') as file:
        
        file.writelines('\n'.join(result))
    return



@SCAN_EVENT_BUS.event_listener(AxisPostIterateEvent, PostMeasureEvent)
class DrawLine:
    def __init__(self) -> None:
        self.fig_config = {'figsize':(10, 6), 'constrained_layout':True}
        self.plot_config = {}
        self.save_config = {}
        self.__read_config()

    def __read_config(self):
        pass    #TODO

    def __call__(self, event:Union[AxisPostIterateEvent, PostMeasureEvent]):
        if event.scan_plan.plugin_config.get('draw_1d', False):
            if isinstance(event, AxisPostIterateEvent) and event.axis_stack_id == 0:
                self.__point_data_draw(event)
            elif isinstance(event, PostMeasureEvent):
                self.__line_data_draw(event)
        return None
    
    def __point_data_draw(self, event:AxisPostIterateEvent):
        # FILE_PER_Y
        path = current_save_path(event)
        path = os.path.dirname(path)
        
        xs = np.array([scan_data.x[-1] for scan_data in event.data.data])
        logger.debug('xs=%s', xs)
        yss:np.ndarray = np.atleast_2d([[scan_data.data[i] for i in range(scan_data.data_shape()[0])] for scan_data in event.data.data]) # type:ignore
        yss = yss.transpose()
        logger.debug('yss=%s', yss)

        env_str = env_channel_str(event.scan_plan.record_env_channel, event.instrument_manager)
        scan_channel_names = [event.instrument_manager.get_channel_strong(idx).name for idx in event.scan_plan.scan_channel]
        
        with MatplotlibBackendEnv('agg'):
            for i in range(yss.shape[0]):
                fig, ax = plt.subplots(**self.fig_config)
                ys = yss[i]
                logger.debug('ys[%d]=%s', i, ys)
                ax.plot(xs, ys, **self.plot_config)
                ax.set_xlabel(event.scan_plan.axes[0].name)
                ax.set_ylabel(scan_channel_names[i])
                ax.set_title(env_str)
                fig.savefig(os.path.join(path, f'{event.axis.name}[y]={event.data.x[-1] if len(event.data.x) > 0 else 1}[{i + 1:d}].png'), **self.save_config)
                plt.close(fig)

        return None
    

    def __line_data_draw(self, event:PostMeasureEvent):
        # FILE_PER_X
        path = current_save_path(event)
        path = os.path.dirname(path)
        if isinstance(event.data, np.ndarray):
            xs = event.data[:, 0]
            yss = [event.data[:, i] for i in range(1, event.data.shape[1])]  # type: ignore

            env_str = env_channel_str(event.scan_plan.record_env_channel, event.instrument_manager)
            scan_channel_names = [event.instrument_manager.get_channel_strong(idx).name for idx in event.scan_plan.scan_channel]
            with MatplotlibBackendEnv('agg'):
                for i in range(len(yss)):
                    fig, ax = plt.subplots(**self.fig_config)
                    ax.plot(xs, yss[i], **self.plot_config)
                    ax.set_xlabel(event.scan_plan.axes[0].name)
                    ax.set_ylabel(scan_channel_names[i])
                    ax.set_title(env_str)
                    fig.savefig(os.path.join(path, '{name}[x]={value}[{0:d}].png'.format(i + 1, value=event.current_axis_stack[-1], name=event.scan_plan.axes[0].name)), **self.save_config)
                    plt.close(fig)
    

@SCAN_EVENT_BUS.event_listener(AxisPostIterateEvent)
class DrawContour:
    def __init__(self) -> None:
        self.contour_config = {}
        self.fig_config = {'figsize': (10, 6), 'constrained_layout':True}
        self.save_config = {}
        self.__read_config()

    def __read_config(self):
        pass
        # TODO
    
    def __call__(self, event:AxisPostIterateEvent):
        if event.scan_plan.plugin_config.get('draw_2d', False):
            _save_mode = save_mode(event.scan_plan, event.instrument_manager)
            line_data_draw_2d = _save_mode == SaveMode.FILE_PER_X and event.axis_stack_id == 0
            point_data_draw_2d = _save_mode == SaveMode.FILE_PER_Y and event.axis_stack_id == 1
            data = None
            if line_data_draw_2d:
                data = [
                    {
                    'x': [scan_data.x for scan_data in event.data.data],
                    'y': event.data.data[0].data[0, :],
                    'z': [data.data[i, :] for data in event.data.data]
                    } for i in range(1, event.data.data[0].data.shape[0])]
            elif point_data_draw_2d:
                data = [
                    {
                    'x': [scan_data.x for scan_data in event.data.data],
                    'y': event.data.data[0].data[0, :],
                    'z': [data.data[i, :] for data in event.data.data]
                    } for i in range(1, event.data.data[0].data.shape[0])]
            if data:
                self.__draw(event, data, _save_mode)

    def __draw(self, event:AxisPostIterateEvent, data, mode):
        path = current_save_path(event)
        path = os.path.dirname(path)
        env_str = env_channel_str(event.scan_plan.record_env_channel, event.instrument_manager)
        for i, d in enumerate(data):
            with MatplotlibBackendEnv('agg'):
                fig, ax = plt.subplots(**self.fig_config)
                X, Y = np.meshgrid(d['x'], d['y'])
                Z = np.array(d['z'])
                ax.contourf(X, Y, Z, **self.contour_config)
                ax.set_xlabel(event.scan_plan.axes[0].name)
                ax.set_ylabel(event.scan_plan.axes[1].name if mode == SaveMode.FILE_PER_Y and event.axis_stack_id == 1 else 'Y')
                ax.set_title(env_str)
                fig.savefig(os.path.join(path, '{value}[{0:d}].png'.format(i + 1, name=event.scan_plan.axes[0].name)), **self.save_config)
                plt.close(fig)


