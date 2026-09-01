import streamlit as st
import time
from streamlit_autorun import st_autorun

# 1. 페이지 기본 설정
st.set_page_config(page_title="1914 WWI Strategy Game", layout="wide")

# 2. 실시간 루프 설정 (10초마다 자동으로 상태 업데이트)
st_autorun(interval=10000, key="game_clock")

# 3. 게임 데이터 초기화 (세션 상태)
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.week = 1
    st.session_state.player_nation = "독일"
    
    # 국가 및 도시 기본 구조 데이터
    st.session_state.nations = {
        "프랑스": {"gold": 200, "manpower": 500, "supplies": 100, "pop": 1000},
        "영국": {"gold": 200, "manpower": 500, "supplies": 100, "pop": 800},
        "러시아 제국": {"gold": 150, "manpower": 1000, "supplies": 50, "pop": 2000},
        "독일": {"gold": 300, "manpower": 800, "supplies": 150, "pop": 1200},
        "오스트리아-헝가리 제국": {"gold": 150, "manpower": 600, "supplies": 80, "pop": 900},
        "이탈리아": {"gold": 100, "manpower": 400, "supplies": 60, "pop": 700},
    }
    
    st.session_state.cities = {
        "파리": {"owner": "프랑스", "civ_factories": 2, "mil_factories": 2, "army": 50, "has_railway": True},
        "런던": {"owner": "영국", "civ_factories": 3, "mil_factories": 2, "army": 40, "has_railway": True},
        "상트페테르부르크": {"owner": "러시아 제국", "civ_factories": 1, "mil_factories": 1, "army": 60, "has_railway": False},
        "베를린": {"owner": "독일", "civ_factories": 3, "mil_factories": 3, "army": 70, "has_railway": True},
        "빈": {"owner": "오스트리아-헝가리 제국", "civ_factories": 2, "mil_factories": 1, "army": 45, "has_railway": True},
        "로마": {"owner": "이탈리아", "civ_factories": 1, "mil_factories": 1, "army": 30, "has_railway": True},
    }

# 4. 주간 자원 업데이트 로직 (1주 = 현실시간 10초)
def update_resources():
    st.session_state.week += 1
    
    # 각 도시별 공장 수 합산 및 자원 산출
    for nation, data in st.session_state.nations.items():
        total_civ = sum(c["civ_factories"] for c in st.session_state.cities.values() if c["owner"] == nation)
        total_mil = sum(c["mil_factories"] for c in st.session_state.cities.values() if c["owner"] == nation)
        
        # 골드: 민간공장 비례 / 인력: 인구수 비례 / 보급품: 군공장 비례
        data["gold"] += total_civ * 20
        data["manpower"] += int(data["pop"] * 0.05)
        data["supplies"] += total_mil * 15

# 페이지가 자동 갱신될 때마다 자원 증가 실행
update_resources()

# 5. UI 구성
st.title("⚔️ 1914년 1차 세계대전 실시간 전략 게임")
st.sidebar.header("국가 선택")
st.session_state.player_nation = st.sidebar.selectbox("플레이할 국가를 선택하세요:", list(st.session_state.nations.keys()))

player_data = st.session_state.nations[st.session_state.player_nation]

# 상단 현황판
col1, col2, col3, col4 = st.columns(4)
col1.metric("경과 시간", f"{st.session_state.week} 주차")
col2.metric("골드 (Gold)", f"{player_data['gold']} G")
col3.metric("인력 (Manpower)", f"{player_data['manpower']} 명")
col4.metric("보급품 (Supplies)", f"{player_data['supplies']} 개")

st.divider()

# 영토 및 도시 관리
st.subheader("🗺️ 도시 및 공장 관리")

player_cities = {name: info for name, info in st.session_state.cities.items() if info["owner"] == st.session_state.player_nation}

for city_name, city_info in player_cities.items():
    with st.expander(f"📍 {city_name} (육군: {city_info['army']}명)", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.write(f"민간공장: {city_info['civ_factories']}개")
        c2.write(f"군공장: {city_info['mil_factories']}개")
        c3.write(f"철도 연결 여부: {'예' if city_info['has_railway'] else '아니오'}")
        
        b1, b2 = st.columns(2)
        if b1.button(f"{city_name}에 민간공장 건설 (100G)", key=f"civ_{city_name}"):
            if player_data["gold"] >= 100:
                player_data["gold"] -= 100
                city_info["civ_factories"] += 1
                st.success("민간공장이 건설되었습니다.")
                st.rerun()
            else:
                st.error("골드가 부족합니다.")
                
        if b2.button(f"{city_name}에 군공장 건설 (100G)", key=f"mil_{city_name}"):
            if player_data["gold"] >= 100:
                player_data["gold"] -= 100
                city_info["mil_factories"] += 1
                st.success("군공장이 건설되었습니다.")
                st.rerun()
            else:
                st.error("골드가 부족합니다.")

# 군대 징집
st.divider()
st.subheader("🎖️ 군사 양성")
col_recruit1, col_recruit2 = st.columns(2)

with col_recruit1:
    target_city = st.selectbox("군대를 배치할 도시 선택", list(player_cities.keys()))
    if st.button("육군 10명 징집 (인력 10, 보급 20 소모)"):
        if player_data["manpower"] >= 10 and player_data["supplies"] >= 20:
            player_data["manpower"] -= 10
            player_data["supplies"] -= 20
            st.session_state.cities[target_city]["army"] += 10
            st.success(f"{target_city}에 육군 10명이 추가되었습니다.")
            st.rerun()
        else:
            st.error("자원이 부족합니다.")
