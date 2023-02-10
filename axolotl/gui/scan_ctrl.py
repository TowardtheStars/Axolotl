
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

from axolotl.backend.util.misc import *
from axolotl.backend.instrument import *
from axolotl.backend.automation.scan import *
from axolotl.backend.automation.scan.events import *
from axolotl.backend.automation.task import Task

from .assets.ui_scan_ctrl import Ui_ScanControl
from .controller import *
from .channel_ui import RefreshEvent

logger = logging.getLogger(__name__)




class ScanCtrl(Ui_ScanControl, QGroupBox):
    

    def __init__(self, manager:InstrumentManager, *args, **kwargs):
        super(Ui_ScanControl, self).__init__()
        super(QGroupBox, self).__init__(*args, **kwargs)

        self.channel_mode_real_channel = True
        self._manager = manager
        self.setupUi(self)
        self.scan_plan_list.clear()
        self.scan_channel_list.clear()
        self.multi_channel_list.clear()
        self.record_channel_list.clear()
        self.save_path.clear()
        
        self.channel_mode_switch_btn.setText('真实通道')
        self.task: Optional[Task] = None
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
        self.__refresh_gui()    # will not load any plan due to no plan selected, this one is for disabling widgets
        
        
    @property
    def manager(self):
        return self._manager

    @property
    def PLAN(self) -> int:
        return Qt.ItemDataRole.UserRole
    @property
    def CHANNEL_ID(self) -> int:
        return 1 + Qt.ItemDataRole.UserRole
    @property
    def CHANNEL_FORMULA(self) -> int:
        return 2 + Qt.ItemDataRole.UserRole
    
    @property
    def PLAN_PATH(self) -> str:
        return pathjoin(data_root, 'gui', 'scan_plans.json')

    @property
    def scan_data(self) -> Optional[ScanPlan]:
        """ Return current selected scan plan
        Optional, can return None if no plan is selected
        """
        try:
            return (self.scan_plan_list.currentItem().data(self.PLAN))
        except:
            pass
        return None
    
    def __refresh_gui(self):
        logger.debug('Refresh GUI')

        self.refreshing_gui = True
        if self.scan_data is not None:

            logger.debug('Display ScanPlan %s', self.scan_data)

            self.summary_tab.setEnabled(True)

            self.scan_plan_name.setText(self.scan_data.name)
            self.record_channel_list.clear()
            for channel_id in self.scan_data.record_env_channel:
                channel = self.manager.get_channel(channel_id)
                if channel:
                    item = QListWidgetItem()
                    item.setText('{0} = {1}'.format(channel.name, channel.read()))
                    item.setData(self.CHANNEL_ID, channel_id)
                    self.record_channel_list.addItem(item)

            self.save_path.setText(self.scan_data.save_path)
            self.extra_info_text.setPlainText(self.scan_data.extra_info)

            self.scan_channel_list.clear()
            for channel_id in self.scan_data.scan_channel:
                channel = self.manager.get_channel(channel_id)
                if channel:
                    item = QListWidgetItem()
                    item.setText(channel.name)
                    item.setData(self.CHANNEL_ID, channel_id)
                    self.scan_channel_list.addItem(item)
            
            # region Channel Axes Info
            f = ([s for s in self.scan_data.channel_formula.values()])
            channel_mode = True
            if 0 < len(f) <= 3:
                channel_mode = 'x' in f
                if len(f) > 1:
                    channel_mode = channel_mode and 'y' in f
                    if len(f) > 2:
                        channel_mode = channel_mode and 'z' in f
            elif len(f) == 0:
                channel_mode = True
            else:
                channel_mode = False
            self.channel_mode_real_channel = channel_mode
            self.channel_mode_switch_btn.setText('真实通道' if self.channel_mode_real_channel else '虚拟通道')

            self.should_scan_z.setChecked(self.scan_data.axes_count() == 3)
            self.channel_combobox_z.setEnabled(self.should_scan_z.isChecked())
            self.should_scan_y.setChecked(self.scan_data.axes_count() >= 2)
            self.channel_combobox_y.setEnabled(self.should_scan_y.isChecked())
            if self.channel_mode_real_channel:
                # load into real channel mode GUI
                
                for chid, axis in self.scan_data.channel_formula.items():
                    combobox: QComboBox = getattr(self, 'channel_combobox_' + axis)
                    channel = self.manager.get_channel(chid)
                    combobox.setEnabled(True)
                    if channel:
                        combobox.setCurrentIndex(channel.index) 
                    else:
                        combobox.setCurrentIndex(0)
            else:
                # load into virtual channel mode GUI
                self.channel_combobox_x.setEnabled(False)
                self.channel_combobox_y.setEnabled(False)
                self.channel_combobox_z.setEnabled(False)

                self.multi_channel_list.clear()
                for chid, formula in self.scan_data.channel_formula.items():
                    channel = self.manager.get_channel(chid)
                    if channel:
                        item = QListWidgetItem(self.multi_channel_list)
                        item.setText(channel.name)
                        item.setData(self.CHANNEL_ID, chid)
                        item.setData(self.CHANNEL_FORMULA, formula)
                        self.multi_channel_list.addItem(item)
            
            # Mundane axes info
            axes = deepcopy(self.scan_data.axes)
            zyx = 'xyz'[0:len(axes)]
            for axis_idx in range(len(axes)):
                logger.debug('Show axis %s info', zyx[axis_idx])
                getattr(self, 'start_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].start)
                getattr(self, 'step_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].step)
                getattr(self, 'stop_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].end)
                getattr(self, 'interval_' + zyx[axis_idx] + '_spinbox').setValue(axes[axis_idx].interval)
            # endregion
            
            self.recover_checkBox.setChecked(self.scan_data.plugin_config.get('recover_init_value', False))
            self.draw_1d_checkBox.setChecked(self.scan_data.plugin_config.get('draw_1d', False))
            self.draw_2d_checkBox.setChecked(self.scan_data.plugin_config.get('draw_2d', False))
            self.tabWidget.setEnabled(True)
        else:
            self.tabWidget.setEnabled(False)
        self.refreshing_gui = False
        return
    
    @annotation
    def refresh_gui(self, func):
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
            self.__refresh_gui()
            return result

        return wrapped

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
            
            if not self.refreshing_gui:
                logger.debug('Refresh ScanPlan')
                if self.channel_mode_real_channel:
                    # logger.debug(self.channel_combobox_x.currentData())
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
                    'draw_1d': self.draw_1d_checkBox.isChecked(),
                    'draw_2d': self.draw_2d_checkBox.isChecked(),
                    'reset2init': self.recover_checkBox.isChecked(),
                }

                plan = ScanPlan(
                    _name=self.scan_plan_name.text(),
                    save_path=self.save_path.text(),
                    extra_info=self.extra_info_text.toPlainText(),
                    record_env_channel=[
                        self.record_channel_list.item(idx).data(self.CHANNEL_ID) for idx in range(self.record_channel_list.count())
                    ],
                    channel_formula=channel_formula,
                    scan_channel=[
                        self.scan_channel_list.item(idx).data(self.CHANNEL_ID) for idx in range(self.scan_channel_list.count())
                    ],
                    axes=axes,
                    plugin_config=plugin_config
                )
                logger.debug(plan)
                item = self.scan_plan_list.currentItem()
                if not item:
                    self.scan_plan_list.setCurrentItem(self.scan_plan_list.item(0))
                item = self.scan_plan_list.currentItem()
                if item:
                    item.setData(self.PLAN, plan)
                    item.setText(plan.name)

                # save plans
                with open(self.PLAN_PATH, mode='w', encoding='utf8') as file:
                    json.dump([self.scan_plan_list.item(_id).data(self.PLAN) for _id in range(self.scan_plan_list.count())], 
                            fp=file, ensure_ascii=False, cls=ScanPlan.encoder_cls(), indent=2, sort_keys=True)
            return result
        
        return wrapped

    
    def connect_callbacks(self):

        
        # region Controller Functions
        @self.refresh_data
        def __change_plan_name():
            name = self.scan_plan_name.text()
            # self.scan_data.name = name
            self.scan_plan_list.currentItem().setText(self.scan_data.name)
            
        def __switch_channel_mode():
            btn = QMessageBox.question(
                self, '确认修改通道模式？', '确认修改通道模式？你将会失去目前所有的自变量通道设置！', 
                buttons=QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), 
                defaultButton=QMessageBox.StandardButton.No
                )
            if btn == QMessageBox.StandardButton.Yes:
                self.channel_mode_real_channel = not self.channel_mode_real_channel
                self.scan_data.channel_formula.clear()

            # Set enable and text based on channel mode
            if self.channel_mode_real_channel:
                self.channel_mode_switch_btn.setText('真实通道')
                self.channel_combobox_x.setEnabled(True)
                
            else:
                self.channel_mode_switch_btn.setText('虚拟通道')
                self.channel_combobox_x.setEnabled(False)
                self.channel_combobox_y.setEnabled(False)
                self.channel_combobox_z.setEnabled(False)

        
        def __create_plan():
            item = QListWidgetItem('扫描计划', self.scan_plan_list)
            item.setData(self.PLAN, ScanPlan(_name='扫描计划'))
            self.scan_plan_list.addItem(item)
            with open(self.PLAN_PATH, mode='w', encoding='utf8') as file:
                json.dump([self.scan_plan_list.item(_id).data(self.PLAN) for _id in range(self.scan_plan_list.count())], 
                        fp=file, ensure_ascii=False, cls=ScanPlan.encoder_cls(), indent=2, sort_keys=True)

        
        def __del_plan():
            removing = self.scan_plan_list
            for item in removing.selectedIndexes():
                removing.takeItem(item.row())
            with open(self.PLAN_PATH, mode='w', encoding='utf8') as file:
                    json.dump([self.scan_plan_list.item(_id).data(self.PLAN) for _id in range(self.scan_plan_list.count())], 
                            fp=file, ensure_ascii=False, cls=ScanPlan.encoder_cls(), indent=2, sort_keys=True)

            
        @self.refresh_data
        def __add_record_channel():
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
                self.scan_data.save_path = directory

        
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
            
        @self.refresh_gui
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
        
        
        @self.refresh_data
        def __axis_check_change():
            if self.should_scan_z.isChecked():
                self.should_scan_y.setChecked(True)
            self.channel_combobox_y.setEnabled(self.should_scan_y.isChecked() and self.channel_mode_real_channel)
            self.channel_combobox_z.setEnabled(self.should_scan_z.isChecked() and self.channel_mode_real_channel)
            
            return None

        def __start_scan():
            if self.scan_data:
                self.task = ScanExecutor(self.manager, self.scan_data)
                self.progressbar.setMaximum(self.scan_data.workload)
                self.task.start()
            
        def __stop_scan():
            self.task.cancel()

        # endregion

        # region Eventlisteners
        @SCAN_EVENT_BUS.event_listener(PostMeasureEvent)
        def __update_progress_bar(event:PostMeasureEvent):  
            self.progressbar.setValue(self.progressbar.value() + 1)
            
            eta = int((self.scan_data.workload - self.progressbar.value()) / self.progressbar.value() * (datetime.now() - event.timestamp).total_seconds())
            eta_m, eta_s = divmod(eta, 60)
            eta_h, eta_m = divmod(eta_m, 60)
            self.current_status.setText(
                '当前进度 {v}/{m}\t'.format(v=self.progressbar.value(), m=self.progressbar.maximum()) 
                + 'ETA: {h}h {min}min {sec}sec'.format(h=eta_h, min=eta_m, sec=eta_s)
                )

        @SCAN_EVENT_BUS.event_listener(ScanStartEvent)
        def __start_scan_event(event):
            self.start_scan.setEnabled(False)
            self.progressbar.setEnabled(True)
            self.progressbar.setValue(0)
            self.stop_scan.setEnabled(True)
            self.current_status.setText('当前进度 {v}/{m}\t'.format(v=self.progressbar.value(), m=self.progressbar.maximum()))

        @SCAN_EVENT_BUS.event_listener(ScanEndEvent)
        def __end_scan_event(event):
            self.start_scan.setEnabled(True)
            self.progressbar.setEnabled(False)
            self.stop_scan.setEnabled(False)

        @GUI_EVENTBUS.event_listener(RefreshEvent)
        def __refresh_env_channel(event):
            self.record_channel_list.clear()
            for channel_id in self.scan_data.record_env_channel:
                channel = self.manager.get_channel(channel_id)
                if channel:
                    item = QListWidgetItem()
                    item.setText('{0} = {1}'.format(channel.name, channel.read()))
                    item.setData(self.CHANNEL_ID, channel_id)
                    self.record_channel_list.addItem(item)
        # endregion
        
        # region Connections
        

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
        if os.path.exists(self.PLAN_PATH):
            logger.info('Load plans into GUI')
            try:
                with open(self.PLAN_PATH, encoding='utf8', mode='r') as file:
                    jsonlst:list = json.load(file)
                for jsonobj in jsonlst:
                    try:
                        plan = ScanPlan.fromJson(jsonobj)
                        item = QListWidgetItem(plan.name, parent=self.scan_plan_list)
                        item.setData(self.PLAN, plan)
                        self.scan_plan_list.addItem(item)
                    except:
                        logger.error('Cannot load plan', exc_info=True)
            except:
                should_backup = QMessageBox.question(
                    self, '损坏的配置文件', '扫描计划配置文件损坏，是否备份？', 
                    QMessageBox.StandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No), 
                    defaultButton=QMessageBox.StandardButton.Yes
                    )
                if should_backup == QMessageBox.StandardButton.Yes:
                    shutil.copyfile(self.PLAN_PATH, dst=os.path.splitext(self.PLAN_PATH)[0] + datetime.now().strftime('_%Y-%m-%d_%H-%M-%S.json'))

    pass

