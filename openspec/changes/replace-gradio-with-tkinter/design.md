## Context

当前 app.py 使用 Gradio 6 Blocks API，PyInstaller 打包后因 Gradio 运行时读取 .py 源码而崩溃。Tkinter 是 Python 标准库，无需额外依赖，PyInstaller 打包零问题。

## Goals / Non-Goals

**Goals:**
- 用 Tkinter 重写 app.py，功能等价于 Gradio 版
- 移除 gradio 依赖，简化 PyInstaller 打包
- 保持 face_detector.py 和 voice_changer.py 不变

**Non-Goals:**
- 不改变处理逻辑（人脸检测、变声、合成）
- 不添加批量处理功能
- 不支持拖拽上传（Tkinter 原生不支持，用文件选择对话框替代）

## Decisions

### 1. Tkinter 布局
- **选择**: 单窗口，垂直布局
  - 顶部：文件选择（按钮 + 路径标签）
  - 中部：三个参数滑块（模糊/变声/精度）
  - 底部：进度条 + 状态文字 + 开始按钮
- **理由**: 简单直观，无需多窗口或标签页

### 2. 进度更新
- **选择**: 使用 oot.update() 在循环中刷新 UI
- **理由**: Tkinter 单线程，处理过程中需手动刷新 UI 避免假死
- **备选方案**: 多线程 + queue（更复杂，对单任务场景过度设计）

### 3. 文件保存
- **选择**: iledialog.asksaveasfilename() 弹出保存对话框，默认文件名 maskface_output.mp4
- **理由**: 标准 Tkinter API，用户体验好

### 4. 处理流程
- **选择**: 在主线程中执行，通过 oot.update() 刷新进度
- 流程：验证输入 → 分离音视频 → 逐帧模糊 → 变声 → 合成 → 弹出保存对话框
- **理由**: 保持与现有 process_video 逻辑一致

### 5. 依赖清理
- **选择**: 从 pyproject.toml 移除 gradio，从 maskface.spec 移除所有 gradio 相关配置
- 删除 runtime_hook.py
- **理由**: 彻底清除 Gradio 痕迹，简化打包

## Risks / Trade-offs

- [Tkinter 界面不如 Gradio 现代] → 接受，功能优先
- [无拖拽上传] → 用文件选择对话框替代，用户体验可接受
- [处理大视频时 UI 可能假死] → 使用 root.update() 刷新，大多数视频可接受