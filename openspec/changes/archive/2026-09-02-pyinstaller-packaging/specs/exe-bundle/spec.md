## Purpose

将 MaskFace 应用打包为单个 Windows .exe 可执行文件，用户无需安装 Python 或任何依赖即可运行。

## ADDED Requirements

### Requirement: 单文件打包
系统 SHALL 通过 PyInstaller 将应用打包为单个 .exe 文件，包含所有 Python 依赖和资源文件。

#### Scenario: 生成 exe 文件
- **WHEN** 执行构建脚本
- **THEN** 在 dist/ 目录生成 MaskFace.exe，可独立运行

### Requirement: 无 Python 环境运行
系统 SHALL 在未安装 Python 的 Windows 系统上正常运行，双击 exe 即可启动。

#### Scenario: 干净环境启动
- **WHEN** 在未安装 Python 的 Windows 电脑上双击 MaskFace.exe
- **THEN** 应用正常启动，浏览器自动打开 Gradio 界面

### Requirement: 控制台窗口
系统 SHALL 以 Windows GUI 模式运行，不显示命令行控制台窗口。

#### Scenario: 无控制台
- **WHEN** 双击 MaskFace.exe 启动
- **THEN** 不弹出命令行窗口，仅在浏览器中显示界面