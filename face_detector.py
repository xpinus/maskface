"""
人脸检测与高斯模糊模块。

使用 OpenCV DNN SSD 模型检测视频帧中的人脸，并应用高斯模糊。
支持跳帧检测 + 线性插值以优化性能。

模型路径：
  - PyInstaller 打包模式：从 sys._MEIPASS/models/ 读取
  - 开发模式：从 ~/.video_anonymizer/ 读取
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# ---- 模型路径 ----

def _get_model_dir() -> Path:
    """获取模型文件目录，兼容打包和开发模式。"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包模式
        return Path(sys._MEIPASS) / "models"
    else:
        # 开发模式
        return Path.home() / ".video_anonymizer"

MODEL_DIR = _get_model_dir()

PROTOTXT_PATH = MODEL_DIR / "deploy.prototxt"
CAFFEMODEL_PATH = MODEL_DIR / "res10_300x300_ssd_iter_140000_fp16.caffemodel"

_net = None


def _ensure_model() -> None:
    """加载模型文件。不存在时给出清晰错误提示。"""
    global _net
    if _net is not None:
        return

    if not PROTOTXT_PATH.exists():
        raise FileNotFoundError(
            f"模型文件未找到: {PROTOTXT_PATH}\n"
            "请确保模型文件已放置在正确位置。"
        )
    if not CAFFEMODEL_PATH.exists():
        raise FileNotFoundError(
            f"模型文件未找到: {CAFFEMODEL_PATH}\n"
            "请确保模型文件已放置在正确位置。"
        )

    _net = cv2.dnn.readNetFromCaffe(str(PROTOTXT_PATH), str(CAFFEMODEL_PATH))


# ---- 人脸检测 ----

def detect_faces(
    frame: np.ndarray, confidence_threshold: float = 0.5
) -> list[tuple[int, int, int, int, float]]:
    """
    检测图像帧中的人脸。

    Args:
        frame: BGR 图像 (numpy array)
        confidence_threshold: 置信度阈值 (0.0 ~ 1.0)

    Returns:
        [(x, y, w, h, confidence), ...] 人脸边界框列表
    """
    _ensure_model()

    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    _net.setInput(blob)
    detections = _net.forward()

    faces: list[tuple[int, int, int, int, float]] = []
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < confidence_threshold:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x1, y1, x2, y2 = box.astype("int")
        faces.append((x1, y1, x2 - x1, y2 - y1, confidence))

    return faces


# ---- 高斯模糊 ----

def apply_blur(
    frame: np.ndarray, faces: list[tuple[int, int, int, int, float]], kernel_size: int
) -> np.ndarray:
    """
    对帧中的人脸区域应用高斯模糊。

    Args:
        frame: BGR 图像
        faces: 人脸边界框列表 [(x, y, w, h, confidence), ...]
        kernel_size: 高斯模糊核大小（自动调整为奇数）

    Returns:
        处理后的图像
    """
    if kernel_size % 2 == 0:
        kernel_size += 1

    result = frame.copy()
    h, w = frame.shape[:2]

    for (x, y, fw, fh, _) in faces:
        # 边界裁剪
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w, x + fw)
        y2 = min(h, y + fh)

        if x2 <= x1 or y2 <= y1:
            continue

        # 扩张区域以包含更多周围像素，使模糊更自然
        pad = kernel_size // 2
        y1_pad = max(0, y1 - pad)
        y2_pad = min(h, y2 + pad)
        x1_pad = max(0, x1 - pad)
        x2_pad = min(w, x2 + pad)

        roi_expanded = result[y1_pad:y2_pad, x1_pad:x2_pad]
        blurred = cv2.GaussianBlur(roi_expanded, (kernel_size, kernel_size), 0)
        result[y1_pad:y2_pad, x1_pad:x2_pad] = blurred

    return result


# ---- 跳帧 + 线性插值 ----

class FaceTracker:
    """跳帧检测 + 线性插值的人脸跟踪器。"""

    def __init__(self, skip_interval: int = 5, confidence_threshold: float = 0.5):
        self.skip_interval = skip_interval
        self.confidence_threshold = confidence_threshold
        self._last_faces: list[tuple[int, int, int, int, float]] = []
        self._next_faces: list[tuple[int, int, int, int, float]] = []
        self._frame_since_detect = skip_interval  # 触发首次检测

    def process_frame(self, frame: np.ndarray) -> list[tuple[int, int, int, int, float]]:
        """
        处理一帧，返回插值后的人脸位置。

        每 skip_interval 帧执行一次完整检测，
        中间帧使用线性插值。
        """
        if self._frame_since_detect >= self.skip_interval:
            self._last_faces = self._next_faces
            self._next_faces = detect_faces(frame, self.confidence_threshold)
            self._frame_since_detect = 0
            return self._next_faces

        self._frame_since_detect += 1

        # 线性插值
        if not self._last_faces or not self._next_faces:
            return self._next_faces or self._last_faces

        t = self._frame_since_detect / self.skip_interval
        interpolated: list[tuple[int, int, int, int, float]] = []

        # 按最近邻匹配两个人脸列表
        for lf in self._last_faces:
            best = min(
                self._next_faces,
                key=lambda nf: (lf[0] - nf[0]) ** 2 + (lf[1] - nf[1]) ** 2,
            )
            x = int(lf[0] + (best[0] - lf[0]) * t)
            y = int(lf[1] + (best[1] - lf[1]) * t)
            w = int(lf[2] + (best[2] - lf[2]) * t)
            h = int(lf[3] + (best[3] - lf[3]) * t)
            interpolated.append((x, y, w, h, best[4]))

        return interpolated