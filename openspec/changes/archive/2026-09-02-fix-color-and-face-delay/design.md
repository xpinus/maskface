## Context

当前处理管线：MoviePy `iter_frames` → RGB → `cv2.cvtColor(RGB2BGR)` → FaceTracker 跳帧检测 → 模糊 → `cv2.cvtColor(BGR2RGB)` → `cv2.VideoWriter` 写入。`cv2.VideoWriter` 的 `mp4v` 编码器期望 BGR 输入，但代码写入了 RGB。FaceTracker 每 5 帧检测一次，新人脸出现时存在盲区。

## Goals / Non-Goals

**Goals:**
- 修复输出视频颜色与原视频一致
- 新人脸出现的第一帧即被检测并模糊
- 简化代码，删除不再需要的 FaceTracker 类

**Non-Goals:**
- 不改变检测模型或模糊算法
- 不引入新的性能优化策略

## Decisions

1. **去掉 FaceTracker，逐帧检测**：SSD 模型单帧检测耗时约 10-20ms（CPU），对 30fps 视频处理时间增加约 10-30%，但正确性优先于性能。逐帧检测消除了跳帧盲区和插值匹配错误。

2. **直接写入 BGR 帧**：`cv2.VideoWriter` 期望 BGR 格式，去除 `COLOR_BGR2RGB` 转换，`out.write(frame_bgr)` 即可。

## Risks / Trade-offs

- [Risk] 逐帧检测增加处理耗时 → 对典型视频（1-3 分钟），增加时间在秒级，用户可接受
- [Risk] 人脸检测置信度阈值过低时可能产生更多误检 → 默认阈值 0.5 已保守，用户可调