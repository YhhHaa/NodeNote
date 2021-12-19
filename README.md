![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.1example.png)

#  [Video](https://youtu.be/pZGTFw3TL4U)

# 1. How to install

## 1. Run through python script
- Install python: `>=Python3.6`
- Install dependence: `pip install -r requirements.txt`
- Run: `python main.py (your saved .note path)`

## 2. Run through executable files

### 1. Windows OS
- Run `NodeNote.exe`
- Resource file will be saved in `Assets` in the current directory

### 2. Linux OS
- Install the package: `sudo apt install libxcb-xinerama0`
- Run: `./NodeNote`
- Resource file will be saved in `Assets` in the current directory

### 3. Mac OS
- Run: `NodeNote.app`
- Resource file will be saved in `Assets` in the current directory

## 3. Custom development
- You can install the python package: `pip install NodeNotePackage or python setup.py install`
- You can run the example in `NodeNotePackage/Examples/example.py`
- Here is the documentation in `doc/build/html/index.html`


# 2. How to use

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.11.png)

## 1. Interface Settings
Set the sidebar visible or invisible : `Ctrl+B`

## 2. How to add widgets and use them.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.12.png)

you can add widgets by the context menu : `Attribute Widget` and  `Logic Widget` and `Draw Widget` 
> `Attribute Widget`: 
- Input and output: Four ports.
- Text input field : Rich text support.
- Expansion and reduction: Press `Shift` and `Lmb` to expand or reduce the attribute widget.

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.17.gif)

- Embedded unlimited sub widgets.:

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.13.png)

|Python highlighter : `Ctrl+9`| Clear alignment: `Ctrl+P` | Bold: `Ctrl+W` |
| ---- |---- | ---- |
| Align left : `Ctrl+[`  |Align right : `Ctrl+]`   | Align center : `Ctrl+ \ ` |
|  Italic : `Ctrl+Q` | Underline : `Ctrl+R`  | Strikethrough: `Ctrl+/` |
| Increase the font: `Ctrl+G` | Decrease the font: `Ctrl+H` | Change the font color: `Ctrl+N` |
| Hyper link: `Ctrl+M` | mathematical formula ($LaTeX$): `Ctrl+I` | Clear format: `Ctrl + L`|
| Undo: `Crtl+Z` | Redo: `Ctrl+Y` | Table: `Ctrl+1` |
| Add a row in a table: `Ctrl+3` | Add a column in a table : `Ctrl+2` | Delete a row in a table : `Ctrl+5` |
| Delete a column in a table : `Ctrl+4` | Merge Table: `Ctrl+6` | Spilt Table: `Ctrl+7` |
|Add a list : `Ctrl+8` |  Resize the image : `Ctrl+U` | Enter the sub scene : `Alt+left_mouse_press` |
| indent: `Tab` or `Ctrl+Tab`| 

> `Logic Widget`:
- Input and output: two ports.
- logic controller: two AND-OR-NOT gates.

## 3. Connections and animation.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.14.png)

- You can double click the port widget to create pipe widgets. 
- Press `Ctrl 0` at pipe widget or attribute widget to turn on the animation. 
- You can change the pipe position with two controller points.

## 4. The tablet support.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.1tablet.gif)
- you can create a draw widget to draw with a tablet.

- The style which contains the width and the color depends on the draw widget style. 

## 5. Other functions.
- collision detection
- Auxiliary line alignment

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.1collision_detection.gif)

- The view zoom in and zoom out: `Ctrl + -` 和 `Ctrl + +`
- Search everywhere: `Crtl + F`
- Change background image(svg format) and background flowing image(png format): `Resources/Background` and `Resources`
- Save and load: `Ctrl S`(auto sava when close the application) and `Ctrl O` to load `.note` file.
- print items in this scene to image: `Ctrl Alt p`
- print selected items to image: `Ctrl Shift p`

# 3. How to note your knowledge 
For the four ports of the specified `attribute widget`, the left side of the two represents the input, and the two represent the output on the right.
The ports on the top are `TRUE` values and the ports on the bottom are `FALSE` values. 

Why do you have two inputs and two outputs, because for the detailed logic, you have to be certain of your true values of the info,
We have to know whether the ports define the information `TRUE` or `FALSE`.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.12.png)

The logic we're saying is that if you oversleep, and you're going to be late, then if we don't oversleep, it's not necessarily the case, for example, we might have a traffic jam on the road.

We connect the `TRUE` port of `oversplept` node with a `Or` gate of logical controller, and so are others. It is saying that just one of all these `Reasons` is `TRUE`, you can
make the logic circulate.

With the second logic controller,it is saying only all these `Reasons` are `FALSE`, the `late` can be `FALSE`

Also, We can use tablet to help us note sth that text/logic can not express.

# 4. Finally
If you meet any problems or want to give a valuable suggestion, please email to `helper033@163.com` or create an issue.


# v2.7.2:
## Function:
- Press Control and left mouse button to drag `attribute widget` into next line of others.(Control must be pressed after left mouse button!!)
## Debug:
- Fixed the wrong position of input text field widget in subview.
## Changed:
- Set cache mode to DeviceCoordinateCache->(logic widget, file widget, flower widget)
- Press F1 to turn on/off the line.
- Press F2 to turn of/off the undo&&redo
- Press F3456 to expand left/right/top/bottom position of scene
- Press f78910 to narrow left/right/top/bottom position of scene

# v2.7.4:
## Debug:
- Restore the scene rect.
- Delete pipes correctly.

# v.2.8.4
## Function:
- Add thumbnails to index scene quickly.

# todo
## Debug: 
- Show the text cursor while editing.
## Function:
- Press `Alt+Q` to create attribute widget
- Press `Alt+W` to create logic widget
- Press `Alt+E` to create draw widget

- Press `Alt+C` to copy the id of the attribute widget, and you can use it as hyperlink (`Ctrl+M`) to index the node. You can edit the id after setting it as hyperlink

- Press `Alt+Z` to redirect to last scene

- Change the background into blank

- Change the style of edit box of pipe widget

- Press `Alt+X` to redirect to parent scene
- 复制剪切节点
- 漂浮特效可关闭
## Changed:
- 安装通过homebrew
