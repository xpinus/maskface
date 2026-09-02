# Repository Guidelines

## Project Overview

MaskFace is a desktop video anonymization tool — blur faces and pitch-shift voices in video files. It uses OpenCV DNN for face detection, MoviePy for video processing, and a Tkinter UI styled with Sun Valley (sv-ttk). Distributed as a standalone Windows executable via PyInstaller.

## Project Structure

```
maskface/
├── app.py              # Tkinter desktop UI (single-file, ~350 lines)
├── face_detector.py    # OpenCV DNN face detection + blur
├── voice_changer.py    # Librosa pitch-shift audio processing
├── models/             # Pre-trained Caffe model files
│   ├── deploy.prototxt
│   └── res10_300x300_ssd_iter_140000_fp16.caffemodel
├── maskface.spec       # PyInstaller spec (onedir bundle)
├── build.bat           # One-click build script
├── pyproject.toml      # uv project config
└── dist/MaskFace/      # Built output (not committed)
```

## Build & Run

| Command | Purpose |
|---------|---------|
| `uv sync` | Install all dependencies |
| `uv run python app.py` | Run the Tkinter app locally |
| `build.bat` | Clean + PyInstaller one-click build |
| `.venv\Scripts\python.exe -m PyInstaller maskface.spec --noconfirm` | Manual packaging |

## Coding Style

- **Python 3.11+**, UTF-8, 4-space indentation
- Follow PEP 8; use `uv` for dependency management
- Heavy imports (cv2, numpy, librosa, moviepy) are **lazy** — imported inside `_process()`, not at module level — to keep the Tkinter window launching instantly
- GUI code is a single `MaskFaceApp` class in `app.py`; use `tk.Tk` widgets styled via `sv_ttk`
- Threading: all processing runs on a `daemon=True` thread; UI updates via `root.after(0, ...)`

## Testing

- Manual end-to-end: run the app, select a test video, verify face blur and pitch-shift, save output
- No automated test suite; the model files are binary and not version-controlled

## Commit & PR Guidelines

- Follow the repo's OpenSpec workflow: changes live in `openspec/changes/` with proposal, design, specs, and tasks artifacts
- Archive completed changes via `openspec archive`
- Keep commits focused; one logical change per commit

## Adding Dependencies

```bash
uv add <package>          # Add a runtime dependency
uv add --dev <package>    # Add a dev-only dependency
```

Then update `maskface.spec` if the new package needs extra `hiddenimports` or `copy_metadata`.