import streamlit as st
import requests
import io
from datetime import datetime

# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("OpenAI 文字转语音 & 语音转文字界面 V2.0")

# 选择功能
tab = st.selectbox("选择功能:", ["文字转语音", "语音转文字"])

# API密钥输入
api_key = st.text_input("输入你的OpenAI API密钥:", type="password")

if tab == "文字转语音":
    # 文字转语音部分
    st.header("文字转语音 (TTS)")
    
    # 输入文本
    input_text = st.text_area("输入要转换为语音的文本:", max_chars=4096, height=200)

    # 字数统计和警告
    char_count = len(input_text)
    st.write(f"当前字数: {char_count}/4096")
    if char_count > 3500:
        st.warning("注意：你已接近4096字符的限制。")

    # 其他设置保持不变...
    model = st.selectbox("选择TTS模型:", ["tts-1-hd", "tts-1"])
    voice = st.selectbox("选择语音:", ["shimmer", "echo", "fable", "onyx", "nova", "alloy"])
    response_format = st.selectbox("选择音频格式:", ["aac", "opus", "mp3", "flac", "wav"])
    speed = st.slider("选择语速:", min_value=0.25, max_value=4.0, value=1.0, step=0.25)

    if st.button("生成音频"):
        if not api_key:
            st.error("请输入你的OpenAI API密钥。")
        elif not input_text:
            st.error("请输入要转换为语音的文本。")
        else:
            # API请求代码保持不变...
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "input": input_text,
                "voice": voice,
                "response_format": response_format,
                "speed": speed
            }

            with st.spinner("正在生成音频..."):
                response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                # 音频处理代码保持不变...
                timestamp = datetime.now().strftime("%Y%m%d-%H%M")
                filename = f"{timestamp}-{voice}.{response_format}"
                audio_bytes = io.BytesIO(response.content)

                st.audio(audio_bytes, format=f'audio/{response_format}')

                st.download_button(
                    label="下载音频",
                    data=audio_bytes,
                    file_name=filename,
                    mime=f"audio/{response_format}"
                )

                st.session_state.history.append({
                    "type": "tts",
                    "timestamp": timestamp,
                    "text": input_text[:50] + "..." if len(input_text) > 50 else input_text,
                    "voice": voice,
                    "format": response_format,
                    "filename": filename,
                    "audio": response.content
                })

                st.success("音频生成成功！你可以在上方播放或使用下载按钮下载。")
            else:
                st.error(f"错误: {response.status_code} - {response.text}")

    # 历史记录显示代码保持不变...
    st.markdown("---")
    st.subheader("历史记录")

    for i, item in enumerate(reversed(st.session_state.history)):
        if item["type"] == "tts":
            with st.expander(f"{item['timestamp']} - {item['voice']}"):
                st.write(f"文本: {item['text']}")
                st.write(f"语音: {item['voice']}")
                st.write(f"格式: {item['format']}")
                st.audio(item['audio'], format=f"audio/{item['format']}")
                st.download_button(
                    label=f"下载 {item['filename']}",
                    data=item['audio'],
                    file_name=item['filename'],
                    mime=f"audio/{item['format']}"
                )

elif tab == "语音转文字":
    # 语音转文字部分
    st.header("语音转文字 (STT)")
    
    # 上传音频文件
    audio_file = st.file_uploader("上传音频文件 (支持格式: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm):", type=["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"])

    # 选择语言
    language = st.selectbox("选择音频语言:", ["中文", "英文", "德语", "法语", "西班牙语", "意大利语", "日语", "其他"])
    language_map = {
        "中文": "zh",
        "英文": "en",
        "德语": "de",
        "法语": "fr",
        "西班牙语": "es",
        "意大利语": "it",
        "日语": "ja",
        "其他": ""
    }
    
    custom_language = ""
    if language == "其他":
        custom_language = st.text_input("请输入音频语言的ISO-639-1代码:")

    if st.button("转换文字"):
        if not api_key:
            st.error("请输入你的OpenAI API密钥。")
        elif not audio_file:
            st.error("请上传音频文件。")
        else:
            # API请求代码
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            files = {
                'file': (audio_file.name, audio_file, audio_file.type),
                'model': (None, "whisper-1")
            }
            if language in language_map and language_map[language]:
                files['language'] = (None, language_map[language])
            elif custom_language:
                files['language'] = (None, custom_language)

            with st.spinner("正在转换文字..."):
                response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                transcription = response.json()["text"]
                st.text_area("转换结果:", transcription, height=200)

                st.session_state.history.append({
                    "type": "stt",
                    "timestamp": datetime.now().strftime("%Y%m%d-%H%M"),
                    "filename": audio_file.name,
                    "transcription": transcription
                })

                st.success("文字转换成功！")
            else:
                st.error(f"错误: {response.status_code} - {response.text}")

    # 历史记录显示代码
    st.markdown("---")
    st.subheader("历史记录")

    for i, item in enumerate(reversed(st.session_state.history)):
        if item["type"] == "stt":
            with st.expander(f"{item['timestamp']} - {item['filename']}"):
                st.write(f"文件名: {item['filename']}")
                st.write(f"转录文本: {item['transcription']}")

st.markdown("---")
st.text("注意：你的API密钥不会被存储，仅用于本次请求。")
st.text("历史记录仅在当前会话中保存,刷新页面会消失，请及时保存满意的结果。")
