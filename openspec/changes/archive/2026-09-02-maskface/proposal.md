## Why

公开分享视频时，人脸的生物特征和声音的声纹特征可能导致隐私泄露。需要一个简单易用的工具，让用户在本地一键完成人脸模糊和变声处理，无需联网、无需专业知识。

## What Changes

- 新增基于 OpenCV DNN 的人脸检测与高斯模糊功能
- 新增基于 librosa 的音频变调（pitch shift）变声功能
- 新增基于 Gradio 的网页 GUI，支持拖拽上传、参数调节、进度显示、一键下载
- 新增 启动工具.bat 双击启动脚本，自动打开浏览器
- 使用 uv 管理 Python 依赖

## Capabilities

### New Capabilities

- ace-blur: 人脸检测与高斯模糊 —— 逐帧检测视频中的人脸区域，应用高斯模糊以隐藏身份
- oice-changer: 音频变声 —— 提取视频音轨，通过音调变换（pitch shift）改变声音特征
- gradio-gui: Gradio 网页界面 —— 提供拖拽上传、参数调节（模糊强度/变声程度/检测精度）、实时进度条、结果下载

### Modified Capabilities

<!-- 无现有能力，留空 -->

## Impact

- 新增 Python 包依赖：opencv-python, moviepy, librosa, 
umpy, 	qdm, gradio
- 项目结构：pp.py（入口）、ace_detector.py（人脸模块）、oice_changer.py（变声模块）、equirements.txt（或 pyproject.toml）
- 首次运行自动下载 OpenCV DNN 模型（~10MB），缓存至 ~/.video_anonymizer/
- 仅支持本地运行，无需网络（除首次模型下载）
