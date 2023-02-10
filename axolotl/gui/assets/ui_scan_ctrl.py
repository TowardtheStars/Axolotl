# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Documents\Proj\Axolotl\axolotl\gui\assets\scan_ctrl.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ScanControl(object):
    def setupUi(self, ScanControl):
        ScanControl.setObjectName("ScanControl")
        ScanControl.resize(1146, 420)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ScanControl.sizePolicy().hasHeightForWidth())
        ScanControl.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(ScanControl)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(ScanControl)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scan_plan_list = QtWidgets.QListWidget(self.widget)
        self.scan_plan_list.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.scan_plan_list.setDragEnabled(True)
        self.scan_plan_list.setAlternatingRowColors(True)
        self.scan_plan_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.scan_plan_list.setTextElideMode(QtCore.Qt.ElideRight)
        self.scan_plan_list.setProperty("isWrapping", True)
        self.scan_plan_list.setWordWrap(True)
        self.scan_plan_list.setObjectName("scan_plan_list")
        item = QtWidgets.QListWidgetItem()
        self.scan_plan_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.scan_plan_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.scan_plan_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.scan_plan_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.scan_plan_list.addItem(item)
        self.verticalLayout.addWidget(self.scan_plan_list)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.delete_scan_plan_btn = QtWidgets.QPushButton(self.widget)
        self.delete_scan_plan_btn.setObjectName("delete_scan_plan_btn")
        self.gridLayout_2.addWidget(self.delete_scan_plan_btn, 0, 1, 1, 1)
        self.start_scan_queue_btn = QtWidgets.QPushButton(self.widget)
        self.start_scan_queue_btn.setEnabled(False)
        self.start_scan_queue_btn.setObjectName("start_scan_queue_btn")
        self.gridLayout_2.addWidget(self.start_scan_queue_btn, 1, 0, 1, 1)
        self.new_scan_plan_btn = QtWidgets.QPushButton(self.widget)
        self.new_scan_plan_btn.setObjectName("new_scan_plan_btn")
        self.gridLayout_2.addWidget(self.new_scan_plan_btn, 0, 0, 1, 1)
        self.stop_scan_queue_btn = QtWidgets.QPushButton(self.widget)
        self.stop_scan_queue_btn.setEnabled(False)
        self.stop_scan_queue_btn.setObjectName("stop_scan_queue_btn")
        self.gridLayout_2.addWidget(self.stop_scan_queue_btn, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(ScanControl)
        self.tabWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.summary_tab = QtWidgets.QWidget()
        self.summary_tab.setObjectName("summary_tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.summary_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setHorizontalSpacing(6)
        self.gridLayout_3.setVerticalSpacing(20)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.start_scan = QtWidgets.QPushButton(self.summary_tab)
        self.start_scan.setObjectName("start_scan")
        self.gridLayout_3.addWidget(self.start_scan, 8, 0, 1, 2)
        self.record_channel_del_btn = QtWidgets.QPushButton(self.summary_tab)
        self.record_channel_del_btn.setObjectName("record_channel_del_btn")
        self.gridLayout_3.addWidget(self.record_channel_del_btn, 2, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.summary_tab)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setWordWrap(False)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 1, 0, 1, 1)
        self.should_scan_y = QtWidgets.QCheckBox(self.summary_tab)
        self.should_scan_y.setEnabled(True)
        self.should_scan_y.setObjectName("should_scan_y")
        self.gridLayout_3.addWidget(self.should_scan_y, 6, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.summary_tab)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 4, 3, 1, 1)
        self.channel_combobox_x = QtWidgets.QComboBox(self.summary_tab)
        self.channel_combobox_x.setEnabled(True)
        self.channel_combobox_x.setEditable(True)
        self.channel_combobox_x.setObjectName("channel_combobox_x")
        self.channel_combobox_x.addItem("")
        self.gridLayout_3.addWidget(self.channel_combobox_x, 7, 1, 1, 1)
        self.channel_combobox_y = QtWidgets.QComboBox(self.summary_tab)
        self.channel_combobox_y.setEnabled(True)
        self.channel_combobox_y.setEditable(True)
        self.channel_combobox_y.setObjectName("channel_combobox_y")
        self.gridLayout_3.addWidget(self.channel_combobox_y, 6, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.summary_tab)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 4, 4, 1, 1)
        self.should_scan_z = QtWidgets.QCheckBox(self.summary_tab)
        self.should_scan_z.setEnabled(True)
        self.should_scan_z.setChecked(False)
        self.should_scan_z.setObjectName("should_scan_z")
        self.gridLayout_3.addWidget(self.should_scan_z, 5, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.summary_tab)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 7, 0, 1, 1)
        self.channel_combobox_z = QtWidgets.QComboBox(self.summary_tab)
        self.channel_combobox_z.setEnabled(True)
        self.channel_combobox_z.setEditable(True)
        self.channel_combobox_z.setObjectName("channel_combobox_z")
        self.gridLayout_3.addWidget(self.channel_combobox_z, 5, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.summary_tab)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 4, 0, 1, 1)
        self.record_channel_combobox = QtWidgets.QComboBox(self.summary_tab)
        self.record_channel_combobox.setEnabled(True)
        self.record_channel_combobox.setEditable(True)
        self.record_channel_combobox.setObjectName("record_channel_combobox")
        self.gridLayout_3.addWidget(self.record_channel_combobox, 1, 1, 1, 2)
        self.record_channel_add_btn = QtWidgets.QPushButton(self.summary_tab)
        self.record_channel_add_btn.setObjectName("record_channel_add_btn")
        self.gridLayout_3.addWidget(self.record_channel_add_btn, 2, 1, 1, 1)
        self.stop_scan = QtWidgets.QPushButton(self.summary_tab)
        self.stop_scan.setEnabled(False)
        self.stop_scan.setObjectName("stop_scan")
        self.gridLayout_3.addWidget(self.stop_scan, 8, 2, 1, 1)
        self.line = QtWidgets.QFrame(self.summary_tab)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_3.addWidget(self.line, 3, 0, 1, 6)
        self.label_8 = QtWidgets.QLabel(self.summary_tab)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 4, 5, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.summary_tab)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 4, 2, 1, 1)
        self.record_channel_list = QtWidgets.QListWidget(self.summary_tab)
        self.record_channel_list.setEnabled(True)
        self.record_channel_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.record_channel_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.record_channel_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.record_channel_list.setSelectionRectVisible(True)
        self.record_channel_list.setObjectName("record_channel_list")
        item = QtWidgets.QListWidgetItem()
        self.record_channel_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.record_channel_list.addItem(item)
        self.gridLayout_3.addWidget(self.record_channel_list, 1, 3, 2, 2)
        self.record_channel_add_current_btn = QtWidgets.QPushButton(self.summary_tab)
        self.record_channel_add_current_btn.setObjectName("record_channel_add_current_btn")
        self.gridLayout_3.addWidget(self.record_channel_add_current_btn, 1, 5, 1, 1)
        self.record_channel_del_all_btn = QtWidgets.QPushButton(self.summary_tab)
        self.record_channel_del_all_btn.setObjectName("record_channel_del_all_btn")
        self.gridLayout_3.addWidget(self.record_channel_del_all_btn, 2, 5, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.summary_tab)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)
        self.channel_mode_switch_btn = QtWidgets.QPushButton(self.summary_tab)
        self.channel_mode_switch_btn.setEnabled(True)
        self.channel_mode_switch_btn.setAutoDefault(False)
        self.channel_mode_switch_btn.setDefault(False)
        self.channel_mode_switch_btn.setFlat(False)
        self.channel_mode_switch_btn.setObjectName("channel_mode_switch_btn")
        self.gridLayout_3.addWidget(self.channel_mode_switch_btn, 4, 1, 1, 1)
        self.scan_plan_name = QtWidgets.QLineEdit(self.summary_tab)
        self.scan_plan_name.setEnabled(True)
        self.scan_plan_name.setObjectName("scan_plan_name")
        self.gridLayout_3.addWidget(self.scan_plan_name, 0, 1, 1, 5)
        self.start_z_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.start_z_spinbox.setEnabled(True)
        self.start_z_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.start_z_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_z_spinbox.setSpecialValueText("")
        self.start_z_spinbox.setDecimals(6)
        self.start_z_spinbox.setMinimum(-1e+19)
        self.start_z_spinbox.setMaximum(1e+19)
        self.start_z_spinbox.setSingleStep(0.01)
        self.start_z_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.start_z_spinbox.setObjectName("start_z_spinbox")
        self.gridLayout_3.addWidget(self.start_z_spinbox, 5, 2, 1, 1)
        self.step_y_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.step_y_spinbox.setEnabled(True)
        self.step_y_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.step_y_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.step_y_spinbox.setSpecialValueText("")
        self.step_y_spinbox.setDecimals(6)
        self.step_y_spinbox.setMinimum(-1e+19)
        self.step_y_spinbox.setMaximum(1e+19)
        self.step_y_spinbox.setSingleStep(0.01)
        self.step_y_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.step_y_spinbox.setObjectName("step_y_spinbox")
        self.gridLayout_3.addWidget(self.step_y_spinbox, 6, 3, 1, 1)
        self.start_y_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.start_y_spinbox.setEnabled(True)
        self.start_y_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.start_y_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_y_spinbox.setSpecialValueText("")
        self.start_y_spinbox.setDecimals(6)
        self.start_y_spinbox.setMinimum(-1e+19)
        self.start_y_spinbox.setMaximum(1e+19)
        self.start_y_spinbox.setSingleStep(0.01)
        self.start_y_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.start_y_spinbox.setObjectName("start_y_spinbox")
        self.gridLayout_3.addWidget(self.start_y_spinbox, 6, 2, 1, 1)
        self.start_x_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.start_x_spinbox.setEnabled(True)
        self.start_x_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.start_x_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_x_spinbox.setSpecialValueText("")
        self.start_x_spinbox.setDecimals(6)
        self.start_x_spinbox.setMinimum(-1e+19)
        self.start_x_spinbox.setMaximum(1e+19)
        self.start_x_spinbox.setSingleStep(0.01)
        self.start_x_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.start_x_spinbox.setObjectName("start_x_spinbox")
        self.gridLayout_3.addWidget(self.start_x_spinbox, 7, 2, 1, 1)
        self.step_z_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.step_z_spinbox.setEnabled(True)
        self.step_z_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.step_z_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.step_z_spinbox.setSpecialValueText("")
        self.step_z_spinbox.setDecimals(6)
        self.step_z_spinbox.setMinimum(-1e+19)
        self.step_z_spinbox.setMaximum(1e+19)
        self.step_z_spinbox.setSingleStep(0.01)
        self.step_z_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.step_z_spinbox.setObjectName("step_z_spinbox")
        self.gridLayout_3.addWidget(self.step_z_spinbox, 5, 3, 1, 1)
        self.stop_z_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.stop_z_spinbox.setEnabled(True)
        self.stop_z_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.stop_z_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.stop_z_spinbox.setSpecialValueText("")
        self.stop_z_spinbox.setDecimals(6)
        self.stop_z_spinbox.setMinimum(-1e+19)
        self.stop_z_spinbox.setMaximum(1e+19)
        self.stop_z_spinbox.setSingleStep(0.01)
        self.stop_z_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.stop_z_spinbox.setObjectName("stop_z_spinbox")
        self.gridLayout_3.addWidget(self.stop_z_spinbox, 5, 4, 1, 1)
        self.interval_z_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.interval_z_spinbox.setEnabled(True)
        self.interval_z_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.interval_z_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.interval_z_spinbox.setSpecialValueText("")
        self.interval_z_spinbox.setDecimals(6)
        self.interval_z_spinbox.setMinimum(-1e+19)
        self.interval_z_spinbox.setMaximum(1e+19)
        self.interval_z_spinbox.setSingleStep(0.01)
        self.interval_z_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.interval_z_spinbox.setObjectName("interval_z_spinbox")
        self.gridLayout_3.addWidget(self.interval_z_spinbox, 5, 5, 1, 1)
        self.interval_y_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.interval_y_spinbox.setEnabled(True)
        self.interval_y_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.interval_y_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.interval_y_spinbox.setSpecialValueText("")
        self.interval_y_spinbox.setDecimals(6)
        self.interval_y_spinbox.setMinimum(-1e+19)
        self.interval_y_spinbox.setMaximum(1e+19)
        self.interval_y_spinbox.setSingleStep(0.01)
        self.interval_y_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.interval_y_spinbox.setObjectName("interval_y_spinbox")
        self.gridLayout_3.addWidget(self.interval_y_spinbox, 6, 5, 1, 1)
        self.stop_y_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.stop_y_spinbox.setEnabled(True)
        self.stop_y_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.stop_y_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.stop_y_spinbox.setSpecialValueText("")
        self.stop_y_spinbox.setDecimals(6)
        self.stop_y_spinbox.setMinimum(-1e+19)
        self.stop_y_spinbox.setMaximum(1e+19)
        self.stop_y_spinbox.setSingleStep(0.01)
        self.stop_y_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.stop_y_spinbox.setObjectName("stop_y_spinbox")
        self.gridLayout_3.addWidget(self.stop_y_spinbox, 6, 4, 1, 1)
        self.stop_x_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.stop_x_spinbox.setEnabled(True)
        self.stop_x_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.stop_x_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.stop_x_spinbox.setSpecialValueText("")
        self.stop_x_spinbox.setDecimals(6)
        self.stop_x_spinbox.setMinimum(-1e+19)
        self.stop_x_spinbox.setMaximum(1e+19)
        self.stop_x_spinbox.setSingleStep(0.01)
        self.stop_x_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.stop_x_spinbox.setObjectName("stop_x_spinbox")
        self.gridLayout_3.addWidget(self.stop_x_spinbox, 7, 4, 1, 1)
        self.step_x_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.step_x_spinbox.setEnabled(True)
        self.step_x_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.step_x_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.step_x_spinbox.setSpecialValueText("")
        self.step_x_spinbox.setDecimals(6)
        self.step_x_spinbox.setMinimum(-1e+19)
        self.step_x_spinbox.setMaximum(1e+19)
        self.step_x_spinbox.setSingleStep(0.01)
        self.step_x_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.step_x_spinbox.setObjectName("step_x_spinbox")
        self.gridLayout_3.addWidget(self.step_x_spinbox, 7, 3, 1, 1)
        self.interval_x_spinbox = QtWidgets.QDoubleSpinBox(self.summary_tab)
        self.interval_x_spinbox.setEnabled(True)
        self.interval_x_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        self.interval_x_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.interval_x_spinbox.setSpecialValueText("")
        self.interval_x_spinbox.setDecimals(6)
        self.interval_x_spinbox.setMinimum(-1e+19)
        self.interval_x_spinbox.setMaximum(1e+19)
        self.interval_x_spinbox.setSingleStep(0.01)
        self.interval_x_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.interval_x_spinbox.setObjectName("interval_x_spinbox")
        self.gridLayout_3.addWidget(self.interval_x_spinbox, 7, 5, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 3)
        self.gridLayout_3.setColumnStretch(2, 3)
        self.gridLayout_3.setColumnStretch(3, 3)
        self.gridLayout_3.setColumnStretch(4, 3)
        self.gridLayout_3.setColumnStretch(5, 3)
        self.horizontalLayout.addLayout(self.gridLayout_3)
        self.frame = QtWidgets.QFrame(self.summary_tab)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.save_path = QtWidgets.QLineEdit(self.frame)
        self.save_path.setEnabled(True)
        self.save_path.setObjectName("save_path")
        self.horizontalLayout_2.addWidget(self.save_path)
        self.save_folder_dialog_btn = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.save_folder_dialog_btn.sizePolicy().hasHeightForWidth())
        self.save_folder_dialog_btn.setSizePolicy(sizePolicy)
        self.save_folder_dialog_btn.setObjectName("save_folder_dialog_btn")
        self.horizontalLayout_2.addWidget(self.save_folder_dialog_btn)
        self.horizontalLayout_2.setStretch(0, 10)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.extra_info_text = QtWidgets.QPlainTextEdit(self.frame)
        self.extra_info_text.setEnabled(True)
        self.extra_info_text.setPlainText("")
        self.extra_info_text.setObjectName("extra_info_text")
        self.verticalLayout_3.addWidget(self.extra_info_text)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.scan_channel_add_btn = QtWidgets.QPushButton(self.frame)
        self.scan_channel_add_btn.setObjectName("scan_channel_add_btn")
        self.gridLayout_5.addWidget(self.scan_channel_add_btn, 1, 0, 1, 1)
        self.scan_channel_del_btn = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scan_channel_del_btn.sizePolicy().hasHeightForWidth())
        self.scan_channel_del_btn.setSizePolicy(sizePolicy)
        self.scan_channel_del_btn.setObjectName("scan_channel_del_btn")
        self.gridLayout_5.addWidget(self.scan_channel_del_btn, 1, 1, 1, 1)
        self.scan_channel_combobox = QtWidgets.QComboBox(self.frame)
        self.scan_channel_combobox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scan_channel_combobox.sizePolicy().hasHeightForWidth())
        self.scan_channel_combobox.setSizePolicy(sizePolicy)
        self.scan_channel_combobox.setEditable(True)
        self.scan_channel_combobox.setObjectName("scan_channel_combobox")
        self.gridLayout_5.addWidget(self.scan_channel_combobox, 0, 0, 1, 2)
        self.horizontalLayout_4.addLayout(self.gridLayout_5)
        self.scan_channel_list = QtWidgets.QListWidget(self.frame)
        self.scan_channel_list.setEnabled(True)
        self.scan_channel_list.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.scan_channel_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.scan_channel_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.scan_channel_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.scan_channel_list.setTextElideMode(QtCore.Qt.ElideRight)
        self.scan_channel_list.setProperty("isWrapping", False)
        self.scan_channel_list.setObjectName("scan_channel_list")
        item = QtWidgets.QListWidgetItem()
        self.scan_channel_list.addItem(item)
        self.horizontalLayout_4.addWidget(self.scan_channel_list)
        self.horizontalLayout_4.setStretch(0, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.current_status = QtWidgets.QLabel(self.frame)
        self.current_status.setObjectName("current_status")
        self.verticalLayout_3.addWidget(self.current_status)
        self.progressbar = QtWidgets.QProgressBar(self.frame)
        self.progressbar.setEnabled(False)
        self.progressbar.setMaximum(1)
        self.progressbar.setProperty("value", 0)
        self.progressbar.setOrientation(QtCore.Qt.Horizontal)
        self.progressbar.setInvertedAppearance(False)
        self.progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressbar.setObjectName("progressbar")
        self.verticalLayout_3.addWidget(self.progressbar)
        self.horizontalLayout.addWidget(self.frame)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.tabWidget.addTab(self.summary_tab, "")
        self.multi_channel_tab = QtWidgets.QWidget()
        self.multi_channel_tab.setObjectName("multi_channel_tab")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.multi_channel_tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.multi_channel_add_btn = QtWidgets.QPushButton(self.multi_channel_tab)
        self.multi_channel_add_btn.setObjectName("multi_channel_add_btn")
        self.gridLayout_4.addWidget(self.multi_channel_add_btn, 1, 0, 1, 1)
        self.multi_channel_del_btn = QtWidgets.QPushButton(self.multi_channel_tab)
        self.multi_channel_del_btn.setObjectName("multi_channel_del_btn")
        self.gridLayout_4.addWidget(self.multi_channel_del_btn, 1, 1, 1, 1)
        self.multi_channel_list = QtWidgets.QListWidget(self.multi_channel_tab)
        self.multi_channel_list.setObjectName("multi_channel_list")
        self.gridLayout_4.addWidget(self.multi_channel_list, 2, 0, 1, 2)
        self.multi_channel_combobox = QtWidgets.QComboBox(self.multi_channel_tab)
        self.multi_channel_combobox.setObjectName("multi_channel_combobox")
        self.gridLayout_4.addWidget(self.multi_channel_combobox, 0, 0, 1, 2)
        self.gridLayout_4.setColumnMinimumWidth(0, 2)
        self.gridLayout_4.setColumnMinimumWidth(1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.multi_channel_tab)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_5.addWidget(self.label_9)
        self.multi_channel_formula = QtWidgets.QPlainTextEdit(self.multi_channel_tab)
        self.multi_channel_formula.setObjectName("multi_channel_formula")
        self.verticalLayout_5.addWidget(self.multi_channel_formula)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)
        self.tabWidget.addTab(self.multi_channel_tab, "")
        self.settings_tab = QtWidgets.QWidget()
        self.settings_tab.setObjectName("settings_tab")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.settings_tab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.recover_checkBox = QtWidgets.QCheckBox(self.settings_tab)
        self.recover_checkBox.setObjectName("recover_checkBox")
        self.gridLayout_6.addWidget(self.recover_checkBox, 0, 0, 1, 1)
        self.draw_1d_checkBox = QtWidgets.QCheckBox(self.settings_tab)
        self.draw_1d_checkBox.setObjectName("draw_1d_checkBox")
        self.gridLayout_6.addWidget(self.draw_1d_checkBox, 0, 1, 1, 1)
        self.draw_2d_checkBox = QtWidgets.QCheckBox(self.settings_tab)
        self.draw_2d_checkBox.setObjectName("draw_2d_checkBox")
        self.gridLayout_6.addWidget(self.draw_2d_checkBox, 1, 1, 1, 1)
        self.tabWidget.addTab(self.settings_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)

        self.retranslateUi(ScanControl)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ScanControl)

    def retranslateUi(self, ScanControl):
        _translate = QtCore.QCoreApplication.translate
        ScanControl.setWindowTitle(_translate("ScanControl", "GroupBox"))
        ScanControl.setTitle(_translate("ScanControl", "扫描控制"))
        __sortingEnabled = self.scan_plan_list.isSortingEnabled()
        self.scan_plan_list.setSortingEnabled(False)
        item = self.scan_plan_list.item(0)
        item.setText(_translate("ScanControl", "扫描计划1"))
        item = self.scan_plan_list.item(1)
        item.setText(_translate("ScanControl", "扫描计划2"))
        item = self.scan_plan_list.item(2)
        item.setText(_translate("ScanControl", "pinchoff-B1"))
        item = self.scan_plan_list.item(3)
        item.setText(_translate("ScanControl", "pinchoff-P1"))
        item = self.scan_plan_list.item(4)
        item.setText(_translate("ScanControl", "......"))
        self.scan_plan_list.setSortingEnabled(__sortingEnabled)
        self.delete_scan_plan_btn.setText(_translate("ScanControl", "删除扫描计划"))
        self.start_scan_queue_btn.setText(_translate("ScanControl", "开始队列"))
        self.new_scan_plan_btn.setText(_translate("ScanControl", "新建扫描计划"))
        self.stop_scan_queue_btn.setText(_translate("ScanControl", "停止队列"))
        self.start_scan.setText(_translate("ScanControl", "开始扫描"))
        self.record_channel_del_btn.setText(_translate("ScanControl", "移除通道"))
        self.label_11.setText(_translate("ScanControl", "记录通道"))
        self.should_scan_y.setText(_translate("ScanControl", "Y 轴"))
        self.label_6.setText(_translate("ScanControl", "步长"))
        self.channel_combobox_x.setItemText(0, _translate("ScanControl", "UP1"))
        self.label_7.setText(_translate("ScanControl", "终止值"))
        self.should_scan_z.setText(_translate("ScanControl", "Z 轴"))
        self.label_10.setText(_translate("ScanControl", "X 轴"))
        self.label_3.setText(_translate("ScanControl", "轴"))
        self.record_channel_add_btn.setText(_translate("ScanControl", "添加通道"))
        self.stop_scan.setText(_translate("ScanControl", "停止扫描"))
        self.label_8.setText(_translate("ScanControl", "间隔(s)"))
        self.label_5.setText(_translate("ScanControl", "起始值"))
        __sortingEnabled = self.record_channel_list.isSortingEnabled()
        self.record_channel_list.setSortingEnabled(False)
        item = self.record_channel_list.item(0)
        item.setText(_translate("ScanControl", "UB1 = 3.6"))
        item = self.record_channel_list.item(1)
        item.setText(_translate("ScanControl", "lockin freq = 177.32"))
        self.record_channel_list.setSortingEnabled(__sortingEnabled)
        self.record_channel_add_current_btn.setText(_translate("ScanControl", "添加当前界面"))
        self.record_channel_del_all_btn.setText(_translate("ScanControl", "清除所有通道"))
        self.label_12.setText(_translate("ScanControl", "扫描名称"))
        self.channel_mode_switch_btn.setText(_translate("ScanControl", "真实通道"))
        self.label_2.setText(_translate("ScanControl", "数据保存路径"))
        self.save_folder_dialog_btn.setText(_translate("ScanControl", "..."))
        self.label.setText(_translate("ScanControl", "附加信息"))
        self.label_4.setText(_translate("ScanControl", "扫描通道"))
        self.scan_channel_add_btn.setText(_translate("ScanControl", "添加"))
        self.scan_channel_del_btn.setText(_translate("ScanControl", "删除"))
        __sortingEnabled = self.scan_channel_list.isSortingEnabled()
        self.scan_channel_list.setSortingEnabled(False)
        item = self.scan_channel_list.item(0)
        item.setText(_translate("ScanControl", "lockin I_x"))
        self.scan_channel_list.setSortingEnabled(__sortingEnabled)
        self.current_status.setText(_translate("ScanControl", "当前进度"))
        self.progressbar.setFormat(_translate("ScanControl", "%p%"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.summary_tab), _translate("ScanControl", "概览"))
        self.multi_channel_add_btn.setText(_translate("ScanControl", "添加频道"))
        self.multi_channel_del_btn.setText(_translate("ScanControl", "删除频道"))
        self.label_9.setText(_translate("ScanControl", "输入公式（三个轴的值分别用 x、y 和 z （或 x1, x2, x3）代替，轴不扫描时默认为 0）"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.multi_channel_tab), _translate("ScanControl", "虚拟通道设置"))
        self.recover_checkBox.setText(_translate("ScanControl", "完成后回到起始值"))
        self.draw_1d_checkBox.setText(_translate("ScanControl", "画一维图"))
        self.draw_2d_checkBox.setText(_translate("ScanControl", "画二维图"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings_tab), _translate("ScanControl", "其他设置"))
