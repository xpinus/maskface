## Why

处理后的视频出现颜色偏移（红蓝通道交换）且人脸出现瞬间无马赛克。根因是 `cv2.VideoWriter` 的 BGR/RGB 通道混用以及 `FaceTracker` 跳帧插值在新人脸出现时存在盲区。

## What Changes

- 移除 `FaceTracker` 跳帧插值类，改为逐帧调用 `detect_faces()`，消除人脸漏检延迟
- 修复 `cv2.VideoWriter` 写入时的 BGR/RGB 通道错误，直接写入 BGR 帧
- 简化 `face_detector.py`，删除约 40 行不再需要的插值逻辑

## Capabilities

### Modified Capabilities

- `face-blur`: 移除跳帧检测与线性插值要求，改为每帧独立检测；移除模型自动下载要求（改为打包内嵌）

## Impact

- `face_detector.py`: 删除 `FaceTracker` 类，`detect_faces()` 和 `apply_blur()` 保持不变
- `app.py`: 处理管线中 `tracker.process_frame()` 替换为 `detect_faces()`，`out.write()` 直接写入 BGR