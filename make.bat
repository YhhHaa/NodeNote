:: lanague
pylupdate5 -noobsolete ./src/NodeNotePackage/NodeNote/Components/attribute.py ./src/NodeNotePackage/NodeNote/Components/window.py ./src/NodeNotePackage/NodeNote/GraphicsView/view.py -ts ./src/NodeNotePackage/NodeNote/Model/MultiLanguages/zh_CN.ts
lrelease ./src/NodeNotePackage/NodeNote/Model/MultiLanguages/zh_CN.ts

:: google protoc
protoc -I./src/NodeNotePackage/NodeNote/Model/ --python_out=./src/NodeNotePackage/NodeNote/Model/ serialize.proto
