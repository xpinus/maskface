"""
MaskFace — 视频匿名化工具 Tkinter 桌面界面。

提供原生桌面窗口：文件选择、参数滑块、进度条、一键处理、保存结果。
"""

import os
import sys

import tempfile
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading

FONT = ("Microsoft YaHei UI", 10)
FONT_BOLD = ("Microsoft YaHei UI", 10, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 14, "bold")
FONT_BTN = ("Microsoft YaHei UI", 13, "bold")

if getattr(sys, 'frozen', False):
    LOGO_PATH = os.path.join(os.path.dirname(sys.executable), '面具2.png')
else:
    LOGO_PATH = r'C:\Users\pinus\Downloads\面具2.png'


class RoundedButton(tk.Canvas):
    """带圆角的按钮，用 Canvas 实现。"""

    def __init__(self, parent, text, command, bg="#4CAF50", disabled_bg="#bdbdbd",
                 width=140, height=44, radius=8, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=parent["bg"], **kwargs)
        self._command = command
        self._bg = bg
        self._disabled_bg = disabled_bg
        self._text = text
        self._w = width
        self._h = height
        self._r = radius
        self._enabled = True
        self._hover = False

        self.after(10, self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self):
        self.delete("all")
        color = self._bg if self._enabled else self._disabled_bg
        if self._enabled and self._hover:
            color = self._darken(color)
        self.create_rounded_rect(0, 0, self._w, self._h, self._r, fill=color, outline=color)
        self.create_text(self._w // 2, self._h // 2, text=self._text,
                         fill="white", font=FONT_BTN)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1 + r, y1, x1 + r, y1,
                  x2 - r, y1, x2 - r, y1,
                  x2, y1, x2, y1 + r,
                  x2, y1 + r, x2, y2 - r,
                  x2, y2 - r, x2, y2,
                  x2 - r, y2, x2 - r, y2,
                  x1 + r, y2, x1 + r, y2,
                  x1, y2, x1, y2 - r,
                  x1, y2 - r, x1, y1 + r,
                  x1, y1 + r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _darken(self, hex_color):
        c = hex_color.lstrip("#")
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_click(self, event):
        if self._enabled and self._command:
            self._command()

    def _on_enter(self, event):
        self._hover = True
        if self._enabled:
            self._draw()

    def _on_leave(self, event):
        self._hover = False
        if self._enabled:
            self._draw()

    def set_text(self, text):
        self._text = text
        self._draw()

    def set_bg(self, bg):
        self._bg = bg
        self._draw()

    def set_enabled(self, enabled):
        self._enabled = enabled
        self["cursor"] = "hand2" if enabled else ""
        self._draw()

    def disable(self):
        self.set_enabled(False)

    def enable(self):
        self.set_enabled(True)


class MaskFaceApp:
    """MaskFace Tkinter 主窗口。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MaskFace - 视频匿名化工具")
        self.root.geometry("620x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")

        self._set_icon()

        self.video_path: str | None = None
        self.output_path: str | None = None
        self._processing = False
        self._cancelled = False

        self._build_ui()

    def _set_icon(self):
        try:
            from PIL import Image, ImageTk
            img = Image.open(LOGO_PATH)
            img = img.resize((48, 48), Image.LANCZOS)
            self._icon = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, self._icon)
        except Exception:
            pass

    def _build_ui(self):
        px, py = 20, 5
        bg = "#f5f5f5"

        # 标题
        title = tk.Label(self.root, text="MaskFace - 视频匿名化工具",
                         font=FONT_TITLE, bg=bg)
        title.pack(pady=(15, 10))

        # --- 文件选择 ---
        file_frame = tk.LabelFrame(self.root, text="视频文件", font=FONT_BOLD,
                                   bg=bg, fg="#333", padx=10, pady=10)
        file_frame.pack(fill="x", padx=px, pady=py)

        self.file_label = tk.Label(
            file_frame, text="未选择文件", fg="gray", font=FONT,
            bg=bg, anchor="w"
        )
        self.file_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.select_btn = tk.Button(
            file_frame, text="选择视频", command=self._select_video,
            font=FONT, padx=12, pady=3, cursor="hand2",
            bg="#e0e0e0", fg="#333", activebackground="#d0d0d0",
            relief="flat", borderwidth=0,
        )
        self.select_btn.pack(side="right")

        # --- 参数 ---
        self.param_frame = tk.LabelFrame(self.root, text="参数设置", font=FONT_BOLD,
                                         bg=bg, fg="#333", padx=10, pady=10)
        self.param_frame.pack(fill="x", padx=px, pady=py)

        tk.Label(self.param_frame, text="模糊强度（越大越模糊）",
                 font=FONT, bg=bg, fg="#555").grid(row=0, column=0, sticky="w", pady=2)
        self.blur_var = tk.IntVar(value=55)
        self.blur_scale = ttk.Scale(
            self.param_frame, from_=1, to=99, variable=self.blur_var,
            command=lambda v: self._on_blur_change(v)
        )
        self.blur_scale.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.blur_label = tk.Label(self.param_frame, text="55", font=FONT_BOLD,
                                   bg=bg, width=4)
        self.blur_label.grid(row=1, column=1, padx=(10, 0))

        tk.Label(self.param_frame, text="变声程度（半音，负值低沉/正值尖锐）",
                 font=FONT, bg=bg, fg="#555").grid(row=2, column=0, sticky="w", pady=2)
        self.pitch_var = tk.IntVar(value=-5)
        self.pitch_scale = ttk.Scale(
            self.param_frame, from_=-12, to=12, variable=self.pitch_var,
            command=lambda v: self._on_pitch_change(v)
        )
        self.pitch_scale.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        self.pitch_label = tk.Label(self.param_frame, text="-5", font=FONT_BOLD,
                                    bg=bg, width=4)
        self.pitch_label.grid(row=3, column=1, padx=(10, 0))

        tk.Label(self.param_frame, text="检测精度（越高越严格）",
                 font=FONT, bg=bg, fg="#555").grid(row=4, column=0, sticky="w", pady=2)
        self.conf_var = tk.DoubleVar(value=0.5)
        self.conf_scale = ttk.Scale(
            self.param_frame, from_=0.1, to=1.0, variable=self.conf_var,
            command=lambda v: self._on_conf_change(v)
        )
        self.conf_scale.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        self.conf_label = tk.Label(self.param_frame, text="0.5", font=FONT_BOLD,
                                   bg=bg, width=4)
        self.conf_label.grid(row=5, column=1, padx=(10, 0))

        self.param_frame.columnconfigure(0, weight=1)

        # --- 进度 ---
        progress_frame = tk.LabelFrame(self.root, text="处理进度", font=FONT_BOLD,
                                       bg=bg, fg="#333", padx=10, pady=10)
        progress_frame.pack(fill="x", padx=px, pady=py)

        self.progress_bar = ttk.Progressbar(
            progress_frame, mode="determinate", length=400
        )
        self.progress_bar.pack(fill="x")

        self.status_label = tk.Label(
            progress_frame, text="就绪，等待开始...", fg="gray",
            font=FONT, bg=bg, anchor="w"
        )
        self.status_label.pack(fill="x", pady=(5, 0))

        # --- 按钮区 ---
        btn_frame = tk.Frame(self.root, bg=bg)
        btn_frame.pack(fill="x", padx=px, pady=(12, 15))

        self.action_btn = RoundedButton(
            btn_frame, text="开始处理", command=self._on_action,
            bg="#4CAF50", disabled_bg="#bdbdbd",
            width=150, height=44, radius=8,
        )
        self.action_btn.pack()

    # ---- 按钮状态机 ----

    def _on_action(self):
        if self._processing:
            # 取消
            self._cancelled = True
            self._update_status("正在取消...", 0)
        elif self.output_path:
            # 保存结果
            self._save_result()
        else:
            # 开始处理
            self._start_process()

    # ---- 滑块 ----

    def _on_blur_change(self, value):
        v = int(float(value))
        if v % 2 == 0:
            v += 1
        self.blur_label.config(text=str(v))

    def _on_pitch_change(self, value):
        self.pitch_label.config(text=str(int(float(value))))

    def _on_conf_change(self, value):
        self.conf_label.config(text=f"{float(value):.2f}")

    # ---- 文件选择 ----

    def _select_video(self):
        if self._processing:
            return
        path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")],
        )
        if path:
            self.video_path = path
            self.file_label.config(text=Path(path).name, fg="black")
            self.status_label.config(text="视频已就绪，点击开始处理")
            self.output_path = None
            self._set_action_state("ready")

    # ---- 状态切换 ----

    def _set_action_state(self, state):
        """state: 'ready' | 'processing' | 'done'"""
        if state == "ready":
            self.action_btn.set_text("开始处理")
            self.action_btn.set_bg("#4CAF50")
            self.action_btn.enable()
            self._set_params_enabled(True)
            self.select_btn.config(state="normal")
        elif state == "processing":
            self.action_btn.set_text("取消")
            self.action_btn.set_bg("#f44336")
            self.action_btn.enable()
            self._set_params_enabled(False)
            self.select_btn.config(state="disabled")
        elif state == "done":
            self.action_btn.set_text("保存结果")
            self.action_btn.set_bg("#2196F3")
            self.action_btn.enable()
            self._set_params_enabled(False)
            self.select_btn.config(state="disabled")

    def _set_params_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for child in self.param_frame.winfo_children():
            try:
                child.config(state=state)
            except tk.TclError:
                pass

    # ---- 处理 ----

    def _start_process(self):
        if not self.video_path:
            messagebox.showwarning("提示", "请先选择视频文件")
            return

        self._processing = True
        self._cancelled = False
        self.output_path = None
        self._set_action_state("processing")

        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        self._update_status("正在加载处理引擎...", 0)

        import cv2
        import numpy as np
        from moviepy import VideoFileClip
        from face_detector import FaceTracker, apply_blur
        from voice_changer import process_audio

        blur_kernel = self.blur_var.get()
        if blur_kernel % 2 == 0:
            blur_kernel += 1
        pitch_steps = self.pitch_var.get()
        confidence = self.conf_var.get()

        try:
            self._update_status("正在加载视频...", 2)
            clip = VideoFileClip(self.video_path)
            total_frames = int(clip.fps * clip.duration) if clip.duration else 0
            fps = clip.fps or 30
            w, h = clip.size

            self._update_status("正在处理音频...", 5)
            new_audio = None
            if clip.audio is not None:
                try:
                    new_audio = process_audio(clip, pitch_steps)
                except Exception as e:
                    print(f"音频处理警告: {e}")

            tracker = FaceTracker(skip_interval=5, confidence_threshold=confidence)

            temp_dir = Path(tempfile.gettempdir()) / "maskface"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_video = temp_dir / f"temp_video_{int(time.time())}.mp4"

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(temp_video), fourcc, fps, (w, h))

            frame_count = 0
            for frame in clip.iter_frames(fps=fps, dtype="uint8"):
                if self._cancelled:
                    break

                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                faces = tracker.process_frame(frame_bgr)
                if faces:
                    frame_bgr = apply_blur(frame_bgr, faces, blur_kernel)

                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                out.write(frame_rgb)

                frame_count += 1
                if total_frames > 0:
                    pct = 5 + 85 * (frame_count / total_frames)
                    self._update_status(f"处理视频帧 {frame_count}/{total_frames}", int(pct))

            out.release()

            if self._cancelled:
                try:
                    os.remove(str(temp_video))
                except OSError:
                    pass
                clip.close()
                self._update_status("已取消", 0)
                self.root.after(0, lambda: self._set_action_state("ready"))
                self._processing = False
                return

            self._update_status("正在合成最终视频...", 92)

            processed_clip = VideoFileClip(str(temp_video))
            if new_audio is not None:
                processed_clip = processed_clip.with_audio(new_audio)

            output_path = temp_dir / f"maskface_output_{int(time.time())}.mp4"
            processed_clip.write_videofile(
                str(output_path), codec="libx264", audio_codec="aac", logger=None
            )
            processed_clip.close()
            clip.close()

            try:
                os.remove(str(temp_video))
            except OSError:
                pass

            self.output_path = str(output_path)
            self._update_status("处理完成！点击保存结果", 100)
            self.root.after(0, lambda: self._set_action_state("done"))

        except Exception as e:
            self._update_status(f"处理失败: {e}", 0)
            messagebox.showerror("错误", f"处理失败:\n{e}")
            self.root.after(0, lambda: self._set_action_state("ready"))

        finally:
            self._processing = False

    def _update_status(self, text: str, pct: int):
        self.root.after(0, lambda: self._set_ui(text, pct))

    def _set_ui(self, text: str, pct: int):
        self.status_label.config(text=text)
        self.progress_bar["value"] = pct

    def _save_result(self):
        if not self.output_path:
            return
        dest = filedialog.asksaveasfilename(
            title="保存处理结果",
            defaultextension=".mp4",
            filetypes=[("MP4 视频", "*.mp4")],
            initialfile="maskface_output.mp4",
        )
        if dest:
            import shutil
            shutil.copy2(self.output_path, dest)
            self.status_label.config(text=f"已保存: {Path(dest).name}")
            messagebox.showinfo("完成", f"视频已保存到:\n{dest}")


def main():
    root = tk.Tk()
    app = MaskFaceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()



