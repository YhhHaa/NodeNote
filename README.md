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
Set the thumbnails visible or invisible: `Shift+B`

## 2. How to add widgets and use them.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.12.png)

- you can add widgets by the context menu : `Attribute Widget` and  `Logic Widget` and `Draw Widget` 
- or you can add widgets by shortcur keys like `Alt+Q`->`Attribute Widget`, `Alt+W`->`Logic Wdiegt`, `Alt+E`->`Draw Widget`
> `Attribute Widget`: 
- Input and output: Four ports.
- Text input field : Rich text support.

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
- Expansion and reduction: Press `Shift` and `Lmb` to expand or reduce the attribute widget.

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.17.gif)

- Embedded unlimited sub widgets.:

    ![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.13.png)

- Copy and paste: You can copy one attribute widget by `Alt+R` and paste it anywhere you want by `Alt+T`

- Node hyperlink: You can press `Alt+C` to copy the special node id, and then paste the id which is used as hyperlink by pressing `Ctrl+M` in other node. After that, you can click the hyperlink to navigate to other node.

> `Logic Widget`:
- Input and output: two ports.
- logic controller: two AND-OR-NOT gates.

## 3. Connections and animation.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.14.png)

- You can double click the port widget to create pipe widgets. 
- Press `Ctrl 0` at pipe widget or attribute widget to turn on the animation. 
- You can change the pipe position with two controller points.

## 4. Scene operations.
- You can redirect back to your last scene by `Alt+Z`.
- You can redirect to your parent scene by `Alt+X`.
- You can export current scene without sub scene to .note file by `Shift+S`.
- You can export current scene with sub scene to .note file by `Alt+S`.

## 5. The tablet support.

![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.1tablet.gif)
- you can create a draw widget to draw with a tablet.

- The style which contains the width and the color depends on the draw widget style. 

## 6. Other functions.
![](https://raw.githubusercontent.com/yetao0806/CloudImage/main/Node_Note_0.1collision_detection.gif)
- collision detection
- Auxiliary line alignment
- The view zoom in and zoom out: `Ctrl + -` 和 `Ctrl + +`
- Search everywhere: `Crtl + F`
- Change background image(svg format) and background flowing image(png format): `Resources/Background` and `Resources`
- Save and load: `Ctrl S`(auto sava when close the application) and `Ctrl O` to load `.note` file.
- print items in this scene to image: `Ctrl Alt p`
- print selected items to image: `Ctrl Shift p`
- You can close the flowing image effect function by `F11`

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

## Shortcut Table:
| This is operations of rich text| | |
| ---- |---- | ---- |
|Python highlighter : `Ctrl+9`| Clear alignment: `Ctrl+P` | Bold: `Ctrl+W` |
| Align left : `Ctrl+[`  |Align right : `Ctrl+]`   | Align center : `Ctrl+ \ ` |
|  Italic : `Ctrl+Q` | Underline : `Ctrl+R`  | Strikethrough: `Ctrl+/` |
| Increase the font: `Ctrl+G` | Decrease the font: `Ctrl+H` | Change the font color: `Ctrl+N` |
| Hyper link: `Ctrl+M` | mathematical formula ($LaTeX$): `Ctrl+I` | Clear format: `Ctrl + L`|
| Undo: `Crtl+Z` | Redo: `Ctrl+Y` | Table: `Ctrl+1` |
| Add a row in a table: `Ctrl+3` | Add a column in a table : `Ctrl+2` | Delete a row in a table : `Ctrl+5` |
| Delete a column in a table : `Ctrl+4` | Merge Table: `Ctrl+6` | Spilt Table: `Ctrl+7` |
|Add a list : `Ctrl+8` |  Resize the image : `Ctrl+U` | indent: `Tab` or `Ctrl+Tab`| 
| Copy html text: `Ctrl+C` | Copy plain text: `Ctrl+Shift+C` | Paste: `Ctrl+V` |

| This is operations of widgets | | |
| --- | --- | --- |
| Copy node: `Alt+R` | Paste node: `Alt+T` | Copy node id: `Alt+C` |
| Create node: `Alt+Q` | Create logic widget: `Alt+W` | Create draw widget: `Alt+E` |
| Enter the sub scene of node: `Alt+left_mouse_press` | | |

| This is operations of scene | | |
| --- | --- | --- |
| Expand scene: `F3/4/5/6` | Narrow scene: `F7/8/9/10` | |
| Auxiliary line alignment: `F1` | Undo&&Redo: `F2` | Flowing image effect: `F11` |
| Redirect back to last scene: `Alt+Z` | Redirect to parent scene: `Alt+X` |


| This is operations of file | | |
| --- | --- | --- |
| Save(auto): `Ctrl+S` | Load: `Ctrl+O` |
| Export scene to pic: `Ctrl+Alt+P` | Export selected items to pic: `Ctrl+Shift+P`|
| Export scene to .note without sub scene: `Shift+S`| Export scene to .note with sub scene: `Alt+S`| 

| This is operations of window | |
| --- | --- |
| Show side bar: `Ctrl+B` | Show thumbnails: `Shift+B` |

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

# v.2.8.4
## Function:
- Add thumbnails to index scene quickly.

# v.2.19.7
## Debug: 
- Show the text cursor while editing.
- Create sub widgets in some area of sub view correctly.
- Draw and delete any lines correctly.
## Function:
- Press `Alt+Q` to create attribute widget
- Press `Alt+W` to create logic widget
- Press `Alt+E` to create draw widget

- Press `Alt+C` to copy the id of the attribute widget, and you can use it as hyperlink (`Ctrl+M`) to index the node. You can edit the id after setting it as hyperlink

- Press `Alt+Z` to redirect to last scene
- Press `Alt+X` to redirect to parent scene

- You can change the style of edit box of pipe widget

- Press `Alt+R` to copy one attribute widget, Press `Alt+T` to paste your widget

- Press `F11` to close flowing image effect.

## Changes:
- Change the background into blank
- Intall NodeNote by homebrew


# todo
## Debug:
- [x] Relative path raise an exception when the file is across the drive.
- [x] Pipe not shows in sub view.
- [x] Set Control points at center of pipe.
- [x] Without `Assets` folder, the draw widget can't save to file.
- [x] Saving raises exception when you are dragging pipe.
- [x] Search and redirect to last scene.
- [x] Press `Detele` characters in text box.
- [x] Can't change scene size in sub view.
## Function:
- [ ] Support markdown: Use `https://github.com/pandao/editor.md`(MIT LICENSE).(输入法有时失去焦点)(失去焦点时清空内容)
- [x] Export current scene to .note file.
- [x] Open with nodenote.
- [x] Set default background image.
- [x] Delete sub scene at sidebar and change selection.
- [ ] Show and hide special tag node.
- [x] Init directory.
- [x] Backup .note
- [ ] 导出矢量图
## Changes:
- [x] Change UI.
- [x] Delete Draw widget of sub view which not works.
- [x] Multi languages.
- [x] Different stylesheet interface.
- [ ] Rewrite undo&&redo logic.
- [ ] Show MIT License.
