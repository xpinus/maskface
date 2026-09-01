## Why

Gradio 6 在运行时读取自身 .py 源码做类型推断，与 PyInstaller 打包模式不兼容（仅打包 .pyc 不含源码）。Tkinter 是 Python 标准库，无需额外依赖，PyInstaller 打包零问题，exe 体积可从 215MB 缩减至约 60MB。

## What Changes

- 重写 app.py：用 Tkinter 替换 Gradio 作为 GUI 框架
- 移除 gradio 依赖，pyproject.toml 中删除 gradio
- 简化 maskface.spec，移除 gradio 相关的隐藏导入和数据收集
- 移除 runtime_hook.py（不再需要）
- 启动方式改为直接弹出桌面窗口，而非浏览器
- face_detector.py 和 voice_changer.py 保持不变

## Capabilities

### New Capabilities

- 	kinter-gui: Tkinter 桌面界面 —— 文件选择对话框、参数滑块、进度条、下载按钮，原生桌面窗口

### Modified Capabilities

- gradio-gui: 替换为 Tkinter 实现，功能规格不变（参考 maskface 变更中的 gradio-gui spec），仅实现方式改变

## Impact

- app.py：完全重写，Tkinter 布局（文件选择 + 滑块 + 进度条 + 按钮）
- pyproject.toml：移除 gradio 依赖
- maskface.spec：移除 gradio 相关配置，移除 runtime_hook
- runtime_hook.py：删除
- 启动工具.bat：不变（仍调用 uv run python app.py）
- exe 体积预计从 215MB 降至 ~60MB