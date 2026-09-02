"""
音频变声模块。

从视频中提取音频，通过音调变换（pitch shift）改变声音特征，
然后将处理后的音频写回。
"""

import numpy as np
import librosa
from moviepy import AudioClip, VideoFileClip


def extract_audio(clip: VideoFileClip) -> tuple[np.ndarray, int] | None:
    """
    从视频中提取音频数据。

    Args:
        clip: moviepy VideoFileClip 对象

    Returns:
        (audio_samples, sample_rate) 或 None（无音轨时）
    """
    if clip.audio is None:
        return None

    audio = clip.audio
    fps = audio.fps or 44100

    # 读取音频数据
    # moviepy 的 to_soundarray 返回 (channels, samples) 的 float32 数组
    audio_array = audio.to_soundarray()  # shape: (n_samples, n_channels)
    # 转为单声道
    if audio_array.ndim == 2 and audio_array.shape[1] > 1:
        audio_array = audio_array.mean(axis=1)
    elif audio_array.ndim == 2:
        audio_array = audio_array[:, 0]

    return audio_array.astype(np.float32), fps


def pitch_shift_audio(
    audio_data: np.ndarray, sample_rate: int, n_steps: float
) -> np.ndarray:
    """
    对音频应用音调变换。

    Args:
        audio_data: 音频采样数据 (float32)
        sample_rate: 采样率
        n_steps: 半音偏移量，负值降低音调，正值提高音调

    Returns:
        变调后的音频数据
    """
    if n_steps == 0:
        return audio_data

    return librosa.effects.pitch_shift(
        y=audio_data, sr=sample_rate, n_steps=n_steps
    )


def make_audio_clip(
    audio_data: np.ndarray, sample_rate: int
) -> AudioClip:
    """
    将 numpy 音频数据封装为 moviepy AudioClip。

    Args:
        audio_data: 音频采样数据 (float32), 1D 单声道
        sample_rate: 采样率

    Returns:
        moviepy AudioClip 对象
    """
    n_samples = len(audio_data)

    def make_frame(t):
        if isinstance(t, np.ndarray):
            # MoviePy 批量请求时 t 是数组
            idx = (t * sample_rate).astype(int)
            idx = np.clip(idx, 0, n_samples - 1)
            return audio_data[idx].reshape(1, -1)
        else:
            i = int(t * sample_rate)
            if i < n_samples:
                return np.array([float(audio_data[i])])
            return np.array([0.0])

    return AudioClip(make_frame, duration=n_samples / sample_rate, fps=sample_rate)


def process_audio(clip: VideoFileClip, n_steps: float) -> AudioClip | None:
    """
    完整音频处理流程：提取 → 变调 → 封装。

    Args:
        clip: 输入视频
        n_steps: 半音偏移量

    Returns:
        处理后的 AudioClip，或 None（无音轨时）
    """
    extracted = extract_audio(clip)
    if extracted is None:
        return None

    audio_data, sr = extracted
    shifted = pitch_shift_audio(audio_data, sr, n_steps)
    return make_audio_clip(shifted, sr)