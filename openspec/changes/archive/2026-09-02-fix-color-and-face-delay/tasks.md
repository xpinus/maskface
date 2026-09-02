## 1. face_detector.py — 删除 FaceTracker

- [x] 1.1 删除 `FaceTracker` 类（约 40 行），保留 `detect_faces()` 和 `apply_blur()` 函数
- [x] 1.2 验证 `detect_faces()` 和 `apply_blur()` 接口无变化，可直接逐帧调用

## 2. app.py — 修复颜色与检测

- [x] 2.1 导入改为 `from face_detector import detect_faces, apply_blur`
- [x] 2.2 删除 `tracker = FaceTracker(...)` 初始化
- [x] 2.3 将 `faces = tracker.process_frame(frame_bgr)` 改为 `faces = detect_faces(frame_bgr, confidence)`
- [x] 2.4 删除 `frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)` 和 `out.write(frame_rgb)`，改为 `out.write(frame_bgr)`

## 3. 验证

- [x] 3.1 本地运行 `uv run python app.py`，处理含人脸视频，对比输出颜色与原视频一致
- [x] 3.2 观察人脸出现首帧是否有马赛克（应无延迟）
- [x] 3.3 调节检测精度滑块，确认不同阈值生效
- [x] 3.4 PyInstaller 打包并运行 exe 验证