# 1. 如何安装

## 1. 通过脚本运行
- 安装`Python3`
- 安装依赖: `pip install -r requirements.txt`
- 启动程序: `python main.py (your saved json path)`

## 2. 直接运行可执行文件

### 1. Windows系统
- 直接运行`NodeNote.exe`即可
- 资源文件会自动保存在`C://Assets`

### 2. Linux系统
- 安装qt插件支持: `sudo apt install libxcb-xinerama0`
- 以管理员权限运行: `sudo ./NodeNote`
- 资源文件会自动保存在: `/Assets`

# 2. 如何使用

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.11.png)

## 1. 关于界面的设置
侧边栏显示与隐藏: `Ctrl+B`

## 2. 关于部件的添加与使用

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.12.png)

右键鼠标能够添加两种部件: `Attribute Widget` 和 `Logic Widget`
> `Attribute Widget`: 
- 输入与输出: 四个连线端口
- 文本信息: 中间的输入框允许输入富文本
- 扩大与缩小: 按住`Shift`与鼠标左键, 扩大与缩小结点

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.17.gif)

- 右键允许无限嵌套内容:

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.13.png)

|`Python`代码高亮: `Ctrl+6`| 清除对齐格式: `Ctrl+P` | 加粗: `Ctrl+W` |
| ---- |---- | ---- |
| 水平居左: `Ctrl+[`  |水平居右: `Ctrl+]`   | 水平居中: `Ctrl+\` |
|  斜体: `Ctrl+Q` | 下划线: `Ctrl+R`  | 删除线: `Ctrl+/` |
| 增大字体: `Ctrl+G` | 缩小字体: `Ctrl+H` | 更改字体颜色: `Ctrl+N` |
| 超链接: `Ctrl+M` | 数学公式($sth$): `Ctrl+I` | 清除格式: `Ctrl + L`|
| 撤回: `Crtl+Z` | 重做: `Ctrl+Y` | 表格添加操作: `Ctrl+1` |
| 表格添加列操作: `Ctrl+T` | 表格添加行操作: `Ctrl+R` | 表格删除列操作: `Ctrl+D` |
| 表格删除行操作: `Ctrl+M` | 添加列表: `Ctrl+2` |  调整图片大小: `Ctrl+U` |
| 进入子图: `Alt+left_mouse_press` | | |

> `Logic Widget`:
- 输入与输出: 两个连线端口
- 逻辑控制: 控制输入的与或非真值门

## 3. 关于连线与动画

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.14.png)

- 双击结点端口可以产生连线 
- 选中结点`Ctrl+0`会产生所有与该结点有关的流向动画 | 选中线条只会产生该线条的动画
- 您可以通过调整两个红点位置更改线条位置

## 4. 关于数位板支持

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.15.png)

您可以插入数位板并开始绘画, 线条样式取决于您设定的`Container widget`样式

## 5. 其他功能
- 碰撞检测
- 辅助线对齐

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.16.gif)

- 场景放大与缩小: `Ctrl + -` 和 `Ctrl + +`
- 搜索: `Crtl + F`
- 更改背景图片与飘落图片资源位置: `Resources/Background`
- 自动保存与打开文件: `一般不需要保存, 全自动保存, 如果要保存请按Ctrl+S`, `Ctrl+O: 保存的文件请以json为后缀`

# 3. 基本使用逻辑
对于`Attribute Widget`的四个端口, 左侧两个表示输入, 右侧两个表示输出.

为什么要有两个输入和两个输出呢, 因为为了表示详细的逻辑, 对于自身的真值必须有确定, 我
们得知道连线产生的结果, 是让这个结点的内容变成真的还是假的, 具体可以看这张图

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.12.png)

我们表示的逻辑是: 如果你睡过头了, 你就会迟到. 那么如果我们没睡过头呢, 那也不一定就会赶得上, 比如说我们可能遇到路上堵车,
车坏了等各种情况. 因此我们把这些情况都连在逻辑控件上, 用或门表示只要这些情况有一个为真, 我们输出用and表示(反正也只有一个输出, 因此无关大雅
, 如果有多个输出, 那这个时候or/and/not就不一样了, or表示我们只能影响输出上的部分结点), 那在这里and就表示我们能影响输出上的全部结点(这里只有一个),
我们连在了输入为真的端口上, 到这里我们完成了逻辑表示: 如果我们睡过头了, 那么我们会迟到; 再看, 我们为什么还引入了第二个逻辑控件呢, 
因为这个时候我们要表示只有当这些情况全部为假的时候, 迟到才能为假.

这只是个逻辑案例, 具体怎么使用该软件还要看您自身的表示! 同时我们可以结果内嵌子图, 进入子图, 嵌套结点去表示构成与构成与等各类复杂逻辑, 
哪怕是需要绘图的, 我们也可以通数位板实现自由绘制!

