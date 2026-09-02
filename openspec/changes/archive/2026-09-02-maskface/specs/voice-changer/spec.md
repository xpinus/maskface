## Purpose

从视频中提取音轨并进行音调变换（pitch shift），改变说话人的声音特征以保护声纹隐私。

## ADDED Requirements

### Requirement: 音频提取
系统 SHALL 从输入视频中提取音频轨道，支持常见视频格式（mp4, avi, mov, mkv）。

#### Scenario: 从视频提取音频
- **WHEN** 输入一个包含音轨的 mp4 视频文件
- **THEN** 系统成功提取音频数据，返回可供处理的音频对象

#### Scenario: 视频无音轨
- **WHEN** 输入视频不包含音频轨道
- **THEN** 系统跳过音频处理，仅输出处理后的视频轨

### Requirement: 音调变换
系统 SHALL 对提取的音频应用 pitch shift 变换，半音偏移量可由用户配置（范围 -12 到 +12）。

#### Scenario: 降低音调
- **WHEN** 用户指定 pitch 为 -5 半音
- **THEN** 系统将音频整体降低 5 个半音，声音听起来更低沉

#### Scenario: 提高音调
- **WHEN** 用户指定 pitch 为 +3 半音
- **THEN** 系统将音频整体提高 3 个半音，声音听起来更尖锐

#### Scenario: 不做变声
- **WHEN** 用户指定 pitch 为 0
- **THEN** 系统保持音频原样，不做任何音调处理

### Requirement: 音频写回
系统 SHALL 将处理后的音频写回视频文件，与处理后的视频轨同步合成。

#### Scenario: 音频视频合成
- **WHEN** 视频轨和音频轨均已处理完毕
- **THEN** 系统将两者合成为完整的 MP4 文件，音画同步
