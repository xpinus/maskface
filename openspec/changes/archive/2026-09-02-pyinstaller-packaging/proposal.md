## Why

当前 MaskFace 需要用户安装 Python 环境和所有依赖才能运行，且首次使用需联网下载人脸检测模型。通过 PyInstaller 打包为单个 .exe 文件，用户无需任何技术背景即可使用，真正做到"双击即用"。

## What Changes

- 新增 PyInstaller 打包配置，生成单文件 MaskFace.exe
- 人脸检测模型文件内置于 exe，不再依赖网络下载
- face_detector.py 适配 PyInstaller 运行时环境（sys._MEIPASS）
- 移除 face_detector.py 中的运行时模型下载逻辑
- 新增 build.bat 一键构建脚本（下载模型 + 打包）
- 新增 pyinstaller 为开发依赖

## Capabilities

### New Capabilities

- xe-bundle: PyInstaller 单文件打包 —— 将应用打包为独立 .exe，双击即可运行，无需 Python 环境
- model-bundling: 模型文件内置 —— 人脸检测模型嵌入 exe，运行时从内部读取，无需网络
- uild-automation: 一键构建脚本 —— build.bat 自动下载模型并执行 PyInstaller 打包

### Modified Capabilities

<!-- 无现有能力，留空 -->

## Impact

- face_detector.py：移除下载逻辑，新增 PyInstaller 路径检测
- 新增文件：maskface.spec（PyInstaller 配置）、build.bat（构建脚本）、models/（模型文件目录）
- 新增开发依赖：pyinstaller
- 最终产物：dist/MaskFace.exe（约 160-200MB）
- 开发模式不变：uv run python app.py 仍可正常使用