




@dataclass(eq=True, repr=True, init=True)
class ScanPlanInfo:
    save_path: str = ''
    extra_data: str = ''

    channel_formula: dict[Channel, str] = {}

    record_channel_info: list[Channel] = [] # 记录的环境变量

    scan_channel: list[Channel] = [] # 读取的通道
    z_info: AxisInfo = AxisInfo('z')
    y_info: AxisInfo = AxisInfo('y')
    x_info: AxisInfo = AxisInfo('x')

    _name: str = ''

    @property
    def axes(self):
        return (self.z_info, self.y_info, self.x_info)
    
    @property
    def axis_count(self):
        return len([axis for axis in self.axes if axis.enabled])

    @property
    def default_scan_plan_name(self):
        return ''.join(['-{}'.format(axis.name) for axis in self.axes])

    @property
    def name(self):
        return self._name if len(self._name) > 0 else self.default_scan_plan_name

    @name.setter
    def name(self, v):
        self._name = v

    def enable_y(self, v):
        self.y_info.enabled = v
        if not v:
            self.enable_z(v)

    def enable_z(self, v): 
        self.z_info.enabled = v
        if v:
            self.enable_y(v)
    






class ScanExecutor():
    def __init__(self, scan_manager:ScanManager, plan_info:ScanPlanInfo) -> None:
        self.__thread = threading.Thread(target=self.run)
        self.__running_flag = False
        self.__line_data = False
        self.manager = scan_manager
        self.plan_info = plan_info
        
        self.__base_path = abspath(pathjoin(plan_info.save_path, plan_info.name))
        self.__targets = plan_info.scan_channel

        self.__z = plan_info.z_info
        self.__y = plan_info.y_info
        self.__x = plan_info.x_info

        self.__formula: Dict['Channel', str] = {}
        

    @property
    def line_data(self):
        return self.__line_data

    @property
    def base_path(self):
        return self.__base_path
    
    @property
    def targets(self):
        return tuple(self.__targets)

    def makepath(self, *s):
        return pathjoin(self.__base_path, *s)

    def set_zyx(self, z, y, x):
        for channel, formula in self.__formula.items():
            value = eval(formula, accessable_functions, {'x':x, 'y':y, 'z':z})
            channel.write(value)

    def fire_event(self, event:ScanEvent):
        SCAN_EVENT_BUS.fire_event(event)

    def start(self) -> None:
        self.__running_flag = True
        self.fire_event(ScanStartEvent(self.plan_info, self))
        self.manager.lock.acquire()

        # check scan target dimension
        data = [channel.read() for channel in self.__targets]
        if any([
            isinstance(data_entry, Iterable) 
            and not isinstance(data_entry, (bytes, str)) 
            for data_entry in data
            ]
            ):
            self.__line_data = True
            if any([len(data[0]) != len(data_entry) for data_entry in data]):
                raise ScanTargetError('Incompatible Data Length')
            else:
                self.__data_length = len(data[0])
        
        self.fire_event(ScanStartEvent(self.plan_info, self))

        self.__thread.start()
        return

    def run(self):
        final_data = None # the final data pass to ScanEndEvent
        zdata = [] # All z data
        axis_stack = [] 
        if self.__z.enabled:
            self.fire_event(AxisPreIterateEvent(self.plan_info, self.__z, 2, np.array(axis_stack)))
        for z in self.__z.get_range():
            
            if self.__z.enabled:
                self.fire_event(AxisChangeEvent(self.plan_info, axis=self.__z, 2, target_value=z))
                axis_stack.append(z)

            if self.__y.enabled:
                self.fire_event(AxisPreIterateEvent(self.plan_info, self.__y, 1, np.array(axis_stack)))
            
            ydata = []
            for y in self.__y.get_range():
                if self.__y.enabled:
                    self.fire_event(AxisChangeEvent(self.plan_info, self.__y, 1, target_value=y))
                    axis_stack.append(y)

                xdata = []
                for x in self.__x.get_range():
                    axis_stack.append(x)
                    xs = np.array(axis_stack)

                    if not self.__running_flag:
                        self.fire_event(ScanEndEvent(self.plan_info, self, False, False))
                        return
                    

                    self.fire_event(AxisChangeEvent(self.plan_info, self.__x, 0, x))

                    self.fire_event(PreChangeChannelEvent(self.plan_info, xs))
                    self.set_zyx(z, y, x)
                    self.fire_event(PostChangeChannelEvent(self.plan_info, xs))
                    
                    time.sleep(self.__x.interval)

                    self.fire_event(PreMeasureEvent(self.plan_info, xs))
                    data_entry = ScanData(np.array(xdata), np.array([channel.read() for channel in self.__targets]))
                    self.fire_event(PostMeasureEvent(self.plan_info, data_entry.x, data_entry))

                    xdata.append(data_entry)
                    axis_stack.pop()

                data = ScanData(axis_stack, np.array(xdata))
                self.fire_event(AxisPostIterateEvent(self.plan_info, self.__x, 0, data))
                final_data = data
                
                if self.__y.enabled:
                    ydata.append(data)
                    axis_stack.pop()

            if self.__y.enabled:
                data = ScanData(axis_stack, np.array(ydata))
                self.fire_event(AxisPostIterateEvent(self.plan_info, self.__y, 1, data))
                final_data = data
                if self.__z.enabled:
                    zdata.append(data)
                    axis_stack.pop()
            

        if self.__z.enabled:
            axis_stack.pop()
            data = ScanData(axis_stack, np.array(zdata))
            final_data = data
            self.fire_event(AxisPostIterateEvent(self.plan_info, self.__z, 2, data))

        self.fire_event(ScanEndEvent(self.plan_info, self, True, True, final_data))
        self.manager.lock.release()

    def stop(self):
        self.__running_flag = False
        while self.__thread.is_alive(): pass
        self.manager.lock.release()
    
