import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="1차 세계대전 RTS - 1914 유럽", layout="wide")

# ----------------------------------------------------
# 1. 게임 데이터 초기화
# ----------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    
    # 국가 세부 데이터
    st.session_state.countries = {
        "프랑스": {"gold": 600, "pop": 39000, "manpower": 200, "supplies": 300, "civ_factories": 8, "mil_factories": 5, "alliance": "협상국"},
        "영국": {"gold": 800, "pop": 45000, "manpower": 220, "supplies": 400, "civ_factories": 10, "mil_factories": 6, "alliance": "협상국"},
        "러시아 제국": {"gold": 400, "pop": 170000, "manpower": 800, "supplies": 200, "civ_factories": 5, "mil_factories": 4, "alliance": "협상국"},
        "독일 제국": {"gold": 750, "pop": 67000, "manpower": 350, "supplies": 450, "civ_factories": 11, "mil_factories": 8, "alliance": "동맹국"},
        "오스트리아-헝가리": {"gold": 450, "pop": 52000, "manpower": 250, "supplies": 250, "civ_factories": 6, "mil_factories": 4, "alliance": "동맹국"},
        "이탈리아": {"gold": 350, "pop": 35000, "manpower": 150, "supplies": 180, "civ_factories": 5, "mil_factories": 3, "alliance": "중립/협상국"},
    }
    
    # 1914년 유럽 주요 도시 데이터 (위도, 경도, 소유국, 철도망, 주둔군)
    st.session_state.cities = {
        # 프랑스
        "파리 (수도)": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "civ": 3, "mil": 2, "is_capital": True, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5, "해군": 0}},
        "마르세유": {"lat": 43.2965, "lon": 5.3698, "owner": "프랑스", "railway": True, "civ": 2, "mil": 1, "is_capital": False, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0, "해군": 15}},
        "리용": {"lat": 45.7640, "lon": 4.8357, "owner": "프랑스", "railway": True, "civ": 2, "mil": 1, "is_capital": False, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0, "해군": 0}},
        "베르됭 (요새)": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "railway": False, "civ": 1, "mil": 1, "is_capital": False, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2, "해군": 0}},
        
        # 영국
        "런던 (수도)": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "civ": 4, "mil": 3, "is_capital": True, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10, "해군": 20}},
        "맨체스터": {"lat": 53.4808, "lon": -2.2426, "owner": "영국", "railway": True, "civ": 3, "mil": 2, "is_capital": False, "garrison": {"보병": 10, "포병": 0, "기병": 0, "공군": 0, "해군": 0}},
        "포츠머스 (해군기지)": {"lat": 50.8198, "lon": -1.0880, "owner": "영국", "railway": True, "civ": 3, "mil": 1, "is_capital": False, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0, "해군": 35}},
        
        # 독일 제국
        "베를린 (수도)": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "railway": True, "civ": 4, "mil": 3, "is_capital": True, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10, "해군": 0}},
        "함부르크": {"lat": 53.5511, "lon": 9.9937, "owner": "독일 제국", "railway": True, "civ": 3, "mil": 2, "is_capital": False, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0, "해군": 25}},
        "뮌헨": {"lat": 48.1351, "lon": 11.5820, "owner": "독일 제국", "railway": True, "civ": 2, "mil": 2, "is_capital": False, "garrison": {"보병": 15, "포병": 5, "기병": 5, "공군": 0, "해군": 0}},
        "메스 (전선 요새)": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "railway": True, "civ": 1, "mil": 1, "is_capital": False, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5, "해군": 0}},
        "쾨니히스베르크": {"lat": 54.7104, "lon": 20.4522, "owner": "독일 제국", "railway": False, "civ": 1, "mil": 0, "is_capital": False, "garrison": {"보병": 15, "포병": 5, "기병": 5, "공군": 0, "해군": 5}},

        # 오스트리아-헝가리
        "빈 (수도)": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "civ": 3, "mil": 2, "is_capital": True, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2, "해군": 0}},
        "부다페스트": {"lat": 47.4979, "lon": 19.0402, "owner": "오스트리아-헝가리", "railway": True, "civ": 2, "mil": 1, "is_capital": False, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0, "해군": 0}},
        "프라하": {"lat": 50.0755, "lon": 14.4378, "owner": "오스트리아-헝가리", "railway": True, "civ": 1, "mil": 1, "is_capital": False, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0, "해군": 0}},
        "사라예보": {"lat": 43.8563, "lon": 18.4131, "owner": "오스트리아-헝가리", "railway": False, "civ": 0, "mil": 0, "is_capital": False, "garrison": {"보병": 15, "포병": 0, "기병": 2, "공군": 0, "해군": 0}},

        # 러시아 제국
        "상트페테르부르크 (수도)": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "civ": 2, "mil": 2, "is_capital": True, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2, "해군": 10}},
        "모스크바": {"lat": 55.7558, "lon": 37.6173, "owner": "러시아 제국", "railway": True, "civ": 2, "mil": 1, "is_capital": False, "garrison": {"보병": 30, "포병": 5, "기병": 10, "공군": 0, "해군": 0}},
        "바르샤바": {"lat": 52.2297, "lon": 21.0122, "owner": "러시아 제국", "railway": False, "civ": 1, "mil": 1, "is_capital": False, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0, "해군": 0}},
        "오데사": {"lat": 46.4825, "lon": 30.7233, "owner": "러시아 제국", "railway": True, "civ": 1, "mil": 0, "is_capital": False, "garrison": {"보병": 15, "포병": 0, "기병": 5, "공군": 0, "해군": 10}},

        # 이탈리아
        "로마 (수도)": {"lat": 41.9028, "lon": 12.4964, "owner": "이탈리아", "railway": True, "civ": 2, "mil": 1, "is_capital": True, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 2, "해군": 10}},
        "밀라노": {"lat": 45.4642, "lon": 9.1900, "owner": "이탈리아", "railway": True, "civ": 2, "mil": 1, "is_capital": False, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0, "해군": 0}},
        "나폴리": {"lat": 40.8518, "lon": 14.2681, "owner": "이탈리아", "railway": False, "civ": 1, "mil": 1, "is_capital": False, "garrison": {"보병": 10, "포병": 0, "기병": 0, "공군": 0, "해군": 10}},
    }
    
    st.session_state.player_country = "프랑스"

# 병종 스펙 정의 (비용, 생산주기, 스탯)
UNIT_SPECS = {
    "보병 사단": {"gold": 30, "manpower": 50, "supplies": 20, "attack": 25, "defense": 35, "icon": "🪖"},
    "포병 사단": {"gold": 80, "manpower": 20, "supplies": 60, "attack": 55, "defense": 15, "icon": "💥"},
    "기병 사단": {"gold": 50, "manpower": 30, "supplies": 30, "attack": 30, "defense": 20, "icon": "🐎"},
    "비행대대": {"gold": 120, "manpower": 10, "supplies": 80, "attack": 70, "defense": 10, "icon": "✈️"},
    "해군 함대": {"gold": 200, "manpower": 40, "supplies": 120, "attack": 80, "defense": 60, "icon": "⚓"},
}

# ----------------------------------------------------
# 2. 1주(10초) 주기 실시간 타이머 및 자원 갱신
# ----------------------------------------------------
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    
    # 국가 자원 획득
    for country, data in st.session_state.countries.items():
        data["gold"] += data["civ_factories"] * 25
        data["manpower"] += int(data["pop"] * 0.002)
        data["supplies"] += data["mil_factories"] * 20

# ----------------------------------------------------
# 3. 사이드바 및 레이아웃
# ----------------------------------------------------
st.title("📜 1914년 유럽: 1차 세계대전 대전략")
st.caption(f"🗓️ Current Time: 1914년 {st.session_state.week}주 차 (1주 = 현실 10초)")

selected_country = st.sidebar.selectbox(
    "👑 플레이할 국가 선택:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country
my_country = st.session_state.countries[selected_country]

# 상단 대시보드
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 국고 (Gold)", f"{my_country['gold']} G")
col2.metric("🪖 징집 가능 인력", f"{my_country['manpower']} 명")
col3.metric("📦 보급품", f"{my_country['supplies']} 톤")
col4.metric("🏭 민간 공장", f"{my_country['civ_factories']} 개")
col5.metric("⚔️ 군수 공장", f"{my_country['mil_factories']} 개")

st.divider()

# ----------------------------------------------------
# 4. 1차 세계대전 빈티지 스타일 지도의 구현 (Plotly)
# ----------------------------------------------------
st.subheader("🗺️ 1914년 유럽 전장 지도 (고전 고지도 스타일)")

country_colors = {
    "프랑스": "#1F4E79",          # 프렌치 블루
    "영국": "#A61C1C",            # 브리티시 레드
    "독일 제국": "#2E4053",        # 프로이센 회검정
    "오스트리아-헝가리": "#D4AC0D",  # 황제 옐로우
    "러시아 제국": "#4A235A",     # 제국 퍼플
    "이탈리아": "#196F3D"          # 사보이 그린
}

fig = go.Figure()

# 철도망 연결선 그리기 (주요 도시 연결)
railway_pairs = [
    ("파리 (수도)", "베르됭 (요새)"), ("파리 (수도)", "마르세유"), ("베를린 (수도)", "메스 (전선 요새)"),
    ("베를린 (수도)", "함부르크"), ("베를린 (수도)", "뮌헨"), ("빈 (수도)", "부다페스트"),
    ("빈 (수도)", "프라하"), ("상트페테르부르크 (수도)", "모스크바"), ("로마 (수도)", "밀라노")
]

for c1, c2 in railway_pairs:
    if c1 in st.session_state.cities and c2 in st.session_state.cities:
        lat1, lon1 = st.session_state.cities[c1]["lat"], st.session_state.cities[c1]["lon"]
        lat2, lon2 = st.session_state.cities[c2]["lat"], st.session_state.cities[c2]["lon"]
        fig.add_trace(go.Scattergeo(
            lat=[lat1, lat2],
            lon=[lon1, lon2],
            mode="lines",
            line=dict(width=1.5, color="#7B7D7D", dash="dash"),
            hoverinfo="none",
            showlegend=False
        ))

# 도시 마커 추가
for c_name, c_info in st.session_state.cities.items():
    g_text = "<br>".join([f"{k}: {v}" for k, v in c_info["garrison"].items() if v > 0])
    hover_content = f"<b>{c_name}</b><br>소유국: {c_info['owner']}<br>철도 연결: {'예' if c_info['railway'] else '아니오'}<br><br><b>주둔군:</b><br>{g_text if g_text else '없음'}"
    
    # 마커 모양 (수도는 별, 일반 도시는 원형)
    symbol_type = "star" if c_info["is_capital"] else "circle"
    marker_size = 16 if c_info["is_capital"] else 11
    
    fig.add_trace(go.Scattergeo(
        lat=[c_info["lat"]],
        lon=[c_info["lon"]],
        text=c_name,
        hoverinfo="text",
        hovertext=hover_content,
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=marker_size,
            color=country_colors.get(c_info["owner"], "#5D6D7E"),
            symbol=symbol_type,
            line=dict(width=1, color="#1C2833")
        ),
        name=c_info["owner"],
        showlegend=False
    ))

# 고지도 느낌(양피지/빈티지 톤) 스타일링
fig.update_geos(
    center=dict(lat=50, lon=15),
    lataxis_range=[36, 62],
    lonaxis_range=[-10, 38],
    showcountries=True,
    countrycolor="#85929E",
    showcoastlines=True,
    coastlinecolor="#5D6D7E",
    showland=True,
    landcolor="#EAECEE",      # 고지도 양피지 느낌의 연한 회갈색
    showocean=True,
    oceancolor="#D4E6F1",     # 고서화 스타일의 연한 파스텔 바다색
    projection_type="natural earth"
)

fig.update_layout(
    height=550,
    margin={"r":0, "t":10, "l":0, "b":0},
    paper_bgcolor="#F2F4F4"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 5. 재설계된 군사 양성 및 내정 시스템
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🪖 군사 훈련 및 양성", "🏭 공장 건설 & 내정", "⚔️ 전선 및 영토 정보"])

with tab1:
    st.subheader("🎖️ 병종별 군사 훈련소")
    
    # 자국 소유 도시만 필터링
    my_cities = [name for name, data in st.session_state.cities.items() if data["owner"] == selected_country]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        target_city_train = st.selectbox("군사를 배치할 도시 선택:", my_cities)
        unit_choice = st.selectbox("양성할 병종 선택:", list(UNIT_SPECS.keys()))
        unit_qty = st.slider("양성 수량 (개 사단/대대):", 1, 10, 1)
        
        spec = UNIT_SPECS[unit_choice]
        total_gold = spec["gold"] * unit_qty
        total_mp = spec["manpower"] * unit_qty
        total_sup = spec["supplies"] * unit_qty
        
        st.markdown(f"""
        **필요 자원:**
        - 💰 골드: `{total_gold}` G
        - 🪖 인력: `{total_mp}` 명
        - 📦 보급품: `{total_sup}` 톤
        """)
        
        if st.button("🚀 군사 모집 명령 하사"):
            if my_country["gold"] < total_gold:
                st.error("골드가 부족합니다!")
            elif my_country["manpower"] < total_mp:
                st.error("징집 인력이 부족합니다!")
            elif my_country["supplies"] < total_sup:
                st.error("보급품이 부족합니다!")
            else:
                # 자원 차감
                my_country["gold"] -= total_gold
                my_country["manpower"] -= total_mp
                my_country["supplies"] -= total_sup
                
                # 도시 주둔군 추가 (단순화된 형태: 보병/포병/기병/공군/해군 범주 매핑)
                category = unit_choice.split()[0] # '보병', '포병', '기병', '비행대대', '해군'
                if category == "비행대대": category = "공군"
                elif category == "해군": category = "해군"
                
                st.session_state.cities[target_city_train]["garrison"][category] += unit_qty
                st.success(f"{target_city_train}에 {unit_choice} {unit_qty}개가 성공적으로 훈련되어 주둔했습니다!")
                st.rerun()

    with c2:
        st.markdown("### 📋 병종 스펙 가이드")
        spec_df = pd.DataFrame.from_dict(UNIT_SPECS, orient="index")
        st.dataframe(spec_df[["gold", "manpower", "supplies", "attack", "defense"]], use_container_width=True)

with tab2:
    st.subheader("🏗️ 국가 산업 발전")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🏢 민간 공장 확충 (Cost: 100 Gold)")
        st.write("주간 Gold 생산량을 늘려줍니다.")
        if st.button("민간 공장 건설 (+1)"):
            if my_country["gold"] >= 100:
                my_country["gold"] -= 100
                my_country["civ_factories"] += 1
                st.success("민간 공장이 완공되었습니다.")
                st.rerun()
            else:
                st.error("골드가 부족합니다.")
                
    with col_b:
        st.markdown("#### 🔫 군수 공장 확충 (Cost: 100 Gold)")
        st.write("주간 보급품 생산량을 늘려줍니다.")
        if st.button("군수 공장 건설 (+1)"):
            if my_country["gold"] >= 100:
                my_country["gold"] -= 100
                my_country["mil_factories"] += 1
                st.success("군수 공장이 완공되었습니다.")
                st.rerun()
            else:
                st.error("골드가 부족합니다.")

with tab3:
    st.subheader("📊 유럽 전체 도시 현황 판")
    city_summary = []
    for c_name, c_info in st.session_state.cities.items():
        gar = c_info["garrison"]
        total_army = gar["보병"] + gar["포병"] + gar["기병"]
        city_summary.append({
            "도시명": c_name,
            "소유국": c_info["owner"],
            "철도": "O" if c_info["railway"] else "X",
            "민간공장": c_info["civ"],
            "군공장": c_info["mil"],
            "육군": total_army,
            "공군": gar["공군"],
            "해군": gar["해군"]
        })
    st.dataframe(pd.DataFrame(city_summary), use_container_width=True)

# 10초 실시간 주기 보장을 위한 리런
time.sleep(1)
st.rerun()
