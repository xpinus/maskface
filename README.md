# MaskFace — 视频人脸匿名化工具

自动检测视频中人脸并模糊处理，保护隐私。

## 展示

👉 [在线演示](https://xpinus.github.io/maskface/)

## 功能

- 支持 mp4 / avi / mov / mkv 视频
- 可调节人脸检测置信度与模糊强度
- 实时进度显示，处理完成后预览保存

![界面](https://xpinus.github.io/maskface/asset/ui.png)

## 使用

1. 双击 `MaskFace.exe`
2. 选择视频 → 调整参数 → 点击"开始处理" → 保存结果

## 开发

```bash
uv sync                        # 安装依赖
.venv\Scripts\python app.py    # 运行
build.bat                      # 打包
```

## 依赖

- OpenCV、librosa、scikit-learn、numba
- sv_ttk (Sun Valley 主题)、moviepy