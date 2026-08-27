import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 설정
st.title("Streamlit 회전 텍스트 예제")

# 회전 애니메이션이 들어간 HTML/CSS 코드
html_code = """
<style>
@keyframes rotate {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.rotating-text-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

.rotating-text {
    font-size: 48px;
    font-weight: bold;
    color: #FF4B4B; /* Streamlit 기본 포인트 컬러 */
    animation: rotate 4s linear infinite;
    display: inline-block;
}
</style>

<div class="rotating-text-container">
    <div class="rotating-text">ulala</div>
</div>
"""

# HTML 컴포넌트로 화면에 출력
components.html(html_code, height=220)
