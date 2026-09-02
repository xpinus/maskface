## Context

当前串行管线：`加载视频 → 处理音频 → 逐帧检测+模糊 → 合成`。音频和视频互不依赖，视频帧间也独立，浪费多核 CPU。

## Goals / Non-Goals

**Goals:**
- 音频与视频帧处理并行运行
- 视频帧批量多线程处理，利用多核加速
- 取消操作线程安全

**Non-Goals:**
- 不改变输出结果（功能行为不变，仅速度提升）
- 不引入 GPU 加速

## Decisions

1. **音频线程 + 视频主线程并行**：音频处理独立线程，视频帧处理立即开始，不等待音频。两者完成后合并。

2. **批处理 + ThreadPoolExecutor**：每 30 帧一批提交到线程池，`os.cpu_count()` 个工作线程。收集结果后按帧序号排序写入 `VideoWriter`。

3. **线程局部 DNN 网络**：`face_detector.py` 用 `threading.local()` 为每个线程创建独立 `_net` 实例，避免锁竞争。

4. **`threading.Event` 取消**：替换 `bool` 标志，线程安全。工作线程和批循环均检查 `event.is_set()`。

## Risks / Trade-offs

- [Risk] 批处理增加内存占用（30 帧 × 1080p ≈ 180MB）→ 批大小可调，内存占用可控
- [Risk] 线程池创建/销毁开销 → 复用单个 executor 处理所有批次
- [Risk] 音频线程异常 → catch 并降级为无音频输出，不影响视频处理