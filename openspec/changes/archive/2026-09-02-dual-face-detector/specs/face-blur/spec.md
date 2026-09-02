## MODIFIED Requirements

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