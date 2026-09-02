## Why

当前 Caffe SSD 模型仅对正面人脸敏感，侧脸和仰头大笑场景识别率低。OpenCV 4.14 内置 YuNet 模型，专为多角度人脸优化，模型仅 ~2MB。

## What Changes

- 新增 YuNet ONNX 模型文件到 `models/`
- `face_detector.py` 新增 YuNet 检测器，与 Caffe 共存
- `detect_faces()` 先调 YuNet，无结果时回退 Caffe SSD
- `maskface.spec` 添加 YuNet 模型打包

## Capabilities

### Modified Capabilities

- `face-blur`: 人脸检测改为 YuNet 优先 + Caffe 回退的双模型策略，提升侧脸和仰角检测率

## Impact

- `face_detector.py`: 新增 `_get_yunet_detector()`、`_detect_yunet()`，修改 `detect_faces()`
- `models/`: 新增 `face_detection_yunet_2023mar.onnx`
- `maskface.spec`: datas 新增一行
- `app.py`: 无改动