## MODIFIED Requirements

### Requirement: 人脸检测
系统 SHALL 对每一帧独立调用 OpenCV DNN SSD 模型进行人脸检测，返回每个人脸的位置和置信度。

#### Scenario: 单帧检测到多张人脸
- **WHEN** 输入一帧包含多张人脸的视频画面
- **THEN** 系统返回所有人脸的边界框坐标 (x, y, w, h) 及对应置信度

#### Scenario: 帧中无人脸
- **WHEN** 输入一帧不包含人脸的视频画面
- **THEN** 系统返回空列表，不进行模糊处理

#### Scenario: 人脸首次出现
- **WHEN** 视频中人脸从无到有出现
- **THEN** 系统在出现的第一帧即刻检测到人脸并应用模糊，无延迟

## REMOVED Requirements

### Requirement: 跳帧优化
**Reason**: 跳帧检测在新人脸出现时存在 0-4 帧盲区，且线性插值逻辑复杂。SSD 模型足够轻量，逐帧检测性能可接受。
**Migration**: 无需迁移，`detect_faces()` 接口不变，调用方改为每帧直接调用。

### Requirement: 模型自动下载
**Reason**: 模型文件已通过 PyInstaller 内嵌打包，不再需要运行时下载。
**Migration**: 无需迁移，`_get_model_dir()` 已支持打包模式。