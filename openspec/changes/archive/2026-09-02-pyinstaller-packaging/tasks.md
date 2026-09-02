## 1. 模型文件准备

- [x] 1.1 创建 models/ 目录并下载模型文件（deploy.prototxt + caffemodel）

## 2. face_detector.py 改造

- [x] 2.1 新增 _get_model_dir() 函数，检测 sys.frozen 区分打包/开发模式
- [x] 2.2 打包模式下从 sys._MEIPASS/models/ 读取模型
- [x] 2.3 开发模式下从 ~/.video_anonymizer/ 读取模型
- [x] 2.4 移除网络下载逻辑（_download_file、URL 常量）

## 3. PyInstaller 配置

- [x] 3.1 创建 maskface.spec，配置单文件模式、数据文件、隐藏导入
- [x] 3.2 添加 pyinstaller 为开发依赖（uv add --dev）
- [x] 3.3 验证 .spec 配置正确（--clean 试打包）

## 4. 构建脚本

- [x] 4.1 创建 build.bat：检查模型 → 安装依赖 → 执行打包
- [x] 4.2 构建完成后显示输出路径和文件大小

## 5. 验证

- [x] 5.1 在干净环境运行 MaskFace.exe，验证人脸模糊和变声功能
- [x] 5.2 验证无网络环境下模型加载正常