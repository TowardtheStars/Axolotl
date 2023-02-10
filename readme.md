# Axolotl

实验室测量扫图框架，基于 Python 3.9



## 安装需求
- Python 3.9
- numpy
- matplotlib
- PyQt5
- ruamel.yaml

## 功能

Axolotl 将所连接到仪器的各个可配置的参量分解为独立的“通道”并统一管理，可以将多台不同型号、不同厂家、不同功能的仪器从**软件**层面整合为一台“一体机”。
Axolotl 自身只是一个框架，并提供编程接口，并不提供具体的仪器控制程序和驱动，具体仪器的控制方法和驱动软件请咨询仪器生产商；另外，出于同样的原因，也无法保证您在实验中不会遇到故障。

- 虚拟一体机：把实验中用到的任何仪器整合到一个界面上（程序上的或 GUI 上的），一台随意组合的一体机！
- 慢慢来：在改变通道的值时，您可以设置特定通道改变的具体路径和时延，拒绝电压跳变！当然，也可以通过设置，允许特定通道产生跳变
- 多线程：在改变不同通道的值时，除非特殊设置，否则这些通道会几乎同时地改变自身的值
- 通用性：在获取到仪器的驱动和控制程序后，您只需要设置仪器提供的“通道”并 `import` 到您的主程序中，即可接入 Axolotl
- 免费且开源：本框架根据 GNU GPL v3.0 协议开源。若您对该框架有任何想法，可以随时改动、提建议
- 扫描器：一个基本的最多支持 3 个轴的扫描器
- 插件系统：基于事件系统的扫描器插件，数据保存、画图都由此实现
