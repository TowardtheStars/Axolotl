
from datetime import datetime, time
import json
import os, shutil
from itertools import product
from typing import Optional
import logging
import functools
from copy import deepcopy

from PyQt5.QtWidgets import QDoubleSpinBox, QGroupBox, QListWidgetItem, QMessageBox, QListWidget, QWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from axolotl.util.misc import *
from axolotl.instrument import *
from axolotl.automation.scan import *
from axolotl.automation.scan.events import *
from axolotl.automation.task import Task

from .assets.ui_scan_ctrl import Ui_ScanControl
from .controller import *
from .mediator import SCAN_EVENT_MEDIATOR

# 垃圾要干湿分离
# 前后端也得分离

logger = logging.getLogger(__name__)        

scan_plan_tasks: Dict[int, ScanExecutor] = {}

def add_plan(plan:ScanExecutor):
    global scan_plan_tasks
    scan_plan_tasks[id(plan)] = plan

def del_plan(id:int):
    global scan_plan_tasks
    scan_plan_tasks[id] = None

PLAN_PATH = pathjoin(data_root, 'gui', 'scan_plans.json')

def load_plans(manager:InstrumentManager):
    if os.path.exists(PLAN_PATH):
        logger.info('Load plans')
        with open(PLAN_PATH, encoding='utf8', mode='r') as file:
            try:
                jsonlst:list = json.load(file)
            except :
                jsonlst = []
            for jsonobj in jsonlst:
                try:    # 循环内 try，不阻塞其他任务计划加载
                    plan = ScanPlan.fromJson(jsonobj)
                    add_plan(ScanExecutor(manager, plan))
                except:
                    logger.error('Cannot load plan', exc_info=True)
            
def save_plans():
    with open(PLAN_PATH, mode='w', encoding='utf8') as file:
        json.dump([task.plan for task in scan_plan_tasks.values()], 
            fp=file, ensure_ascii=False, cls=ScanPlan.encoder_cls(), indent=2, sort_keys=True
            )

class ScanCtrl(Ui_ScanControl, QGroupBox):
    

    def __init__(self, manager:InstrumentManager, *args, **kwargs):
        super(Ui_ScanControl, self).__init__()
        super(QGroupBox, self).__init__(*args, **kwargs)

        load_plans(manager)

        self.channel_mode_real_channel = True
        self._manager = manager
        self.setupUi(self)
        self.scan_plan_list.clear()
        self.scan_channel_list.clear()
        self.multi_channel_list.clear()
        self.record_channel_list.clear()
        self.save_path.clear()
        
        self.channel_mode_switch_btn.setText('真实通道')
        self.task: Optional[ScanExecutor] = None
        self.progressbar.setValue(0)
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(1)

        update_channel_comboboxes.extend([
                self.channel_combobox_x,
                self.channel_combobox_y,
                self.channel_combobox_z,
                self.scan_channel_combobox,
                self.multi_channel_combobox,
                self.record_channel_combobox
        ])

        self.refreshing_gui = False
        self.__refresh_plan_info_display()    # will not load any plan due to no plan selected, this one is for disabling widgets
        
        
    @property
    def manager(self):
        return self._manager
    
    def get_plan_controllers(self) -> tuple[QWidget]:
        return (
            self.scan_plan_name, 
            self.record_channel_add_btn, self.record_channel_add_current_btn, self.record_channel_combobox, self.record_channel_del_all_btn, self.record_channel_list, self.record_channel_del_btn,
            self.save_path, self.save_folder_dialog_btn, self.extra_info_text,
            self.should_scan_y, self.should_scan_z,
            self.channel_combobox_x, self.channel_combobox_y, self.channel_combobox_z,
            self.start_x_spinbox, self.start_y_spinbox, self.start_z_spinbox,
            self.step_x_spinbox, self.step_y_spinbox, self.step_z_spinbox,
            self.stop_x_spinbox, self.stop_y_spinbox, self.stop_z_spinbox,
            self.interval_x_spinbox, self.interval_y_spinbox, self.interval_z_spinbox,
            self.scan_channel_add_btn, self.scan_channel_combobox, self.scan_channel_del_btn, self.scan_channel_list,
            self.multi_channel_tab, self.settings_tab
            )
    
    @property
    def PLAN(self) -> int:
        return Qt.ItemDataRole.UserRole
    @property
    def CHANNEL_ID(self) -> int:
        return 1 + Qt.ItemDataRole.UserRole
    @property
    def CHANNEL_FORMULA(self) -> int:
        return 2 + Qt.ItemDataRole.UserRole
    

    
    def scan_data(self) -> Optional[ScanPlan]:
        """ Return current selected scan plan
        Optional, can return None if no plan is selected
        """
        item = self.scan_plan_list.currentItem()
        if item:
            try:
                plan_idx:int = item.data(self.PLAN)
                return scan_plan_tasks[plan_idx].plan
            except Exception as e:
                logger.error(e, exc_info=True)
        return None
    
    def scan_task(self) -> Optional[Task]:
        item = self.scan_plan_list.currentItem()
        if item:
            try:
                plan_idx:int = item.data(self.PLAN)
                return scan_plan_tasks[plan_idx]
            except Exception as e:
                logger.error(e, exc_info=True)
        return None
    
    def set_current_plan(self, plan:ScanPlan):
        try:
            plan_idx:int = self.scan_plan_list.currentItem().data(self.PLAN)
            scan_plan_tasks[plan_idx].plan = plan
        except Exception as e:
            logger.error(e, exc_info=True)

        return None
    
    def __refresh_plan_info_display(self):
        logger.debug('Refresh GUI')

        self.refreshing_gui = True
        # self.load_plans()
        if self.scan_data() is not None:

            logger.debug('Display ScanPlan %s', self.scan_data())
            self.tabWidget.setEnabled(True)
            # 扫描计划名称
            self.scan_plan_name.setText(self.scan_data().name)

            # region 控制的环境变量通道
            self.record_channel_list.clear()
            for channel_id in self.scan_data().record_env_channel:
                channel = self.manager.get_channel(channel_id)
                if channel:
                    item = QListWidgetItem()
                    item.setText('{0} = {1}'.format(channel.name, channel.read()))
                    item.setData(self.CHANNEL_ID, channel_id)
                    self.record_channel_list.addItem(item)
            # endregion

            # 保存路径
            self.save_path.setText(self.scan_data().save_path)

            # 额外文本信息
            self.extra_info_text.setPlainText(self.scan_data().extra_info)

            # region 扫描通道
            self.scan_channel_list.clear()
            for channel_id in self.scan_data().scan_channel:
                channel = self.manager.get_channel(channel_id)
                if channel:
                    item = QListWidgetItem()
                    item.setText(channel.name)
                    item.setData(self.CHANNEL_ID, channel_id)
                    self.scan_channel_list.addItem(item)
            # endregion
            
            # region 扫描轴信息
            
            self.channel_mode_real_channel = self.scan_data().plugin_config.get('real_channel', True)
            self.channel_mode_switch_btn.setText('真实通道' if self.channel_mode_real_channel else '虚拟通道')

            self.should_scan_z.setChecked(self.scan_data().axes_count() == 3)
            self.channel_combobox_z.setEnabled(self.should_scan_z.isChecked() and self.channel_mode_real_channel)
            self.should_scan_y.setChecked(self.scan_data().axes_count() >= 2)
            self.channel_combobox_y.setEnabled(self.should_scan_y.isChecked() and self.channel_mode_real_channel)
            self.channel_combobox_x.setEnabled(self.channel_mode_real_channel)

            self.enable_multi_channel(not self.channel_mode_real_channel)
            if self.channel_mode_real_channel:
                # 加载真实通道
                
                for chid, axis in self.scan_data().channel_formula.items():
                    combobox: QComboBox = getattr(self, 'channel_combobox_' + axis)
                    channel = self.manager.get_channel(chid)
                    if channel:
                        combobox.setCurrentIndex(channel.index) 
                    else:
                        combobox.setCurrentIndex(0)
                # 清空虚拟通道列表
                self.multi_channel_list.clear()
            else:
                # 加载虚拟通道

                self.multi_channel_list.clear()
                for chid, formula in self.scan_data().channel_formula.items():
                    channel = self.manager.get_channel(chid)
                    if channel:
                        item = QListWidgetItem(self.multi_channel_list)
                        item.setText(channel.name)
                        item.setData(self.CHANNEL_ID, chid)
                        item.setData(self.CHANNEL_FORMULA, formula)
                        self.multi_channel_list.addItem(item)
            
            # 轴基本信息
            axes = deepcopy(self.scan_data().axes)
            zyx = 'xyz'[0:len(axes)]
            for axis_idx in range(len(axes)):
                getattr(self, 'start_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].start)
                getattr(self, 'step_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].step)
                getattr(self, 'stop_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].end)
                getattr(self, 'interval_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].interval)
            # endregion
            

            # 其他设置页面
            self.recover_checkBox.setChecked(self.scan_data().plugin_config.get('reset2init', False))
            self.draw_1d_checkBox.setChecked(self.scan_data().plugin_config.get('draw_1d', False))
            self.draw_2d_checkBox.setChecked(self.scan_data().plugin_config.get('draw_2d', False))
            
            
            if self.task and self.task.get_thread().running() and self.task.plan == self.scan_data():
                for controller in self.get_plan_controllers():
                    controller.setEnabled(False)

        else:
            self.tabWidget.setEnabled(False)
        self.refreshing_gui = False
        return
    
    @annotation
    def refresh_display(self, func):
        """ Annotation for controllers to refresh info display from scan plan data
        """
        
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except:
                try:
                    result = func(self)
                except:
                    result = func()
            try:
                self.__refresh_plan_info_display()
            except Exception as e:
                if self.scan_data():
                    self.on_scan_plan_data_error()
                logger.error(e, exc_info=True)
            return result

        return wrapped

    def __refresh_data(self):
        if not self.refreshing_gui: # 状态机，用于在刷新 GUI 时禁用写入扫描计划
            logger.debug('Read ScanPlan from GUI')
            if self.channel_mode_real_channel:
                channel_formula={}
                if self.channel_combobox_x.currentData():
                    channel_formula.update({
                        self.channel_combobox_x.currentData():'x',
                    })
                if self.should_scan_y.isChecked() and self.channel_combobox_y.currentData():
                    channel_formula.update({self.channel_combobox_y.currentData():'y',})
                if self.should_scan_z.isChecked() and self.channel_combobox_z.currentData():
                    channel_formula.update({self.channel_combobox_z.currentData():'z'})
            else:
                channel_formula={
                    channel.data(self.CHANNEL_ID):channel.data(self.CHANNEL_FORMULA) 
                    for channel in [
                        self.multi_channel_list.item(idx) 
                        for idx in range(self.multi_channel_list.count())
                        ]
                }
            
            
            axes = [
                AxisInfo(
                    name=self.manager.get_channel(self.channel_combobox_x.currentData()).name if self.channel_mode_real_channel else 'x',
                    start=self.start_x_spinbox.value(),
                    step=self.step_x_spinbox.value(),
                    end=self.stop_x_spinbox.value(),
                    interval=self.interval_x_spinbox.value()
                )
                ]
            if self.should_scan_y.isChecked():
                axes.append(AxisInfo(
                    name=self.manager.get_channel(self.channel_combobox_y.currentData()).name if self.channel_mode_real_channel else 'y',
                    start=self.start_y_spinbox.value(),
                    step=self.step_y_spinbox.value(),
                    end=self.stop_y_spinbox.value(),
                    interval=self.interval_y_spinbox.value()
                ))
                if self.should_scan_z.isChecked():
                    axes.append(AxisInfo(
                        name=self.manager.get_channel(self.channel_combobox_z.currentData()).name if self.channel_mode_real_channel else 'z',
                        start=self.start_z_spinbox.value(),
                        step=self.step_z_spinbox.value(),
                        end=self.stop_z_spinbox.value(),
                        interval=self.interval_z_spinbox.value()
                    ))


            plugin_config = {
                'real_channel': self.channel_mode_real_channel,
                'draw_1d': self.draw_1d_checkBox.isChecked(),
                'draw_2d': self.draw_2d_checkBox.isChecked(),
                'reset2init': self.recover_checkBox.isChecked(),
            }

            plan = ScanPlan(
                _name=self.scan_plan_name.text(),
                save_path=self.save_path.text(),
                extra_info=self.extra_info_text.toPlainText(),
                record_env_channel={
                    self.record_channel_list.item(idx).data(self.CHANNEL_ID) for idx in range(self.record_channel_list.count())
                },
                channel_formula=channel_formula,
                scan_channel={
                    self.scan_channel_list.item(idx).data(self.CHANNEL_ID) for idx in range(self.scan_channel_list.count())
                },
                axes=axes,
                plugin_config=plugin_config
            )
            
            logger.debug(plan)
            self.set_current_plan(plan)

            # save plans
            save_plans()
    
    @annotation
    def refresh_data(self, func):
        """ Annotation for controllers to refresh scan plan data
        """

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except:
                try:
                    result = func(self)
                except:
                    result = func()
            
            self.__refresh_data()
            return result
        
        return wrapped
    
    def enable_multi_channel(self, enable):
        for widget in (self.multi_channel_add_btn, self.multi_channel_combobox, self.multi_channel_del_btn, self.multi_channel_formula, self.multi_channel_list):
            widget.setEnabled(enable)

    def find_plan_item(self, task:Task) -> QListWidgetItem:
        fidx = id(task)
        idx = -1
        for i in range(self.scan_plan_list.count()):
            if fidx == self.scan_plan_list.item(i).data(self.PLAN):
                idx = i
                break
        if idx < 0 or idx >= self.scan_plan_list.count():
            logger.warn("Unmannaged task!")
            return None
        return self.scan_plan_list.item(idx)
    
    def connect_callbacks(self):

        
        # region Controller Functions
        @self.refresh_data
        def __change_plan_name():
            name = self.scan_plan_name.text()
            # self.scan_data.name = name
            self.scan_plan_list.currentItem().setText(name)
            return    
        
        @self.refresh_data
        def __switch_channel_mode():
            """ 转换通道模式回调
            """
            btn = QMessageBox.question(
                self, '确认修改通道模式？', '确认修改通道模式？你将会失去目前所有的自变量通道设置！', 
                buttons=QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), 
                defaultButton=QMessageBox.StandardButton.No
                )
            if btn == QMessageBox.StandardButton.Yes:
                self.channel_mode_real_channel = not self.channel_mode_real_channel
                self.scan_data().channel_formula.clear()

            # Set enable and text based on channel mode
            self.channel_mode_switch_btn.setText('真实通道' if self.channel_mode_real_channel else '虚拟通道')

            self.channel_combobox_x.setEnabled(self.channel_mode_real_channel)
            self.channel_combobox_y.setEnabled(self.channel_mode_real_channel and self.should_scan_y.isChecked())
            self.channel_combobox_z.setEnabled(self.channel_mode_real_channel and self.should_scan_z.isChecked())
            self.enable_multi_channel(not self.channel_mode_real_channel)

        
        def __create_plan():
            item = QListWidgetItem(parent = self.scan_plan_list)
            plan = ScanExecutor(self.manager, ScanPlan())
            item.setData(self.PLAN, id(plan))
            add_plan(plan)
            self.scan_plan_list.addItem(item)
            save_plans()
            self.load_plans()

        
        def __del_plan():
            global scan_plan_tasks
            removing = self.scan_plan_list
            for item in removing.selectedIndexes():
                scan_plan_tasks[item.data(self.PLAN)] = None
                removing.takeItem(item.row())
            scan_plan_tasks = {id(task):task for task in scan_plan_tasks.values() if task}
            save_plans()
            self.load_plans()

        @self.refresh_display
        @self.refresh_data
        def __add_record_channel():
            logger.debug('add_record_channel')
            channel_id: ChannelId = self.record_channel_combobox.currentData()
            if channel_id:  # avoid "（空）"
                channel:Channel = self.manager.get_channel(channel_id)
                if channel and channel.readable():
                    list_item = QListWidgetItem('{name} = {value}'.format(name=channel.name, value=channel.read()), self.record_channel_list)
                    # list_item.setData(self.CHANNEL, channel)
                    list_item.setData(self.CHANNEL_ID, channel_id)
                    self.record_channel_list.addItem(list_item)
                    
                else:
                    channel_name = self.record_channel_combobox.currentText()
                    logger.error('Unable to set `%s` as record channel, channel invalid or not readable', channel_name)
                    QMessageBox(title='错误', text='不能将{}设置为记录频道, 频道不可用或不可读取'.format(channel_name), buttons=QMessageBox.StandardButton.Ok, parent=self)


        @self.refresh_data
        def __remove_record_channel():
            for item in self.record_channel_list.selectedIndexes():
                self.record_channel_list.takeItem(item.row())
            

        @self.refresh_display
        @self.refresh_data
        def __add_scan_channel():
            channel_id: str = self.scan_channel_combobox.currentData()
            if channel_id:
                channel = self.manager.get_channel(channel_id)
                if channel and channel.readable():
                    list_item = QListWidgetItem()
                    list_item.setText('{name}'.format(name=channel.name))
                    list_item.setData(self.CHANNEL_ID, channel_id)
                    self.scan_channel_list.addItem(list_item)
                    
                else:
                    channel_name = self.scan_channel_combobox.currentText()
                    logger.error('Unable to set `%s` as scan channel, channel invalid or not readable', channel_name)
                    QMessageBox.warning(parent=self, title='错误', text='不能将{}设置为扫描频道, 频道不可用或不可读取'.format(channel_name), buttons=QMessageBox.StandardButton.Ok)

        @self.refresh_data
        def __remove_scan_channel():
            for item in self.scan_channel_list.selectedIndexes():
                self.scan_channel_list.takeItem(item.row())
            

        @self.refresh_data
        def __select_save_folder():
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, '选择文件夹', directory=self.save_path.text(), options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
            if len(directory) > 0:
                logger.debug('Changed save directory to %s', directory)
                self.save_path.setText(directory)
                self.scan_data().save_path = directory

        
        @self.refresh_display
        @self.refresh_data
        def __add_multi_channel():
            channel_id = self.multi_channel_combobox.currentData()
            if channel_id:
                channel = self.manager.get_channel(channel_id)
                if channel and channel.writable():
                    list_item = QListWidgetItem()
                    list_item.setText('{name}'.format(name=channel.name))
                    list_item.setData(self.CHANNEL_ID, channel_id)
                    self.multi_channel_list.addItem(list_item)
                    
                else:
                    channel_name = self.multi_channel_combobox.currentText()
                    logger.error('Unable to set `%s` as scan channel, channel invalid or not readable', channel_name)
                    QMessageBox.warning(title='错误', text='不能将{}设置为扫描频道, 频道不可用或不可读取'.format(channel_name), buttons=QMessageBox.StandardButton.Ok, parent=self)

        @self.refresh_data
        def __remove_multi_channel():
            removing = self.multi_channel_list
            for item in removing.selectedIndexes():
                removing.takeItem(item.row())
            

        @self.refresh_data
        def __select_multi_channel():
            item = self.multi_channel_list.currentItem()
            if item:
                self.multi_channel_formula.setPlainText(item.data(self.CHANNEL_FORMULA))

        @self.refresh_data
        def __save_formulae():
            item = self.multi_channel_list.currentItem()
            if item:
                item.setData(self.CHANNEL_FORMULA, self.multi_channel_formula.toPlainText())
            
        @self.refresh_display
        def __change_current_plan():
            pass

        @self.refresh_data
        def __modify_scanplan():
            pass

        @self.refresh_data
        def __axis_check_change():
            if self.should_scan_z.isChecked():
                self.should_scan_y.setChecked(True)
            self.channel_combobox_y.setEnabled(self.should_scan_y.isChecked() and self.channel_mode_real_channel)
            self.channel_combobox_z.setEnabled(self.should_scan_z.isChecked() and self.channel_mode_real_channel)
            return None

        def __start_scan():
            if self.scan_data():
                # self.task = ScanExecutor(self.manager, self.scan_data())
                
                try:
                    self.scan_task().start()
                    self.progressbar.setMaximum(self.scan_data().workload)
                except ScanError as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle('Error')
                    msg.setText('Error')
                    msg.setInformativeText(' '.join(e.args))
                    msg.exec_()
            
        def __stop_scan():
            self.scan_task().cancel()

        def __start_scan_queue():
            for i in range(self.scan_plan_list.count()):
                scan_plan_tasks[self.scan_plan_list.item(i).data(self.PLAN)].start()

        def __stop_scan_queue():
            for task in scan_plan_tasks.values():
                if task.running:
                    task.cancel()

        # endregion

        # region Eventlisteners
        @SCAN_EVENT_MEDIATOR.event_listener(PostMeasureEvent)
        def __update_progress_bar(event:PostMeasureEvent): 
            if event.scan_plan == self.scan_data(): 
                self.progressbar.setEnabled(True)
                self.progressbar.setValue(event.progress)
                if event.progress > 0:
                    deltaT = (datetime.now() - event.timestamp).total_seconds()
                    if deltaT > 1:
                        eta = int((self.scan_data().workload - event.progress) / event.progress * deltaT)
                        eta_m, eta_s = divmod(eta, 60)
                        eta_h, eta_m = divmod(eta_m, 60)
                        self.current_status.setText(
                            f'当前进度 {self.progressbar.value():d}/{self.progressbar.maximum():d}\tETA: {eta_h:d}h {eta_m:d}min {eta_s:d}sec'
                            )
                self.scan_plan_list.currentItem().setText(event.scan_plan.name + '...%d%%' % (event.progress / event.scan_plan.workload * 100))
            else:
                self.find_plan_item(event.task).setText(event.scan_plan.name + '...%d%%' % (event.progress / event.scan_plan.workload * 100))
            pass


        @SCAN_EVENT_MEDIATOR.event_listener(ScanStartEvent)
        def __start_scan_event(event:ScanStartEvent):
            if event.scan_plan == self.scan_data():
                self.start_scan.setEnabled(False)
                self.progressbar.setEnabled(True)
                self.progressbar.setValue(0)
                self.stop_scan.setEnabled(True)
                self.current_status.setText('当前进度 {v}/{m}\t'.format(v=self.progressbar.value(), m=self.progressbar.maximum()))
                self.scan_plan_list.currentItem().setText(self.scan_data().name + '...Init!')
            else:
                self.find_plan_item(event.task).setText(event.scan_plan.name + '...Init!')

        @SCAN_EVENT_MEDIATOR.event_listener(ScanEndEvent)
        def __end_scan_event(event:ScanEndEvent):
            if event.scan_plan == self.scan_data():
                self.start_scan.setEnabled(True)
                self.progressbar.setEnabled(False)
                self.stop_scan.setEnabled(False)
                if event.complete:
                    self.current_status.setText('完成！')
                else:
                    self.current_status.setText('停止')
            self.find_plan_item(event.task).setText(event.scan_plan.name)

        
        def __refresh_env_channel():
            self.record_channel_list.clear()
            if self.scan_data():
                for channel_id in self.scan_data().record_env_channel:
                    channel = self.manager.get_channel(channel_id)
                    if channel:
                        item = QListWidgetItem()
                        item.setText('{0} = {1}'.format(channel.name, channel.read()))
                        item.setData(self.CHANNEL_ID, channel_id)
                        self.record_channel_list.addItem(item)
        
        GlobalSignals.refresh_signal.connect(__refresh_env_channel)

        # endregion
        
        # region Connections
        
        self.start_scan_queue_btn.clicked.connect(__start_scan_queue)
        self.stop_scan_queue_btn.clicked.connect(__stop_scan_queue)

        self.channel_mode_switch_btn.clicked.connect(__switch_channel_mode)
        self.should_scan_y.stateChanged.connect(__axis_check_change)
        self.should_scan_z.stateChanged.connect(__axis_check_change)
        
        self.record_channel_add_btn.clicked.connect(__add_record_channel)
        self.record_channel_del_btn.clicked.connect(__remove_record_channel)
        self.record_channel_del_all_btn.clicked.connect(self.record_channel_list.clear)

        self.scan_channel_add_btn.clicked.connect(__add_scan_channel)
        self.scan_channel_del_btn.clicked.connect(__remove_scan_channel)
        self.save_folder_dialog_btn.clicked.connect(__select_save_folder)

        for xyz, func in product('xyz', ['start', 'step', 'stop', 'interval']):
            spinbox:QDoubleSpinBox = getattr(self, '{0}_{1}_spinbox'.format(func, xyz))
            spinbox.valueChanged.connect(__modify_scanplan)

        for xyz in 'xyz':
            combo:QComboBox = getattr(self, 'channel_combobox_' + xyz)
            combo.currentIndexChanged.connect(__modify_scanplan)

        self.multi_channel_add_btn.clicked.connect(__add_multi_channel)
        self.multi_channel_del_btn.clicked.connect(__remove_multi_channel)
        self.multi_channel_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.multi_channel_list.currentItemChanged.connect(__select_multi_channel)
        self.multi_channel_formula.textChanged.connect(__save_formulae)

        self.new_scan_plan_btn.clicked.connect(__create_plan)
        self.delete_scan_plan_btn.clicked.connect(__del_plan)

        self.scan_plan_name.textChanged.connect(__change_plan_name)
        self.scan_plan_list.itemClicked.connect(__change_current_plan)
        self.save_path.textChanged.connect(__modify_scanplan)
        
        self.start_scan.clicked.connect(__start_scan)
        self.stop_scan.clicked.connect(__stop_scan)

        self.recover_checkBox.clicked.connect(__modify_scanplan)
        self.draw_1d_checkBox.clicked.connect(__modify_scanplan)
        self.draw_2d_checkBox.clicked.connect(__modify_scanplan)


        # endregion
        return None

    
    def load_plans(self):
        self.scan_plan_list.clear()
        for idx, plan in scan_plan_tasks.items():
            item = QListWidgetItem(plan.get_name(), parent=self.scan_plan_list)
            item.setData(self.PLAN, idx)
            self.scan_plan_list.addItem(item)

    def on_scan_plan_data_error(self):
        should_backup = QMessageBox.question(
            self, '损坏的配置文件', '扫描计划配置文件损坏，是否备份？', 
            QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), 
            defaultButton=QMessageBox.StandardButton.Yes
            )
        if should_backup == QMessageBox.StandardButton.Yes:
            shutil.copyfile(PLAN_PATH, dst=os.path.splitext(PLAN_PATH)[0] + datetime.now().strftime('_%Y-%m-%d_%H-%M-%S.json'))
    pass

