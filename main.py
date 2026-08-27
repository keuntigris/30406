import streamlit as st
from gtts import gTTS
import io

st.title("🗣️ 간단한 TTS 프로그램")
st.write("텍스트를 입력하면 음성으로 변환해 드립니다.")

# 사용자 입력 받기
text_input = st.text_area(
    "음성으로 변환할 텍스트를 입력하세요", 
    "안녕하세요! Streamlit으로 만든 TTS 프로그램입니다."
)

# 언어 옵션 설정 (화면 표시용 이름: gTTS 언어 코드)
lang_options = {
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어": "zh-CN",
    "스페인어": "es"
}

# format_func를 활용하여 깔끔하게 선택창 구현
selected_label = st.selectbox(
    "언어를 선택하세요",
    options=list(lang_options.keys())
)

if st.button("음성 변환"):
    if not text_input.strip():
        st.warning("텍스트를 입력해주세요.")
    else:
        with st.spinner("음성을 생성하는 중입니다..."):
            lang_code = lang_options[selected_label]
            
            # TTS 변환 수행
            tts = gTTS(text=text_input, lang=lang_code)
            
            # 메모리에 음성 파일 저장
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # 결과 출력
            st.success("변환이 완료되었습니다!")
            st.audio(audio_fp, format="audio/mp3")
            st.download_button(
                label="음성 파일 다운로드",
                data=audio_fp,
                file_name="speech.mp3",
                mime="audio/mp3"
            )
