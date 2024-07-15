# OpenAI 文字转语音 & 语音转文字 Streamlit 应用

这是一个使用Streamlit构建的Web应用程序，利用OpenAI的API提供文字转语音(TTS)和语音转文字(STT)功能。
![image](https://github.com/user-attachments/assets/c091a50b-4b81-4d9c-990d-d2f394471506)


## 功能

- **文字转语音 (TTS)**
  - 支持多种TTS模型和声音选项
  - 可调节语速
  - 多种音频格式输出
  - 实时音频预览和下载

- **语音转文字 (STT)**
  - 支持多种音频格式上传
  - 多语言支持
  - 快速准确的转录

- **历史记录**
  - 保存TTS和STT操作历史
  - 方便回顾和重新下载

## 安装

1. 克隆此仓库：
   ```
   git clone https://github.com/niqifan007/Openai-tts-stt-streamlit.git
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```
   streamlit run app.py
   ```

## 使用说明

1. 启动应用后，在浏览器中打开显示的URL。
2. 输入你的OpenAI API密钥。
3. 选择要使用的功能（TTS或STT）。
4. 按照界面提示进行操作。

注意：请确保你有有效的OpenAI API密钥，并且有足够的额度来使用这些服务。

## 注意事项

- API密钥仅用于当前会话，不会被存储。
- 历史记录仅在当前会话中保存，刷新页面后会消失。

## 贡献

欢迎提交问题报告和拉取请求。对于重大更改，请先开issue讨论您想要改变的内容。