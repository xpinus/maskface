## Why

当前处理管线完全串行：音频处理完成后才开始视频帧处理，每帧顺序检测人脸。音频和视频互不依赖，视频帧之间也可独立处理，串行方式浪费了多核 CPU 资源。

## What Changes

- 音频处理与视频帧处理并行运行（两个独立线程）
- 视频帧批量提交到线程池，多线程并行检测人脸与模糊
- `face_detector.py` 全局 DNN 网络改为线程局部存储，每线程独立实例
- 取消机制从 `bool` 标志改为 `threading.Event`，线程安全

## Capabilities

此变更不改变系统行为——输出结果与串行版本一致，仅处理速度提升。纯性能优化，无 spec 变更。

## Impact

- `face_detector.py`: 全局 `_net` → `threading.local()` 线程局部
- `app.py`: 处理管线重构，引入 `ThreadPoolExecutor`、`threading.Event`、批处理