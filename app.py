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
from concurrent.futures import ThreadPoolExecutor, as_completed

import sv_ttk

FONT = ("Microsoft YaHei UI", 10)
FONT_BOLD = ("Microsoft YaHei UI", 10, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 14, "bold")
FONT_BTN = ("Microsoft YaHei UI", 13, "bold")

BATCH_SIZE = 30



class MaskFaceApp:
    """MaskFace Tkinter 主窗口。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MaskFace - 视频匿名化工具")
        self.root.geometry("620x520")
        self.root.resizable(False, False)

        sv_ttk.set_theme("light")
        self._setup_button_styles()
        self._set_icon()

        self.video_path: str | None = None
        self.output_path: str | None = None
        self._processing = False
        self._cancel_event = threading.Event()

        self._build_ui()

    def _setup_button_styles(self):
        style = ttk.Style()
        style.configure("Start.TButton", font=FONT_BTN, padding=(30, 10))
        style.configure("Cancel.TButton", font=FONT_BTN, padding=(30, 10))
        style.configure("Save.TButton", font=FONT_BTN, padding=(30, 10))
        style.configure("Select.TButton", font=FONT, padding=(12, 3))

    def _set_icon(self):
        try:
            if getattr(sys, "frozen", False):
                self.root.iconbitmap(sys.executable)
            else:
                self.root.iconbitmap("maskface.ico")
        except Exception:
            pass

    def _build_ui(self):
        px, py = 20, 5

        ttk.Label(self.root, text="MaskFace - 视频匿名化工具",
                  font=FONT_TITLE).pack(pady=(15, 10))

        # --- 文件选择 ---
        file_frame = ttk.LabelFrame(self.root, text="视频文件", padding=10)
        file_frame.pack(fill="x", padx=px, pady=py)

        self.file_label = ttk.Label(file_frame, text="未选择文件", foreground="gray")
        self.file_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.select_btn = ttk.Button(
            file_frame, text="选择视频", command=self._select_video,
            style="Select.TButton"
        )
        self.select_btn.pack(side="right")

        # --- 参数 ---
        self.param_frame = ttk.LabelFrame(self.root, text="参数设置", padding=10)
        self.param_frame.pack(fill="x", padx=px, pady=py)

        ttk.Label(self.param_frame, text="模糊强度（越大越模糊）").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.blur_var = tk.IntVar(value=55)
        self.blur_scale = ttk.Scale(
            self.param_frame, from_=1, to=99, variable=self.blur_var,
            command=lambda v: self._on_blur_change(v)
        )
        self.blur_scale.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.blur_label = ttk.Label(self.param_frame, text="55", font=FONT_BOLD, width=4)
        self.blur_label.grid(row=1, column=1, padx=(10, 0))

        ttk.Label(self.param_frame, text="变声程度（半音，负值低沉/正值尖锐）").grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.pitch_var = tk.IntVar(value=-5)
        self.pitch_scale = ttk.Scale(
            self.param_frame, from_=-12, to=12, variable=self.pitch_var,
            command=lambda v: self._on_pitch_change(v)
        )
        self.pitch_scale.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        self.pitch_label = ttk.Label(self.param_frame, text="-5", font=FONT_BOLD, width=4)
        self.pitch_label.grid(row=3, column=1, padx=(10, 0))

        ttk.Label(self.param_frame, text="检测精度（越高越严格）").grid(
            row=4, column=0, sticky="w", pady=2
        )
        self.conf_var = tk.DoubleVar(value=0.5)
        self.conf_scale = ttk.Scale(
            self.param_frame, from_=0.1, to=1.0, variable=self.conf_var,
            command=lambda v: self._on_conf_change(v)
        )
        self.conf_scale.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        self.conf_label = ttk.Label(self.param_frame, text="0.5", font=FONT_BOLD, width=4)
        self.conf_label.grid(row=5, column=1, padx=(10, 0))

        self.param_frame.columnconfigure(0, weight=1)

        # --- 进度 ---
        progress_frame = ttk.LabelFrame(self.root, text="处理进度", padding=10)
        progress_frame.pack(fill="x", padx=px, pady=py)

        self._pb_canvas = tk.Canvas(
            progress_frame, height=22,
            bg="#fafafa", highlightthickness=0, bd=0
        )
        self._pb_canvas.pack(fill="x", pady=6)
        self._pb_trough = self._pb_canvas.create_rectangle(
            0, 0, 0, 22, fill="#e0e0e0", outline="#d0d0d0", width=1
        )
        self._pb_bar = self._pb_canvas.create_rectangle(
            0, 0, 0, 22, fill="#196ebf", outline="", width=0
        )
        

        self.status_label = ttk.Label(
            progress_frame, text="就绪，等待开始...", foreground="gray"
        )
        self.status_label.pack(pady=(5, 0))

        # --- 按钮区 ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=px, pady=(12, 15))

        self.action_btn = ttk.Button(
            btn_frame, text="开始处理", command=self._on_action,
            style="Start.TButton"
        )
        self.action_btn.pack()

    # ---- 按钮状态机 ----

    def _on_action(self):
        if self._processing:
            self._cancel_event.set()
            self._update_status("正在取消...", 0)
        elif self.output_path:
            self._save_result()
        else:
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
            self.file_label.config(text=Path(path).name, foreground="black")
            self.status_label.config(text="视频已就绪，点击开始处理")
            self.output_path = None
            self._set_action_state("ready")

    # ---- 状态切换 ----

    def _set_action_state(self, state):
        """state: 'ready' | 'processing' | 'done'"""
        if state == "ready":
            self.action_btn.config(text="开始处理", style="Start.TButton")
            self._set_params_enabled(True)
            self.select_btn.config(state="normal")
        elif state == "processing":
            self.action_btn.config(text="取消", style="Cancel.TButton")
            self._set_params_enabled(False)
            self.select_btn.config(state="disabled")
        elif state == "done":
            self.action_btn.config(text="保存结果", style="Save.TButton")
            self._set_params_enabled(True)
            self.select_btn.config(state="normal")

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
        self._cancel_event.clear()
        self.output_path = None
        self._set_action_state("processing")

        threading.Thread(target=self._process, daemon=True).start()

    @staticmethod
    def _process_one_frame(frame_bgr, confidence, blur_kernel):
        """处理单帧：检测人脸并模糊。纯函数，供线程池调用。"""
        from face_detector import detect_faces, apply_blur

        faces = detect_faces(frame_bgr, confidence)
        if faces:
            frame_bgr = apply_blur(frame_bgr, faces, blur_kernel)
        return frame_bgr

    def _process_batch(self, batch, out, executor, confidence, blur_kernel):
        """并行处理一批帧，按序号排序后写入 VideoWriter。"""
        results = {}
        futures = {}
        for idx, frame_bgr in batch:
            if self._cancel_event.is_set():
                break
            futures[executor.submit(
                self._process_one_frame, frame_bgr, confidence, blur_kernel
            )] = idx

        for future in as_completed(futures):
            if self._cancel_event.is_set():
                break
            idx = futures[future]
            results[idx] = future.result()

        # 按帧序号排序写入
        for idx, _ in sorted(batch, key=lambda x: x[0]):
            if idx in results:
                out.write(results[idx])

    def _process(self):
        self._update_status("正在加载处理引擎...", 0)

        import cv2
        from moviepy import VideoFileClip


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

            # 先同步提取音频数据（避免与 iter_frames 并发冲突）
            audio_result = {"clip": None, "error": None}
            from voice_changer import extract_audio, pitch_shift_audio, make_audio_clip
            extracted = extract_audio(clip)
            if extracted is not None:
                audio_data, sr = extracted

                def _run_audio():
                    try:
                        shifted = pitch_shift_audio(audio_data, sr, pitch_steps)
                        audio_result["clip"] = make_audio_clip(shifted, sr)
                    except Exception as e:
                        audio_result["error"] = str(e)
                        print(f"音频处理失败: {e}")

                audio_thread = threading.Thread(target=_run_audio, daemon=True)
                audio_thread.start()
            else:
                audio_thread = None

            self._update_status("正在处理视频帧...", 5)

            temp_dir = Path(tempfile.gettempdir()) / "maskface"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_video = temp_dir / f"temp_video_{int(time.time())}.mp4"

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(temp_video), fourcc, fps, (w, h))

            workers = os.cpu_count() or 4
            with ThreadPoolExecutor(max_workers=workers) as executor:
                frame_count = 0
                batch = []

                for frame in clip.iter_frames(fps=fps, dtype="uint8"):
                    if self._cancel_event.is_set():
                        break

                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    batch.append((frame_count, frame_bgr))
                    frame_count += 1

                    if len(batch) >= BATCH_SIZE:
                        self._process_batch(batch, out, executor, confidence, blur_kernel)
                        if total_frames > 0:
                            pct = 5 + 85 * (frame_count / total_frames)
                            self._update_status(
                                f"处理视频帧 {frame_count}/{total_frames}", int(pct)
                            )
                        batch.clear()

                # 处理剩余帧
                if batch and not self._cancel_event.is_set():
                    self._process_batch(batch, out, executor, confidence, blur_kernel)

            out.release()

            if self._cancel_event.is_set():
                try:
                    os.remove(str(temp_video))
                except OSError:
                    pass
                clip.close()
                self._update_status("已取消", 0)
                self.root.after(0, lambda: self._set_action_state("ready"))
                self._processing = False
                return

            # 等待音频线程完成
            if audio_thread is not None:
                audio_thread.join()

            self._update_status("正在合成最终视频...", 92)

            processed_clip = VideoFileClip(str(temp_video))
            if audio_result["clip"] is not None:
                processed_clip = processed_clip.with_audio(audio_result["clip"])

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
        self._update_progress_bar(pct)

    def _update_progress_bar(self, pct: int):
        c = self._pb_canvas
        w = c.winfo_width()
        if w > 0:
            c.coords(self._pb_trough, 0, 0, w, 22)
            bar_w = int(w * pct / 100)
            c.coords(self._pb_bar, 0, 0, bar_w, 22)

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
            self._set_action_state("ready")


def main():
    root = tk.Tk()
    app = MaskFaceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()