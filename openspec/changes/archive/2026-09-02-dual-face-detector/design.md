## Context

当前单一 Caffe SSD 模型对侧脸/仰角检测弱。YuNet 内置于 OpenCV 4.14，对多角度人脸更鲁棒。

## Goals / Non-Goals

**Goals:**
- 提升侧脸和仰头大笑场景的检测率
- 保持 `detect_faces()` 接口不变，app.py 零改动
- 两个模型共用线程局部存储，不增加额外内存竞争

**Non-Goals:**
- 不改变模糊算法或输出格式
- 不引入额外 Python 依赖

## Decisions

1. **YuNet 优先 + Caffe 回退**：YuNet 多角度强，Caffe 作为兜底。不需要用户感知双模型。

2. **YuNet 输入尺寸 320×320**：原图 resize 后送入，平衡速度与精度。原 SSD 为 300×300。

3. **共用阈值**：两个模型共用 `confidence_threshold`，用户滑块同时控制。

4. **线程局部存储**：YuNet 和 Caffe 各自独立 `threading.local()`，互不干扰。

## Risks / Trade-offs

- [Risk] YuNet 模型文件需下载 → 实现时自动下载，打包时内嵌
- [Risk] 双模型增加 ~2MB 内存 → 可接受