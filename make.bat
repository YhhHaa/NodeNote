:: lanague
:: pylupdate5 ./src/NodeNotePackage/NodeNote/Components/attribute.py ./src/NodeNotePackage/NodeNote/Components/window.py ./src/NodeNotePackage/NodeNote/GraphicsView/view.py  ./src/NodeNotePackage/NodeNote/Components/work_dir_interface.py -ts ./src/NodeNotePackage/NodeNote/Resources/MultiLanguages/zh_CN.ts
lrelease ./src/NodeNotePackage/NodeNote/Resources/MultiLanguages/zh_CN.ts

:: google protoc
:: protoc -I./src/NodeNotePackage/NodeNote/Model/ --python_out=./src/NodeNotePackage/NodeNote/Model/ serialize.proto

:: package
:: pyinstaller --noconfirm ./example.spec
