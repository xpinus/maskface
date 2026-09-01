# 视频匿名化工具：人脸高斯模糊 + 变声（Gradio GUI）

## 摘要

构建一个带 Gradio 网页界面的视频匿名化工具。用户双击 `.bat` 文件即可启动，浏览器自动打开操作界面，拖拽上传视频，调节参数，一键处理并下载结果。

---

## 技术栈

| 组件 | 库 | 用途 |
|------|-----|------|
| 人脸检测 | `opencv-python` (DNN) | 加载 SSD 模型逐帧检测人脸 |
| 人脸模糊 | `opencv-python` | 高斯模糊人脸区域 |
| 音视频拆合 | `moviepy` | 分离/合成音视频轨（自带 ffmpeg） |
| 变声 | `librosa` | 音调变换（pitch shift） |
| 界面 | `gradio` | 网页 GUI，拖拽上传，进度条 |
| 进度条 | `tqdm` | 处理进度显示 |

---

## 项目结构

```
D:\project\_myself\maskface\
├── app.py                 # Gradio GUI 入口
├── face_detector.py       # 人脸检测 + 高斯模糊模块
├── voice_changer.py       # 音频变声模块
├── requirements.txt       # 依赖清单
└── 启动工具.bat            # 双击启动脚本
```

---

## 各模块职责

### face_detector.py

- 下载并缓存 OpenCV DNN 模型（res10_300x300_ssd，约 10MB），首次自动下载到 `~/.video_anonymizer/`
- `detect_faces(frame)` → `[(x, y, w, h, confidence), ...]`
- `apply_blur(frame, faces, kernel_size)` → 对每个人脸区域做高斯模糊，返回处理后的帧
- 跳帧检测 + 线性插值平滑人脸位置（每 N 帧检测一次，中间帧复用）

### voice_changer.py

- 从 moviepy VideoFileClip 提取音频
- `librosa.effects.pitch_shift` 音调变换
- 写回 AudioFileClip

### app.py（Gradio 界面）

- 布局：左侧参数区、右侧进度区
- 组件：
  - 视频上传（拖拽或点击，支持 mp4/avi/mov/mkv）
  - 模糊强度滑块（1~99，奇数，默认 55）
  - 变声程度滑块（-12 ~ +12 半音，默认 -5）
  - 检测精度滑块（0.1 ~ 1.0，默认 0.5）
  - "开始处理"按钮
  - 实时进度条
  - 处理完成后显示下载按钮
- 设置 `inbrowser=True` 启动时自动打开浏览器

### 启动工具.bat

```bat
@echo off
title 视频匿名化工具
python app.py
pause
```

---

## 处理流程

```
用户上传视频 + 设置参数 → 点击"开始处理"
  │
  ├─ 1. 分离音视频轨 (moviepy)
  ├─ 2. 视频轨：逐帧人脸检测 → 高斯模糊 → 写入临时视频
  ├─ 3. 音频轨：提取 → pitch_shift 变调 → 写回
  ├─ 4. 合成最终视频 (moviepy)
  └─ 5. 返回下载链接，Gradio 显示进度
```

---

## 命令行接口（备选，不依赖 GUI）

```
python video_anonymizer.py <input> [options]

Options:
  -o, --output PATH        输出文件路径 (默认: output_anonymized.mp4)
  --blur INT              高斯模糊核大小，奇数 (默认: 55)
  --pitch FLOAT           音调变换半音数，负=低沉 (默认: -5)
  --confidence FLOAT      人脸检测置信度阈值 0-1 (默认: 0.5)
  --skip INT              跳帧间隔 (默认: 5)
  --no-voice              不处理音频
  --no-face               不处理人脸
```

---

## 依赖清单

```
opencv-python>=4.8
moviepy>=2.0
librosa>=0.10
numpy>=1.24
tqdm>=4.65
gradio>=4.0
```

---

## 假设

- 默认高斯模糊核 55（1080p 视频适中），变声 -5 半音（低沉效果）
- 首次运行自动下载人脸检测模型（~10MB），需联网
- 处理大视频时内存占用较高，建议处理 1080p 及以下分辨率
- 最终输出 MP4 格式
