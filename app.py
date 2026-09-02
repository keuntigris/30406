import streamlit as st
import time
import pandas as pd

st.set_page_config(page_title="1차 세계대전 RTS", layout="wide")

# 1. 게임 상태 초기화
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    
    # 국가별 초기 데이터 (1914년 설정)
    st.session_state.countries = {
        "프랑스": {"gold": 500, "pop": 3900, "manpower": 100, "supplies": 200, "civ_factories": 5, "mil_factories": 3, "army": 50, "airforce": 10, "navy": 20},
        "영국": {"gold": 600, "pop": 4500, "manpower": 120, "supplies": 250, "civ_factories": 6, "mil_factories": 4, "army": 40, "airforce": 15, "navy": 50},
        "러시아 제국": {"gold": 300, "pop": 17000, "manpower": 500, "supplies": 150, "civ_factories": 3, "mil_factories": 2, "army": 100, "airforce": 5, "navy": 15},
        "독일": {"gold": 550, "pop": 6700, "manpower": 200, "supplies": 300, "civ_factories": 7, "mil_factories": 5, "army": 80, "airforce": 20, "navy": 30},
        "오스트리아-헝가리": {"gold": 350, "pop": 5200, "manpower": 150, "supplies": 180, "civ_factories": 4, "mil_factories": 3, "army": 60, "airforce": 5, "navy": 10},
        "이탈리아": {"gold": 300, "pop": 3500, "manpower": 90, "supplies": 120, "civ_factories": 3, "mil_factories": 2, "army": 35, "airforce": 5, "navy": 15},
    }
    st.session_state.player_country = "프랑스"

# 2. 1주(10초) 주기 자원 업데이트 로직
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    
    for country, data in st.session_state.countries.items():
        # 골드 생산: 민간공장 수 비례
        data["gold"] += data["civ_factories"] * 20
        # 인력 생산: 인구수 비례
        data["manpower"] += int(data["pop"] * 0.01)
        # 보급품 생산: 군공장 수 비례
        data["supplies"] += data["mil_factories"] * 15

# UI 헤더
st.title("⚔️ 1914년 유럽: 1차 세계대전 실시간 전략 게임")
st.caption(f"현재 경과: {st.session_state.week}주 차 (1주는 현실 시간 10초)")

# 플레이어 국가 선택
selected_country = st.sidebar.selectbox(
    "플레이할 국가를 선택하세요:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country

my_data = st.session_state.countries[selected_country]

# 대시보드 - 자원 현황
st.header(f"🏛️ {selected_country} 상태 대시보드")
col1, col2, col3, col4 = st.columns(4)
col1.metric("골드", f"{my_data['gold']} G")
col2.metric("인력", f"{my_data['manpower']} 명")
col3.metric("보급품", f"{my_data['supplies']} 개")
col4.metric("공장 (민간/군)", f"{my_data['civ_factories']} / {my_data['mil_factories']}")

# 건설 및 군사 양성 세션
st.divider()
st.subheader("🏗️ 내정 및 군사 관리")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### 공장 건설 (각 100 Gold)")
    if st.button("민간공장 건설"):
        if my_data["gold"] >= 100:
            my_data["gold"] -= 100
            my_data["civ_factories"] += 1
            st.success("민간공장을 건설했습니다!")
            st.rerun()
        else:
            st.error("골드가 부족합니다.")
            
    if st.button("군공장 건설"):
        if my_data["gold"] >= 100:
            my_data["gold"] -= 100
            my_data["mil_factories"] += 1
            st.success("군공장을 건설했습니다!")
            st.rerun()
        else:
            st.error("골드가 부족합니다.")

with c2:
    st.markdown("### 군사 양성")
    if st.button("육군 10기 훈련 (인력 20, 보급품 30)"):
        if my_data["manpower"] >= 20 and my_data["supplies"] >= 30:
            my_data["manpower"] -= 20
            my_data["supplies"] -= 30
            my_data["army"] += 10
            st.success("육군 10기를 모집했습니다.")
            st.rerun()
        else:
            st.error("자원이 부족합니다.")

# 전세계 현황 표
st.divider()
st.subheader("🌍 1914년 유럽 국가별 현황")
df = pd.DataFrame.from_dict(st.session_state.countries, orient="index")
st.dataframe(df[["gold", "manpower", "supplies", "civ_factories", "mil_factories", "army", "navy", "airforce"]], use_container_width=True)

# 10초마다 자동 새로고침을 위한 타이머 연동 (실시간 루프)
time.sleep(1)
st.rerun()
