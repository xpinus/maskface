## Purpose

将人脸检测 DNN 模型文件嵌入可执行文件内部，运行时从内部读取，彻底移除网络下载依赖。

## ADDED Requirements

### Requirement: 模型内置
系统 SHALL 将人脸检测模型文件（deploy.prototxt 和 caffemodel）作为数据文件打包进 exe。

#### Scenario: 模型随 exe 分发
- **WHEN** 用户获得 MaskFace.exe
- **THEN** 模型文件已包含在 exe 内部，无需额外下载

### Requirement: 运行时从内部读取
系统 SHALL 在 PyInstaller 打包模式下从 sys._MEIPASS 临时目录读取模型文件。

#### Scenario: 打包模式加载模型
- **WHEN** 应用以 exe 形式运行
- **THEN** 从 exe 内部提取的临时目录加载模型，人脸检测正常工作

### Requirement: 移除下载逻辑
系统 SHALL 移除 face_detector.py 中的网络下载代码，模型仅通过内置方式提供。

#### Scenario: 无网络时启动
- **WHEN** 在无网络环境中启动 MaskFace.exe
- **THEN** 人脸检测功能正常可用，不尝试联网下载

### Requirement: 开发模式兼容
系统 SHALL 在开发模式（非 PyInstaller 运行时）下仍从 ~/.video_anonymizer/ 读取模型文件。

#### Scenario: 开发模式启动
- **WHEN** 通过 uv run python app.py 启动
- **THEN** 从 ~/.video_anonymizer/ 读取模型，功能正常