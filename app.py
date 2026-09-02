import streamlit as st
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="1차 세계대전 RTS", layout="wide")

# 1. 게임 상태 초기화
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    
    # 국가 데이터
    st.session_state.countries = {
        "프랑스": {"gold": 500, "pop": 3900, "manpower": 100, "supplies": 200, "civ_factories": 5, "mil_factories": 3, "army": 50},
        "영국": {"gold": 600, "pop": 4500, "manpower": 120, "supplies": 250, "civ_factories": 6, "mil_factories": 4, "army": 40},
        "러시아 제국": {"gold": 300, "pop": 17000, "manpower": 500, "supplies": 150, "civ_factories": 3, "mil_factories": 2, "army": 100},
        "독일": {"gold": 550, "pop": 6700, "manpower": 200, "supplies": 300, "civ_factories": 7, "mil_factories": 5, "army": 80},
        "오스트리아-헝가리": {"gold": 350, "pop": 5200, "manpower": 150, "supplies": 180, "civ_factories": 4, "mil_factories": 3, "army": 60},
        "이탈리아": {"gold": 300, "pop": 3500, "manpower": 90, "supplies": 120, "civ_factories": 3, "mil_factories": 2, "army": 35},
    }
    
    # 지도 데이터 (도시 좌표 및 점령 상태)
    st.session_state.cities = {
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "civ": 3, "mil": 2},
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "civ": 4, "mil": 2},
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일", "railway": True, "civ": 4, "mil": 3},
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "civ": 2, "mil": 2},
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "civ": 2, "mil": 1},
        "로마": {"lat": 41.9028, "lon": 12.4964, "owner": "이탈리아", "railway": True, "civ": 2, "mil": 1},
        "메스 (국경 도시)": {"lat": 49.1193, "lon": 6.1757, "owner": "독일", "railway": False, "civ": 1, "mil": 1},
    }
    st.session_state.player_country = "프랑스"

# 2. 10초(1주) 생산 루프
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    for country, data in st.session_state.countries.items():
        data["gold"] += data["civ_factories"] * 20
        data["manpower"] += int(data["pop"] * 0.01)
        data["supplies"] += data["mil_factories"] * 15

# UI 헤더
st.title("⚔️ 1914년 유럽: 1차 세계대전 실시간 전장 지도")
st.caption(f"현재 경과: {st.session_state.week}주 차")

# 사이드바
selected_country = st.sidebar.selectbox(
    "플레이할 국가:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country

# --- 3. 유럽 전장 지도 시각화 ---
st.subheader("🗺️ 유럽 전장 지도 (도시 및 점령 상태)")

# 도시 데이터를 DataFrame으로 변환
cities_df = pd.DataFrame.from_dict(st.session_state.cities, orient="index").reset_index()
cities_df.rename(columns={"index": "도시명"}, inplace=True)

# 국가별 지정 색상 (1차 세계대전 스타일)
color_discrete_map = {
    "프랑스": "#1f77b4",          # 파란색
    "영국": "#d62728",            # 빨간색
    "독일": "#2ca02c",            # 초록/진회색 계열
    "오스트리아-헝가리": "#ff7f0e",  # 주황색
    "러시아 제국": "#9467bd",     # 보라색
    "이탈리아": "#8c564b"          # 갈색
}

# Plotly 지도 생성 (유럽 중심 설정)
fig = px.scatter_geo(
    cities_df,
    lat="lat",
    lon="lon",
    text="도시명",
    color="owner",
    size=[15]*len(cities_df),  # 점 크기
    hover_name="도시명",
    hover_data={"owner": True, "railway": True, "civ": True, "mil": True, "lat": False, "lon": False},
    color_discrete_map=color_discrete_map,
    projection="natural earth",
    title="1914 유럽 주요 도시 현황"
)

# 지도 범위 유럽으로 제한
fig.update_geos(
    center=dict(lat=50, lon=15),
    lataxis_range=[35, 65],
    lonaxis_range=[-10, 40],
    showcountries=True,
    countrycolor="LightGray",
    showcoastlines=True,
    showland=True,
    landcolor="#F0F2F6"
)

fig.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# --- 4. 영토 점령(도시 점령) 명령 섹션 ---
st.divider()
st.subheader("🚩 도시 이동 및 점령")

col1, col2 = st.columns(2)
with col1:
    target_city = st.selectbox("점령을 시도할 도시를 선택하세요:", list(st.session_state.cities.keys()))
    
with col2:
    current_owner = st.session_state.cities[target_city]["owner"]
    st.write(f"**선택한 도시:** {target_city}")
    st.write(f"**현재 점령국:** {current_owner}")
    
    if st.button("해당 도시로 육군 진격 및 점령 시도"):
        if current_owner == selected_country:
            st.warning("이미 자국이 점령 중인 도시입니다.")
        else:
            # 영토 점령 처리
            prev_owner = current_owner
            st.session_state.cities[target_city]["owner"] = selected_country
            
            # 이전 국가 공장 차감 및 신규 점령국 공장 추가
            lost_civ = st.session_state.cities[target_city]["civ"]
            lost_mil = st.session_state.cities[target_city]["mil"]
            
            st.session_state.countries[prev_owner]["civ_factories"] = max(0, st.session_state.countries[prev_owner]["civ_factories"] - lost_civ)
            st.session_state.countries[prev_owner]["mil_factories"] = max(0, st.session_state.countries[prev_owner]["mil_factories"] - lost_mil)
            
            st.session_state.countries[selected_country]["civ_factories"] += lost_civ
            st.session_state.countries[selected_country]["mil_factories"] += lost_mil
            
            st.success(f"{selected_country}이(가) {target_city}을(를) 점령했습니다! (공장 소유권 이전 완료)")
            st.rerun()

# 10초 주기 자동 갱신
time.sleep(1)
st.rerun()
