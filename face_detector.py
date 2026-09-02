"""
人脸检测与高斯模糊模块。

使用 YuNet + Caffe SSD 双模型检测视频帧中的人脸，并应用高斯模糊。
YuNet 为主检测器（侧脸/仰角强），Caffe SSD 为回退。

模型路径：
  - PyInstaller 打包模式：从 sys._MEIPASS/models/ 读取
  - 开发模式：从 ~/.video_anonymizer/ 读取，回退到项目 models/
"""

import sys
import cv2
import numpy as np
from pathlib import Path
import threading

# ---- 模型路径 ----

def _get_model_dir() -> Path:
    """获取模型文件目录，兼容打包和开发模式。"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "models"
    else:
        return Path.home() / ".video_anonymizer"

MODEL_DIR = _get_model_dir()
_PROJECT_MODELS = Path(__file__).resolve().parent / "models"

# Caffe SSD
PROTOTXT_PATH = MODEL_DIR / "deploy.prototxt"
CAFFEMODEL_PATH = MODEL_DIR / "res10_300x300_ssd_iter_140000_fp16.caffemodel"

# YuNet
YUNET_PATH = MODEL_DIR / "face_detection_yunet_2023mar.onnx"
_PROJECT_YUNET = _PROJECT_MODELS / "face_detection_yunet_2023mar.onnx"

# ---- 线程局部模型 ----

_local = threading.local()


def _get_net():
    """获取线程局部的 Caffe DNN 网络实例。"""
    net = getattr(_local, 'net', None)
    if net is not None:
        return net

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

    _local.net = cv2.dnn.readNetFromCaffe(str(PROTOTXT_PATH), str(CAFFEMODEL_PATH))
    return _local.net


def _get_yunet_detector():
    """获取线程局部的 YuNet 检测器实例。"""
    detector = getattr(_local, 'yunet', None)
    if detector is not None:
        return detector

    model_path = YUNET_PATH if YUNET_PATH.exists() else _PROJECT_YUNET
    if not model_path.exists():
        raise FileNotFoundError(
            f"YuNet 模型文件未找到: {YUNET_PATH}\n"
            "请确保模型文件已放置在正确位置。"
        )

    _local.yunet = cv2.FaceDetectorYN.create(
        str(model_path), "", (320, 320), 0.5, 0.5, 5000
    )
    return _local.yunet


# ---- 人脸检测 ----

def _detect_yunet(
    frame: np.ndarray, confidence_threshold: float
) -> list[tuple[int, int, int, int, float]]:
    """使用 YuNet 检测人脸，返回与 Caffe 一致的格式。"""
    detector = _get_yunet_detector()
    h, w = frame.shape[:2]
    detector.setInputSize((w, h))
    detector.setScoreThreshold(confidence_threshold)
    _, results = detector.detect(frame)

    faces: list[tuple[int, int, int, int, float]] = []
    if results is None:
        return faces

    # YuNet 输出格式: [x, y, w, h, ...landmarks, confidence]
    for det in results:
        x, y, fw, fh = int(det[0]), int(det[1]), int(det[2]), int(det[3])
        conf = float(det[14])
        faces.append((x, y, fw, fh, conf))

    return faces


def _detect_caffe(
    frame: np.ndarray, confidence_threshold: float
) -> list[tuple[int, int, int, int, float]]:
    """使用 Caffe SSD 检测人脸。"""
    net = _get_net()
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    faces: list[tuple[int, int, int, int, float]] = []
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < confidence_threshold:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x1, y1, x2, y2 = box.astype("int")
        faces.append((x1, y1, x2 - x1, y2 - y1, confidence))

    return faces


def detect_faces(
    frame: np.ndarray, confidence_threshold: float = 0.5
) -> list[tuple[int, int, int, int, float]]:
    """
    检测图像帧中的人脸。

    YuNet 优先（侧脸/仰角强），未检出时回退 Caffe SSD。

    Args:
        frame: BGR 图像 (numpy array)
        confidence_threshold: 置信度阈值 (0.0 ~ 1.0)

    Returns:
        [(x, y, w, h, confidence), ...] 人脸边界框列表
    """
    faces = _detect_yunet(frame, confidence_threshold)
    if not faces:
        faces = _detect_caffe(frame, confidence_threshold)
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
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w, x + fw)
        y2 = min(h, y + fh)

        if x2 <= x1 or y2 <= y1:
            continue

        pad = kernel_size // 2
        y1_pad = max(0, y1 - pad)
        y2_pad = min(h, y2 + pad)
        x1_pad = max(0, x1 - pad)
        x2_pad = min(w, x2 + pad)

        roi_expanded = result[y1_pad:y2_pad, x1_pad:x2_pad]
        blurred = cv2.GaussianBlur(roi_expanded, (kernel_size, kernel_size), 0)
        result[y1_pad:y2_pad, x1_pad:x2_pad] = blurred

    return result