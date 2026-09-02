## Purpose

提供基于 Tkinter 的原生桌面窗口界面，让用户选择视频文件、调节参数、一键处理并下载匿名化结果。

## ADDED Requirements

### Requirement: 视频选择
系统 SHALL 提供文件选择对话框，支持 mp4、avi、mov、mkv 格式的视频文件。

#### Scenario: 选择视频文件
- **WHEN** 用户点击"选择视频"按钮并选取 mp4 文件
- **THEN** 系统显示文件路径，准备处理

#### Scenario: 不支持的格式
- **WHEN** 用户选择不支持的格式（如 .wav）
- **THEN** 系统弹出警告提示支持的格式列表

### Requirement: 参数调节
系统 SHALL 提供滑块控件供用户调节：模糊强度（1-99，奇数）、变声程度（-12 到 +12 半音）、检测精度（0.1-1.0），并显示当前值。

#### Scenario: 默认参数值
- **WHEN** 应用启动
- **THEN** 滑块显示默认值：模糊强度 55、变声 -5 半音、检测精度 0.5

### Requirement: 处理进度
系统 SHALL 在处理过程中显示进度条和状态文字，让用户了解当前处理阶段。

#### Scenario: 处理中显示进度
- **WHEN** 用户点击"开始处理"按钮
- **THEN** 进度条从 0% 递增至 100%，状态文字显示当前阶段

### Requirement: 结果下载
系统 SHALL 在处理完成后弹出保存文件对话框，用户可选择保存路径。

#### Scenario: 处理完成保存
- **WHEN** 视频处理全部完成
- **THEN** 弹出保存对话框，默认文件名为 maskface_output.mp4

### Requirement: 桌面窗口
系统 SHALL 以原生桌面窗口形式运行，窗口标题为"MaskFace - 视频匿名化工具"，包含关闭按钮。

#### Scenario: 双击启动
- **WHEN** 用户双击 启动工具.bat 或 MaskFace.exe
- **THEN** 弹出桌面窗口，无需浏览器