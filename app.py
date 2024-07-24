import streamlit as st
import requests
import io
from datetime import datetime
import math  # 添加这行来导入 math 模块


# Constants
TTS_API_URL = "https://api.wakaa.tech/v1/audio/speech"
STT_API_URL = "https://api.wakaa.tech/v1/audio/transcriptions"
TTS_MODELS = ["tts-1-hd", "tts-1"]
TTS_VOICES = ["shimmer", "echo", "fable", "onyx", "nova", "alloy"]
AUDIO_FORMATS = ["aac", "opus", "mp3", "flac", "wav"]
SUPPORTED_AUDIO_TYPES = ["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"]
LANGUAGE_MAP = {
    "中文": "zh", "英文": "en", "德语": "de", "法语": "fr",
    "西班牙语": "es", "意大利语": "it", "日语": "ja", "其他": ""
}

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

def init_ui():
    st.title("OpenAI 文字转语音 & 语音转文字界面 V2.3")
    tab = st.selectbox("选择功能:", ["文字转语音", "语音转文字"])
    api_key = st.text_input("输入你的OpenAI API密钥:", type="password")
    return tab, api_key

def text_to_speech(api_key):
    st.header("文字转语音 (TTS)")
    
    input_text = st.text_area("输入要转换为语音的文本:", max_chars=4096, height=200)
    char_count = len(input_text)
    st.write(f"当前字数: {char_count}/4096")
    if char_count > 3500:
        st.warning("注意：你已接近4096字符的限制。")

    model = st.selectbox("选择TTS模型:", TTS_MODELS)
    voice = st.selectbox("选择语音:", TTS_VOICES)
    response_format = st.selectbox("选择音频格式:", AUDIO_FORMATS)
    speed = st.slider("选择语速:", min_value=0.25, max_value=4.0, value=1.0, step=0.25)

    if st.button("生成音频"):
        if not api_key:
            st.error("请输入你的OpenAI API密钥。")
        elif not input_text:
            st.error("请输入要转换为语音的文本。")
        else:
            generate_audio(api_key, model, input_text, voice, response_format, speed)

def generate_audio(api_key, model, input_text, voice, response_format, speed):
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
        response = requests.post(TTS_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        process_audio_response(response, voice, response_format, input_text)
    else:
        st.error(f"错误: {response.status_code} - {response.text}")

def process_audio_response(response, voice, response_format, input_text):
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

def speech_to_text(api_key):
    st.header("语音转文字 (STT)")
    
    audio_file = st.file_uploader("上传音频文件:", type=SUPPORTED_AUDIO_TYPES)
    language = st.selectbox("选择音频语言:", list(LANGUAGE_MAP.keys()))
    
    custom_language = ""
    if language == "其他":
        custom_language = st.text_input("请输入音频语言的ISO-639-1代码:")

    if st.button("转换文字"):
        if not api_key:
            st.error("请输入你的OpenAI API密钥。")
        elif not audio_file:
            st.error("请上传音频文件。")
        else:
            transcribe_audio(api_key, audio_file, language, custom_language)

def transcribe_audio(api_key, audio_file, language, custom_language):
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {
        'file': (audio_file.name, audio_file, audio_file.type),
        'model': (None, "whisper-1")
    }
    if language in LANGUAGE_MAP and LANGUAGE_MAP[language]:
        files['language'] = (None, LANGUAGE_MAP[language])
    elif custom_language:
        files['language'] = (None, custom_language)

    with st.spinner("正在转换文字..."):
        response = requests.post(STT_API_URL, headers=headers, files=files)

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

def display_history():
    st.markdown("---")
    st.subheader("历史记录")

    # 分页逻辑
    items_per_page = 10
    total_items = len(st.session_state.history)
    total_pages = math.ceil(total_items / items_per_page)

    # 使用 session_state 来保存当前页码
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # 创建分页控件
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("首页"):
            st.session_state.current_page = 1

    with col2:
        if st.button("上一页") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1

    with col3:
        st.write(f"页 {st.session_state.current_page}/{total_pages}")

    with col4:
        if st.button("下一页") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1

    with col5:
        if st.button("末页"):
            st.session_state.current_page = total_pages

    # 计算当前页的起始和结束索引
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

    # 显示当前页的历史记录
    for index, item in enumerate(reversed(st.session_state.history[start_idx:end_idx]), start=start_idx):
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
                    mime=f"audio/{item['format']}",
                    key=f"download_button_{item['timestamp']}_{index}"
                )
        elif item["type"] == "stt":
            with st.expander(f"{item['timestamp']} - {item['filename']}"):
                st.write(f"文件名: {item['filename']}")
                st.write(f"转录文本: {item['transcription']}")

def main():
    tab, api_key = init_ui()

    if tab == "文字转语音":
        text_to_speech(api_key)
    elif tab == "语音转文字":
        speech_to_text(api_key)

    display_history()

    st.markdown("---")
    st.text("注意：你的API密钥不会被存储，仅用于本次请求。")
    st.text("历史记录仅在当前会话中保存,刷新页面会消失，请及时保存满意的结果。")

if __name__ == "__main__":
    main()
