<div align="center">
    <div>
        <img src="https://github-readme-stats.vercel.app/api?username=yetao0806&show_icons=true&theme=gruvbox_light">
    </div>
    <a href="https://github.com/yetao0806/">
        <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
    </a>
    <a href="https://github.com/yetao0806/">
        <img src="https://img.shields.io/badge/author-YeTao-lightgrey" alt="YeTao">
    </a>
    <a href="https://pypi.org/project/PyQt5/">
    <img src="https://img.shields.io/badge/language-PyQt5-orange">
    </a>
</div>

# NodeNote

# 1. 如何运行

## 1. 不同平台的方式

### 1. 使用脚本方式运行
1. 安装`python`: `Python版本` >= 3.6
2. 安装依赖: `pip install -r requirements.txt`
3. 运行脚本: `python example.py`

### 2. 使用可执行文件运行
- Windows: 运行`NodeNote.exe`
- Mac: 运行`NodeNote.app`
- Linux: 
    1. 安装依赖: `sudo apt install libxcb-xinerama0` << `(Unbuntu)`
    2. 运行`NodeNote`二进制文件

## 2. 打开后的工作区介绍

> 1. 进入工作区: 现版本采用工作区结构, 
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_15work_dir_interface.png)
 - 双击上次打开的目录可以直接打开目录
 - 也可以选择打开工作区目录按钮, 选择你的文件夹
  
> 2. 工作区结构: 第一次打开空白工作区会生成以下文件
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231111754.png)
- `.NOTENOTE`: 记录你创建工作区的时间以及保存你上次打开过的文件
- `Resources`: 程序运行所需的资源文件
- `Notes`: 创建笔记所在的目录, 您的`.note`格式笔记最好都创建在该文件夹, 因为如果没有上次打开的文件, 则在该目录检索, 如果没有检索到, 则在该目录新建一个`.note`格式文件
- `History`: 运行时的文件每隔3分钟会自动备份一份到该文件夹, 如果资源过大可以定时清理! 一个`.note`小型的话大概只有`几KB`.
- `Documents`: 您的markdown文件备份
- `Attachments`: 当你使用节点的附件功能时, 会自动拉取该文件到这个文件夹
- `Assets`: 您的笔记所用到的图片都保存在这个文件夹
  
> 过去版本迁移
- 将根目录的`Assests`移动到工作区目录
- 将您的`.note`文件移动到`Notes`即可

# 2. 如何使用小部件
## 1. `Alt+Q`或者`鼠标右键` 创建`属性控件`: 支持富文本, markdown, 以及其他小部件的嵌套
> 支持的嵌套类型
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231112935.png)
- 嵌套自身
- 嵌套子图: 相当于一个存在于当前场景的自由的子场景
- 嵌套`todo控件`: 
  - 用于你的任务控制, 点开始按钮则开始计时, 左侧是总时间, 右侧是你开始计时之后的时间. 
  - 结束计时后, 会将你的右侧时间加到左侧总时间上.
- 嵌套`附件控件`: 
  - `cover`是你的附件图片,可以自定义; 
  - `File`是你要添加的附件.添加完成后, 会将你的附件拉到当前目录的`Attachments`中.
  - 添加完成后, 双击图片则会调用系统默认的打开程序打开你的附件.

> 支持的富文本操作: 

|Python高亮 : `Ctrl+9`| 清空对齐格式: `Ctrl+P` | 加粗: `Ctrl+W` |
| --- | --- | --- |
| 左对齐 : `Ctrl+[`  |右对齐 : `Ctrl+]`   | 居中对齐 : `Ctrl+ \ ` |
| 斜体 : `Ctrl+Q` | 下划线 : `Ctrl+R`  | 删除线: `Ctrl+/` |
| 增大字体: `Ctrl+G` | 缩小字体: `Ctrl+H` | 改变字体颜色: `Ctrl+N` |
| 超链接: `Ctrl+M` | 数学公式($MaJax$): `Ctrl+I` | 清空所有格式: `Ctrl + L`|
| 撤销上一步: `Crtl+Z` | 恢复上一步: `Ctrl+Y` | 创建一个表格: `Ctrl+1` |
| 增加一行表格: `Ctrl+3` | 增加一列表格 : `Ctrl+2` | 删除一行表格 : `Ctrl+5` |
| 删除一列表格 : `Ctrl+4` | 选中表格后合并表格行列: `Ctrl+6` | 合并表格后拆分已合并内容: `Ctrl+7` |
| 添加一个列表 : `Ctrl+8` |  改变插入图片的大小 : `Ctrl+U` | 文字向后缩进或向前缩进: `Tab` or `Ctrl+Tab`| 
| 复制html内容: `Ctrl+C` | 复制纯文本内容: `Ctrl+Shift+C` | 粘贴: `Ctrl+V` |

> 支持的Markdown操作:
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231115038.png)

- 选中小部件后在侧边栏进行编辑, 当退出侧边栏时, 会自动保存`markdown`到数据库以及备份文件中
- 支持的Markdown类型有: 所有基本`markdown`以及`UML`, `代码块高亮`, `LaTeX`, `绘图` 具体可以移步该项目 >> [tui.editor](https://github.com/nhn/tui.editor)
- 插入图片请使用相对路径: `../Assets/您的图片`
  
> 支持的真值

- 可以注意到每个节点都有四个端口, 上面两个是真值为真的输入输出端口, 下面两个是真值为假的输入输出端口
- 通过按照相应真值的端口进行连线, 结合下面的逻辑部件, 可以表示出你想要的逻辑.

> 支持的复制节点以及粘贴
- 您可以使用`Alt+R`复制该节点以及其内部所有内容
- 然后可以通过`Alt+T`粘贴其到任意一个场景中


## 2. `Alt+W`或`鼠标右键`创建`逻辑控件`: 使用两个与或非门进行逻辑的控制

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231115413.png)
- 上面的是输入的`与或非门`, 下面的是输出的`与或非门`
- 当你有多个输入的时候
  - 调整输入成`或门`, 则表示所有输入, 仅需一个成立, 则输出成立
  - 调整输入成`与门`, 则表示所有输入, 全部都得成立, 则输出成立
  - 调整输入成`非门`, 则表示将输入结果逆反, 例如你从`逻辑部件`的真值为假的端口连到`逻辑控件`, 则逆反后为真
- 当你有多个输出的时候
  - 调整输出成`或门`, 则表示所有输出, 仅有部分成立
  - 调整输出成`与门`, 则表示所有输出, 全部都成立
  - 调整输出成`非门`, 则表示将输出结果逆反

## 3. `Alt+E`或`鼠标右键`创建`绘画部件`

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231120147.png)

- 请先连接数位板
- 支持橡皮擦功能, 现在数位板驱动中, 将你的笔其中一个按钮设置为橡皮擦.

## 4. 通过`双击其他部件端口`创建连线
- 连线选中后可以通过两个`控制点`控制连线的位置

  ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231123727.png)
- 可以在`属性控件`上按`Ctrl+0`生成与之相关所有连线的`ui动画`, 观察逻辑流向
  
  ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231123922.png)

- 也可以在`连线`上单独使用`Ctrl+0`生成选中`连线`的逻辑动画


## 5. 结合上述所有部件的碰撞检测
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_15GIF%202021-12-31%2012-58-45.gif)

- 您可以拖动`属性部件`碰撞其他部件
  - 直接拖动到其他`属性部件`: 将自身添加进其他`属性部件`的当前行
  - 拖动到其他`属性部件`时, 按住`Ctrl`: 将自身添加进其他`属性部件`的下一行
  - 拖动到`连线`: 自动插入该部件到连线的中间
- 您可以在`属性部件`中进行碰撞检测
  - 删除`属性控件`的子控件会生成一个雪花图案, 通过碰撞雪花图案, 可以替代其位置
- 您可以使用右键的上下文菜单调整自身在其他`属性控件`内的位置


# 3. 如何使用场景

## 1. 创建子场景
- 每个`子场景`都与一个`属性控件`绑定, 您可以通过`Alt+鼠标左键`点击小部件, 创建其子场景.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231120617.png)

- 创建子场景后, 会在侧边栏的目录中生成你的索引, 您可以通过索引找到相应的子场景
  - 可以通过`Alt+Z`返回上一次的场景
  - 可以通过`Alt+X`返回父场景
  
## 2. `属性控件`与其他`属性控件`跨越场景的超链接跳转
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231121418.png)
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231121505.png)
  - 通过`Alt+C`复制该节点的`id`
  - 在其他节点中输入该`id`, 通过`Ctrl+M`将其变为超链接
  - 变为超链接后, 您可以自由修改其`id`字符串, 存储的跳转信息不会因为其字符串改变而改变了
  
## 3. 基本设置
- 扩大场景(左右上下): `F3/4/5/6`
- 缩小场景(左右上下): `F7/8/9/10`
- 打开辅助线功能(默认开启): `F1`
- 打开Undo&&Redo功能(默认开启): `F2`
- 打开飘落的图片特效(默认开启): `F11`
- 打开搜索栏: `Ctrl+F`
- 缩放视图: `Ctrl +-`
- 打开缩略图: `Shift+B`
    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/V_2_31_1520211231122330.png)

# 4. 文件分享与导出操作
## 1. 导出该场景到`.note`文件
- 不导出该场景下的子场景, 仅导出该场景的内容: `Shift+S`
- 导出该场景下的所有递归子场景: `Alt+S`
## 2. 导出该场景到`png`图片
- 导出该场景所有内容: `Ctrl+Alt+P`
- 导出该场景选中部件的内容: `Ctrl+Shift+P`

# 5. UI的操作
- 您可以通过`Ctrl+B`打开`侧边栏`
  - 侧边栏拥有文件夹视图: 您可以通过右键上下文菜单`创建`或`删除`文件, 以及通过鼠标左键切换`.note`文件
  - 场景+Markdown视图: 这是您该`.note`笔记的结构
  - 样式自定义视图: 您可以通过该视图自定义所有样式
    - 目前的窗口样式可以通过`qss`文件进行修改, 我只做了一个, 感兴趣的朋友可以参照`Resources/Stylesheets`目录下的`qss`仿照一个, 然后可以通过样式按钮加载你写的`qss`文件.
    - 其他部件样式支持`所有场景`, `当前场景`, `选中部件`样式的修改
- 您可以通过`Alt+G`调整侧边栏到左边或上边
- 您可以通过拉动侧边栏以及内部的条进行调整大小
  
# 6. 最后
> 感谢您使用`NodeNote`, 如果遇到任何问题或想提建, 欢迎创建一个`issue`

> 如果有朋友想参与项目, 非常欢迎. 目前要是有人能多写几个`qss样式表`就好了哈哈哈哈.
1. `clone`该仓库
2. 修改代码
3. 创建新`brand`
4. `push`到我的`main`分支
5. 我会根据实际情况进行合并分支
