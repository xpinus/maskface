## 1. face_detector.py — 线程局部 DNN

- [x] 1.1 引入 `threading`，创建 `_local = threading.local()`
- [x] 1.2 新增 `_get_net()` 函数：首次访问时创建线程局部 `_net`，后续复用
- [x] 1.3 `detect_faces()` 改为调用 `_get_net()` 替代 `_ensure_model()`

## 2. app.py — 并行处理管线

- [x] 2.1 引入 `concurrent.futures.ThreadPoolExecutor`、`os`、`threading`
- [x] 2.2 `self._cancelled` 改为 `self._cancel_event = threading.Event()`
- [x] 2.3 新增 `_process_one_frame(frame_bgr, confidence, blur_kernel)` 纯函数
- [x] 2.4 新增 `_process_batch(batch, out, ...)` 批处理函数
- [x] 2.5 重构 `_process()`：音频线程 + 视频批处理并行，`Event` 取消
- [x] 2.6 进度报告适配批处理模式

## 3. 验证

- [ ] 3.1 本地处理含音频视频，确认音视频同步、输出正确
- [ ] 3.2 处理无音频视频，确认不报错
- [ ] 3.3 点击取消，确认所有线程及时停止
- [x] 3.4 PyInstaller 打包并运行 exe 验证