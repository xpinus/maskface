## 1. 模型准备

- [x] 1.1 下载 `face_detection_yunet_2023mar.onnx` 到 `models/`
- [x] 1.2 `maskface.spec` datas 添加 `('models/face_detection_yunet_2023mar.onnx', 'models')`

## 2. face_detector.py — 双模型检测

- [x] 2.1 新增 `YUNET_PATH` 和 `_get_yunet_detector()` 线程局部加载
- [x] 2.2 新增 `_detect_yunet(frame, confidence)` 函数，返回与 Caffe 一致的格式
- [x] 2.3 修改 `detect_faces()`：先调 `_detect_yunet`，无结果时回退原 Caffe 逻辑

## 3. 验证

- [ ] 3.1 本地运行，侧脸视频测试检测率
- [ ] 3.2 仰头大笑场景测试
- [ ] 3.3 正脸视频确认 YuNet 直接检出
- [ ] 3.4 无脸视频确认不报错
- [x] 3.5 PyInstaller 打包验证