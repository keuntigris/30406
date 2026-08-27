import streamlit as st
from gtts import gTTS
import io

# 앱 제목 설정
st.title("🔊 Text-to-Speech (TTS) 프로그램")
st.write("텍스트를 입력하면 음성 파일로 변환해 줍니다.")

# 사용자가 입력할 텍스트 상자
text_input = st.text_area("변환할 텍스트를 입력하세요", value="안녕하세요! Streamlit으로 만든 TTS 프로그램입니다.", height=150)

# 언어 선택 옵션
language_options = {
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어": "zh-CN",
    "스페인어": "es",
    "프랑스어": "fr"
}

selected_lang = st.selectbox("언어를 선택하세요", list(language_options.keys()))

# 변환 버튼
if st.button("음성으로 변환하기"):
    if text_input.strip() == "":
        st.warning("텍스트를 입력해 주세요.")
    else:
        with st.spinner("음성을 생성하는 중입니다..."):
            try:
                # gTTS를 사용해 음성 변환 (메모리 버퍼 사용)
                lang_code = language_options[selected_lang]
                tts = gTTS(text=text_input, lang=lang_code)
                
                # 파일 저장 없이 메모리(BytesIO)에 직접 저장
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                
                st.success("변환이 완료되었습니다!")
                
                # 오디오 재생기 표시
                st.audio(audio_bytes, format="audio/mp3")
                
                # MP3 파일 다운로드 버튼
                st.download_button(
                    label="📥 MP3 파일 다운로드",
                    data=audio_bytes,
                    file_name="speech.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"음성 변환 중 오류가 발생했습니다: {e}")
