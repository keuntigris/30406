import streamlit as st
from gtts import gTTS
import io

st.title("🗣️ 간단한 TTS 프로그램")
st.write("텍스트를 입력하면 음성으로 변환해 드립니다.")

# 사용자 입력 받기
text_input = st.text_area("음성으로 변환할 텍스트를 입력하세요", "안녕하세요! Streamlit으로 만든 TTS 프로그램입니다.")

# 언어 선택 Option
language = st.selectbox(
    "언어를 선택하세요",
    [("한국어", "ko"), ("영어", "en"), ("일본어", "ja")]
)

if st.button("음성 변환"):
    if text_input.strip() == "":
        st.warning("텍스트를 입력해주세요.")
    else:
        # TTS 변환 수행
        lang_code = language[1]
        tts = gTTS(text=text_input, lang=lang_code)
        
        # 메모리에 음성 파일 저장 (임시 파일 생성 없음)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # 음성 재생 및 다운로드 버튼 표시
        st.audio(audio_fp, format="audio/mp3")
        st.download_button(
            label="음성 파일 다운로드",
            data=audio_fp,
            file_name="speech.mp3",
            mime="audio/mp3"
        )
