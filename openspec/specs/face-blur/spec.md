## Purpose

对视频中的人脸区域进行检测并使用高斯模糊处理，使面部生物特征不可识别，保护个人隐私。

## ADDED Requirements

### Requirement: 人脸检测
系统 SHALL 使用 YuNet 模型作为主检测器，对每一帧进行人脸检测；当 YuNet 未检出人脸时，回退使用 Caffe SSD 模型。两模型共用同一置信度阈值。

#### Scenario: 正脸检测
- **WHEN** 输入一帧包含正面人脸的视频画面
- **THEN** YuNet 检出所有人脸，返回边界框坐标和置信度，不触发 Caffe 回退

#### Scenario: 侧脸或仰角检测
- **WHEN** 输入一帧包含侧脸或仰头大笑人脸的视频画面
- **THEN** YuNet 检出人脸并返回结果，检测率高于仅使用 Caffe SSD

#### Scenario: YuNet 未检出时回退
- **WHEN** YuNet 未检出人脸
- **THEN** 系统回退使用 Caffe SSD 模型检测

#### Scenario: 帧中无人脸
- **WHEN** 输入一帧不包含人脸的视频画面
- **THEN** 两个模型均返回空列表，不进行模糊处理

### Requirement: 高斯模糊
系统 SHALL 对检测到的人脸区域应用高斯模糊，模糊核大小可由用户配置（奇数，范围 1-99）。

#### Scenario: 正常模糊处理
- **WHEN** 用户指定模糊核大小为 55，帧中检测到人脸
- **THEN** 系统对每个人脸区域应用 55x55 高斯核模糊，人脸不可识别

#### Scenario: 无效模糊核大小
- **WHEN** 用户指定模糊核大小为偶数（如 50）
- **THEN** 系统自动调整为最近的奇数（51）并继续处理