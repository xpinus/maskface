## Context

当前 face_detector.py 在运行时从 GitHub 下载模型到 ~/.video_anonymizer/。打包后需要改为从 exe 内部读取。使用 PyInstaller 的 sys._MEIPASS 机制，模型文件在构建时通过 .spec 的 datas 配置嵌入。

## Goals / Non-Goals

**Goals:**
- 生成单文件 MaskFace.exe，双击即用
- 模型文件嵌入 exe，无需联网
- 开发模式不受影响（uv run python app.py 仍可用）

**Non-Goals:**
- 不支持 macOS/Linux 打包（仅 Windows）
- 不生成安装程序（仅绿色便携 exe）
- 不压缩 exe 体积（接受 160-200MB）

## Decisions

### 1. 单文件模式（--onefile）
- **选择**: PyInstaller --onefile，生成单个 exe
- **理由**: 用户只需一个文件，分发简单
- **代价**: 启动时需解压到临时目录，首次启动慢 2-3 秒

### 2. Windows GUI 模式（console=False）
- **选择**: 禁用控制台窗口
- **理由**: 用户通过浏览器交互，命令行窗口多余
- **备选方案**: 保留控制台（调试方便但用户体验差）

### 3. 模型路径适配策略
- **选择**: sys.frozen 检测 + 双路径模式
  - 打包模式：sys._MEIPASS/models/
  - 开发模式：~/.video_anonymizer/
- **理由**: 改动最小，不影响现有开发流程
- **备选方案**: 统一路径（开发者也需手动放置模型到 models/，体验差）

### 4. 模型文件存储位置
- **选择**: 构建时 models/ 目录在项目根，.spec 中 datas 配置映射
- **理由**: 模型文件与代码一起版本管理，构建脚本自动下载
- .spec 配置：datas=[('models/deploy.prototxt', 'models'), ('models/...caffemodel', 'models')]

### 5. 隐藏导入
- **选择**: 显式指定 hiddenimports 和 collect-all
- 需要特殊处理的库：
  - gradio：使用 --collect-all gradio 收集所有子模块和静态资源
  - 
umba：使用 --collect-all numba，JIT 编译依赖
  - soundfile：librosa 的音频后端
  - imageio_ffmpeg：moviepy 的 ffmpeg 后端
  - cv2：OpenCV 原生模块，PyInstaller 有内置 hook

### 6. 构建脚本（build.bat）
- **选择**: .bat 批处理，三步流程
  1. 检查并下载模型
  2. uv add --dev pyinstaller
  3. uv run pyinstaller maskface.spec
- **理由**: 简单直接，Windows 原生支持

## Risks / Trade-offs

- [exe 体积大（160-200MB）] → 接受，单文件分发的代价
- [启动慢（解压到临时目录）] → 首次 2-3 秒，后续可接受
- [numba JIT 编译兼容性] → 使用 --collect-all numba 确保所有 .py 文件包含
- [Gradio 静态资源路径] → 使用 --collect-all gradio 确保模板和静态文件完整
- [杀毒软件误报] → PyInstaller 打包的 exe 偶有误报，需在知名杀软中提交白名单