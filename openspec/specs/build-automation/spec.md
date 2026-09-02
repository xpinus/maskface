## Purpose

提供一键构建脚本，自动完成从模型下载到 PyInstaller 打包的全流程，无需手动操作。

## ADDED Requirements

### Requirement: 一键打包
系统 SHALL 提供 build.bat 脚本，执行后自动完成模型下载、依赖安装、PyInstaller 打包。

#### Scenario: 执行构建
- **WHEN** 开发者运行 build.bat
- **THEN** 脚本自动下载模型文件（如不存在）、安装 pyinstaller、执行打包，最终输出 dist/MaskFace.exe

### Requirement: 模型自动下载
系统 SHALL 在构建时检查 models/ 目录，如模型文件不存在则自动从 GitHub 下载。

#### Scenario: 首次构建
- **WHEN** models/ 目录为空，执行 build.bat
- **THEN** 脚本自动下载 deploy.prototxt 和 caffemodel 到 models/ 目录

#### Scenario: 模型已存在
- **WHEN** models/ 目录已有模型文件，执行 build.bat
- **THEN** 脚本跳过下载，直接执行打包

### Requirement: 构建结果反馈
系统 SHALL 在构建完成后显示成功或失败信息，并指明 exe 输出路径。

#### Scenario: 构建成功
- **WHEN** PyInstaller 打包完成
- **THEN** 显示 "构建完成: dist/MaskFace.exe" 及文件大小