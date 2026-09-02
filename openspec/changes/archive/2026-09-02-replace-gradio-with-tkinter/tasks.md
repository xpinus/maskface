## 1. 依赖清理

- [x] 1.1 从 pyproject.toml 移除 gradio 依赖
- [x] 1.2 运行 uv sync 更新虚拟环境

## 2. Tkinter GUI 实现

- [x] 2.1 重写 app.py：文件选择按钮 + 路径标签
- [x] 2.2 实现三个参数滑块（模糊强度/变声程度/检测精度），显示当前值
- [x] 2.3 实现进度条和状态文字
- [x] 2.4 实现处理流程：分离音视频 → 逐帧模糊 → 变声 → 合成
- [x] 2.5 实现保存文件对话框
- [x] 2.6 窗口标题"MaskFace - 视频匿名化工具"，适当大小和布局

## 3. PyInstaller 简化

- [x] 3.1 更新 maskface.spec：移除 gradio 隐藏导入、数据收集、runtime_hook
- [x] 3.2 删除 runtime_hook.py

## 4. 验证

- [x] 4.1 开发模式验证：uv run python app.py 正常启动和使用
- [x] 4.2 PyInstaller 打包验证：exe 正常启动，功能完整