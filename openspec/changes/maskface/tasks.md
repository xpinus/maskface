## 1. 项目初始化

- [x] 1.1 使用 uv init 初始化项目，生成 pyproject.toml
- [x] 1.2 添加依赖：opencv-python, moviepy, librosa, numpy, tqdm, gradio
- [x] 1.3 创建启动工具.bat 双击启动脚本

## 2. 人脸检测与模糊模块

- [x] 2.1 实现 face_detector.py：下载并缓存 OpenCV DNN SSD 模型到 ~/.video_anonymizer/
- [x] 2.2 实现 detect_faces(frame) 函数：返回 [(x, y, w, h, confidence), ...]
- [x] 2.3 实现 apply_blur(frame, faces, kernel_size) 函数：对每个人脸区域做高斯模糊
- [x] 2.4 实现跳帧检测 + 线性插值平滑逻辑

## 3. 音频变声模块

- [x] 3.1 实现 voice_changer.py：从 VideoFileClip 提取音频
- [x] 3.2 实现 pitch_shift 变调处理，支持 -12 到 +12 半音
- [x] 3.3 实现处理后的音频写回 AudioFileClip

## 4. Gradio 界面

- [x] 4.1 实现 app.py：左侧参数区 + 右侧进度区布局
- [x] 4.2 实现视频上传组件（拖拽/点击，支持 mp4/avi/mov/mkv）
- [x] 4.3 实现参数滑块：模糊强度（1-99，奇数）、变声程度（-12~+12）、检测精度（0.1~1.0）
- [x] 4.4 实现处理流程：分离音视频 -> 逐帧模糊 -> 变声 -> 合成 -> 返回下载
- [x] 4.5 实现实时进度条和下载按钮
- [x] 4.6 设置 inbrowser=True 自动打开浏览器

## 5. 验证

- [x] 5.1 端到端测试：上传测试视频，验证人脸模糊和变声效果
- [x] 5.2 验证 .bat 双击启动流程