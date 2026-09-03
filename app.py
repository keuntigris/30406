import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random
import math

st.set_page_config(page_title="1차 세계대전 대전략", layout="wide")

# ----------------------------------------------------
# 0. 거리 계산 함수 (Haversine 공식)
# ----------------------------------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

MAX_ATTACK_DISTANCE = 650  # 도로 연결 및 이동 가능 최대 거리 (km)

UNIT_SPECS = {
    "보병": {"gold": 30, "manpower": 50, "supplies": 20, "atk": 20, "def": 30},
    "포병": {"gold": 80, "manpower": 20, "supplies": 60, "atk": 50, "def": 10},
    "기병": {"gold": 50, "manpower": 30, "supplies": 30, "atk": 25, "def": 15},
    "공군": {"gold": 120, "manpower": 10, "supplies": 80, "atk": 60, "def": 5},
}

# ----------------------------------------------------
# 1. 게임 데이터 초기화
# ----------------------------------------------------
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.week = 1
    st.session_state.battle_animation = None
    st.session_state.battle_logs = []
    
    st.session_state.countries = {
        "프랑스": {"faction": "협상국", "color": "#1F4E79", "gold": 1200, "pop": 39000, "manpower": 400, "supplies": 500, "civ_factories": 15, "mil_factories": 10},
        "영국": {"faction": "협상국", "color": "#C0392B", "gold": 1500, "pop": 45000, "manpower": 450, "supplies": 600, "civ_factories": 18, "mil_factories": 12},
        "러시아 제국": {"faction": "협상국", "color": "#7D3C98", "gold": 800, "pop": 170000, "manpower": 1200, "supplies": 450, "civ_factories": 12, "mil_factories": 8},
        "이탈리아": {"faction": "협상국", "color": "#27AE60", "gold": 600, "pop": 35000, "manpower": 300, "supplies": 300, "civ_factories": 9, "mil_factories": 6},
        "독일 제국": {"faction": "동맹국", "color": "#2C3E50", "gold": 1400, "pop": 67000, "manpower": 700, "supplies": 800, "civ_factories": 20, "mil_factories": 15},
        "오스트리아-헝가리": {"faction": "동맹국", "color": "#D4AC0D", "gold": 800, "pop": 52000, "manpower": 500, "supplies": 450, "civ_factories": 12, "mil_factories": 8},
        "오스만 제국": {"faction": "동맹국", "color": "#E67E22", "gold": 500, "pop": 21000, "manpower": 300, "supplies": 250, "civ_factories": 7, "mil_factories": 4},
    }
    
    st.session_state.cities = {
        # 프랑스
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "morale": 100, "civ": 4, "mil": 2, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5}},
        "베르됭": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "morale": 100, "civ": 1, "mil": 2, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2}},
        "마르세유": {"lat": 43.2965, "lon": 5.3698, "owner": "프랑스", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        "리용": {"lat": 45.7640, "lon": 4.8357, "owner": "프랑스", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0}},
        "보르도": {"lat": 44.8378, "lon": -0.5792, "owner": "프랑스", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 10, "포병": 2, "기병": 2, "공군": 0}},
        "릴": {"lat": 50.6292, "lon": 3.0573, "owner": "프랑스", "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 20, "포병": 8, "기병": 0, "공군": 0}},

        # 영국
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "morale": 100, "civ": 5, "mil": 3, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10}},
        "맨체스터": {"lat": 53.4808, "lon": -2.2426, "owner": "영국", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0}},
        "에든버러": {"lat": 55.9533, "lon": -3.1883, "owner": "영국", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 10, "포병": 0, "기병": 2, "공군": 0}},
        "칼레 (영국 통제)": {"lat": 50.9513, "lon": 1.8587, "owner": "영국", "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 2}},

        # 독일 제국
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "morale": 100, "civ": 5, "mil": 4, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10}},
        "메스": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "morale": 100, "civ": 1, "mil": 2, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5}},
        "함부르크": {"lat": 53.5511, "lon": 9.9937, "owner": "독일 제국", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0}},
        "뮌헨": {"lat": 48.1351, "lon": 11.5820, "owner": "독일 제국", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 5, "공군": 0}},
        "쾰른": {"lat": 50.9375, "lon": 6.9603, "owner": "독일 제국", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 20, "포병": 10, "기병": 2, "공군": 0}},
        "쾨니히스베르크": {"lat": 54.7104, "lon": 20.4522, "owner": "독일 제국", "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},

        # 오스트리아-헝가리
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "morale": 100, "civ": 4, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2}},
        "부다페스트": {"lat": 47.4979, "lon": 19.0402, "owner": "오스트리아-헝가리", "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0}},
        "프라하": {"lat": 50.0755, "lon": 14.4378, "owner": "오스트리아-헝가리", "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0}},
        "사라예보": {"lat": 43.8563, "lon": 18.4131, "owner": "오스트리아-헝가리", "morale": 85, "civ": 1, "mil": 0, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        "트리에스테": {"lat": 45.6495, "lon": 13.7768, "owner": "오스트리아-헝가리", "morale": 90, "civ": 2, "mil": 1, "garrison": {"보병": 12, "포병": 4, "기병": 0, "공군": 0}},
        "크라쿠프": {"lat": 50.0647, "lon": 19.9450, "owner": "오스트리아-헝가리", "morale": 95, "civ": 1, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 3, "공군": 0}},

        # 러시아 제국
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2}},
        "모스크바": {"lat": 55.7558, "lon": 37.6173, "owner": "러시아 제국", "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 30, "포병": 5, "기병": 10, "공군": 0}},
        "바르샤바": {"lat": 52.2297, "lon": 21.0122, "owner": "러시아 제국", "morale": 85, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
        "키예프": {"lat": 50.4501, "lon": 30.5234, "owner": "러시아 제국", "morale": 95, "civ": 2, "mil": 1, "garrison": {"보병": 20, "포병": 5, "기병": 8, "공군": 0}},
        "민스크": {"lat": 53.9006, "lon": 27.5590, "owner": "러시아 제국", "morale": 90, "civ": 1, "mil": 1, "garrison": {"보병": 18, "포병": 4, "기병": 4, "공군": 0}},

        # 이탈리아
        "로마": {"lat": 41.9028, "lon": 12.4964, "owner": "이탈리아", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 2}},
        "밀라노": {"lat": 45.4642, "lon": 9.1900, "owner": "이탈리아", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 18, "포병": 6, "기병": 2, "공군": 0}},
        "베네치아": {"lat": 45.4408, "lon": 12.3155, "owner": "이탈리아", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 4, "기병": 0, "공군": 0}},

        # 오스만 제국
        "이스탄불": {"lat": 41.0082, "lon": 28.9784, "owner": "오스만 제국", "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
        "앙카라": {"lat": 39.9334, "lon": 32.8597, "owner": "오스만 제국", "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 5, "공군": 0}},
    }
    st.session_state.player_country = "프랑스"

# ----------------------------------------------------
# 2. AI 동작 함수
# ----------------------------------------------------
def process_ai_turn():
    st.session_state.week += 1
    
    # 1) 전체 자원 생산
    for c_name, c_data in st.session_state.countries.items():
        c_data["gold"] += c_data["civ_factories"] * 25
        c_data["manpower"] += int(c_data["pop"] * 0.002)
        c_data["supplies"] += c_data["mil_factories"] * 20

    # 2) AI 제어 (플레이어 이외 국가)
    ai_countries = [c for c in st.session_state.countries.keys() if c != st.session_state.player_country]
    
    for country_name in ai_countries:
        c_data = st.session_state.countries[country_name]
        ai_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == country_name]
        
        if not ai_cities:
            continue

        # AI 병력 생산
        for unit, u_spec in UNIT_SPECS.items():
            if c_data["gold"] >= u_spec["gold"] * 2 and c_data["manpower"] >= u_spec["manpower"] * 2 and c_data["supplies"] >= u_spec["supplies"] * 2:
                c_data["gold"] -= u_spec["gold"] * 2
                c_data["manpower"] -= u_spec["manpower"] * 2
                c_data["supplies"] -= u_spec["supplies"] * 2
                target_c = random.choice(ai_cities)
                st.session_state.cities[target_c]["garrison"][unit] += 2
                break

        # AI 공격 시도
        if random.random() < 0.4:
            from_city_name = random.choice(ai_cities)
            from_c = st.session_state.cities[from_city_name]
            
            # 공격 대상 선정
            possible_targets = []
            for t_name, t_info in st.session_state.cities.items():
                if t_info["owner"] != country_name:
                    target_faction = st.session_state.countries[t_info["owner"]]["faction"]
                    if target_faction != c_data["faction"]:
                        dist = calculate_distance(from_c["lat"], from_c["lon"], t_info["lat"], t_info["lon"])
                        if dist <= MAX_ATTACK_DISTANCE:
                            possible_targets.append(t_name)
            
            if possible_targets:
                target_city_name = random.choice(possible_targets)
                def_c = st.session_state.cities[target_city_name]
                
                att_power = (from_c["garrison"]["보병"]*20 + from_c["garrison"]["포병"]*50) * (from_c["morale"]/100.0)
                def_power = (def_c["garrison"]["보병"]*30 + def_c["garrison"]["포병"]*10) * (def_c["morale"]/100.0)
                
                if att_power > def_power * 1.2:
                    def_c["owner"] = country_name
                    def_c["garrison"]["보병"] = max(5, int(from_c["garrison"]["보병"] * 0.3))
                    st.session_state.battle_logs.append(f"⚔️ {country_name}이(가) {target_city_name}을(를) 점령했습니다!")

# ----------------------------------------------------
# 3. 게임 시작 선택 화면 (초기 진입)
# ----------------------------------------------------
if not st.session_state.game_started:
    st.title("⚔️ 1차 세계대전 대전략 - 국가 선택")
    st.markdown("---")
    st.subheader("운영할 국가를 선택하고 대전략 게임을 시작하세요.")
    
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        selected_player = st.selectbox(
            "플레이할 국가 선택:",
            list(st.session_state.countries.keys())
        )
        if st.button("🎮 게임 시작", use_container_width=True):
            st.session_state.player_country = selected_player
            st.session_state.game_started = True
            st.rerun()

    with col_info:
        c_info = st.session_state.countries[selected_player]
        st.markdown(f"### {selected_player}")
        st.markdown(f"- **소속 진영:** {c_info['faction']}")
        st.markdown(f"- **초기 골드:** {c_info['gold']} G")
        st.markdown(f"- **인구 수:** {c_info['pop']:,} 명")
        st.markdown(f"- **민간 / 군수 공장:** {c_info['civ_factories']}개 / {c_info['mil_factories']}개")
        
        player_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_player]
        st.markdown(f"- **보유 도시 ({len(player_cities)}개):** {', '.join(player_cities)}")

else:
    # ----------------------------------------------------
    # 4. 메인 게임 화면
    # ----------------------------------------------------
    st.sidebar.title("🚩 국가 정보")
    st.sidebar.markdown(f"**플레이어 국가:** {st.session_state.player_country}")
    
    if st.sidebar.button("🔄 주차 진행 (AI 턴 동시 진행)", use_container_width=True):
        process_ai_turn()
        st.rerun()
        
    if st.sidebar.button("🏳️ 국가 다시 선택하기"):
        st.session_state.game_started = False
        st.rerun()

    my_country = st.session_state.countries[st.session_state.player_country]

    st.title(f"⚔️ 1차 세계대전 대전략 - {st.session_state.player_country}")
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("현재 주차", f"{st.session_state.week} 주차")
    m2.metric("진영", my_country["faction"])
    m3.metric("골드", f"{my_country['gold']} G")
    m4.metric("인력", f"{my_country['manpower']} 명")
    m5.metric("보급품", f"{my_country['supplies']} 톤")
    m6.metric("공장(민/군)", f"{my_country['civ_factories']} / {my_country['mil_factories']}")

    # ----------------------------------------------------
    # 5. 지도 시각화
    # ----------------------------------------------------
    st.subheader("🗺️ 1914 유럽 전장 지도")

    fig = go.Figure()

    city_list = list(st.session_state.cities.items())
    road_lats = []
    road_lons = []

    for i in range(len(city_list)):
        for j in range(i + 1, len(city_list)):
            c1_name, c1_info = city_list[i]
            c2_name, c2_info = city_list[j]
            
            dist = calculate_distance(c1_info["lat"], c1_info["lon"], c2_info["lat"], c2_info["lon"])
            if dist <= MAX_ATTACK_DISTANCE:
                road_lats.extend([c1_info["lat"], c2_info["lat"], None])
                road_lons.extend([c1_info["lon"], c2_info["lon"], None])

    fig.add_trace(go.Scattergeo(
        lat=road_lats,
        lon=road_lons,
        mode="lines",
        line=dict(width=1.2, color="#95A5A6"),
        hoverinfo="none",
        showlegend=False
    ))

    for c_name, c_info in st.session_state.cities.items():
        owner_country = c_info["owner"]
        country_color = st.session_state.countries[owner_country]["color"]
        gar = c_info["garrison"]
        
        hover_text = (
            f"<b>{c_name}</b> ({owner_country})<br>"
            f"사기: {c_info['morale']}%<br>"
            f"<b>주둔 병력:</b> 보병 {gar['보병']} | 포병 {gar['포병']} | 기병 {gar['기병']} | 공군 {gar['공군']}"
        )
        
        fig.add_trace(go.Scattergeo(
            lat=[c_info["lat"]],
            lon=[c_info["lon"]],
            text=c_name,
            hoverinfo="text",
            hovertext=hover_text,
            mode="markers+text",
            textposition="top center",
            marker=dict(size=12, color=country_color, line=dict(width=1, color="#000000")),
            showlegend=False
        ))

    if st.session_state.battle_animation:
        anim = st.session_state.battle_animation
        from_c = st.session_state.cities[anim["from"]]
        to_c = st.session_state.cities[anim["to"]]
        
        fig.add_trace(go.Scattergeo(
            lat=[from_c["lat"], to_c["lat"]],
            lon=[from_c["lon"], to_c["lon"]],
            mode="lines",
            line=dict(width=3.5, color="#E74C3C", dash="dash"),
            showlegend=False
        ))
        fig.add_trace(go.Scattergeo(
            lat=[to_c["lat"]],
            lon=[to_c["lon"]],
            mode="text",
            text=["💥"],
            textfont=dict(size=26),
            hoverinfo="none",
            showlegend=False
        ))

    fig.update_geos(
        center=dict(lat=50, lon=15),
        lataxis_range=[35, 63],
        lonaxis_range=[-10, 40],
        showcountries=True,
        countrycolor="#BDC3C7",
        showland=True,
        landcolor="#EAEDED",
        showocean=True,
        oceancolor="#EBF5FB",
        projection_type="natural earth"
    )
    fig.update_layout(height=480, margin={"r":0, "t":10, "l":0, "b":0})
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.battle_logs:
        with st.expander("📜 최근 AI 전황 로그"):
            for log in st.session_state.battle_logs[-5:]:
                st.write(log)

    # ----------------------------------------------------
    # 6. 전투 및 내정 탭
    # ----------------------------------------------------
    st.divider()
    st.subheader("🛠️ 군사 및 내정 관리")

    tab_train, tab_attack, tab_air = st.tabs(["🎖️ 군대 양성", "⚔️ 도로 연계 진격", "✈️ 공군 포격"])

    my_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == st.session_state.player_country]

    with tab_train:
        st.markdown("### 🪖 도시별 군대 양성")
        if not my_cities:
            st.error("소유한 도시가 없습니다.")
        else:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                train_city = st.selectbox("병력 배치 도시:", my_cities)
                unit_type = st.selectbox("양성 병종:", list(UNIT_SPECS.keys()))
                unit_count = st.slider("양성 수량:", 1, 10, 1)
                
                spec = UNIT_SPECS[unit_type]
                req_gold = spec["gold"] * unit_count
                req_mp = spec["manpower"] * unit_count
                req_sup = spec["supplies"] * unit_count
                
                st.markdown(f"**필요 자원:** 💰 {req_gold} G | 🪖 {req_mp} 명 | 📦 {req_sup} 톤")
                
                if st.button("🚀 군대 훈련 및 배치"):
                    if my_country["gold"] >= req_gold and my_country["manpower"] >= req_mp and my_country["supplies"] >= req_sup:
                        my_country["gold"] -= req_gold
                        my_country["manpower"] -= req_mp
                        my_country["supplies"] -= req_sup
                        st.session_state.cities[train_city]["garrison"][unit_type] += unit_count
                        st.success(f"{train_city}에 {unit_type} {unit_count}기 충원 완료!")
                        st.rerun()
                    else:
                        st.error("자원이 부족합니다!")
            with col_t2:
                st.dataframe(pd.DataFrame.from_dict(UNIT_SPECS, orient="index")[["gold", "manpower", "supplies", "atk", "def"]], use_container_width=True)

    with tab_attack:
        st.markdown("### ⚔️ 연결된 도로를 통한 진격")
        if not my_cities:
            st.error("소유한 도시가 없습니다.")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                from_city = st.selectbox("출발 도시 선택:", my_cities)
            
            from_coords = st.session_state.cities[from_city]
            
            nearby_targets = []
            for target_name, target_info in st.session_state.cities.items():
                if target_info["owner"] != st.session_state.player_country:
                    dist = calculate_distance(
                        from_coords["lat"], from_coords["lon"],
                        target_info["lat"], target_info["lon"]
                    )
                    if dist <= MAX_ATTACK_DISTANCE:
                        nearby_targets.append((target_name, dist))
            
            with col_b:
                if nearby_targets:
                    nearby_targets.sort(key=lambda x: x[1])
                    target_options = [f"{t[0]} ({int(t[1])} km)" for t in nearby_targets]
                    selected_target_str = st.selectbox("도로로 연결된 적 도시:", target_options)
                    to_city = selected_target_str.split(" (")[0]
                else:
                    st.selectbox("목표 도시:", ["도로로 연결된 적 도시 없음"])
                    to_city = None

            if st.button("⚔️ 도로 타고 공격 개시"):
                if not to_city:
                    st.error("진격할 수 있는 도로 연결 도시가 없습니다.")
                else:
                    att_city = st.session_state.cities[from_city]
                    def_city = st.session_state.cities[to_city]
                    def_owner = def_city["owner"]
                    def_faction = st.session_state.countries[def_owner]["faction"]
                    
                    if def_faction == my_country["faction"]:
                        st.warning("동맹국 영토는 공격할 수 없습니다.")
                    else:
                        st.session_state.battle_animation = {"from": from_city, "to": to_city}
                        att_gar = att_city["garrison"]
                        def_gar = def_city["garrison"]
                        
                        att_power = (att_gar["보병"]*20 + att_gar["포병"]*50 + att_gar["기병"]*25) * (att_city["morale"]/100.0)
                        def_power = (def_gar["보병"]*30 + def_gar["포병"]*10 + def_gar["기병"]*15) * (def_city["morale"]/100.0)
                        
                        att_loss_rate = min(0.7, (def_power / (att_power + 1)) * 0.4 + 0.1)
                        def_loss_rate = min(0.7, (att_power / (def_power + 1)) * 0.4 + 0.1)
                        
                        for unit in ["보병", "포병", "기병"]:
                            att_gar[unit] = max(0, att_gar[unit] - int(att_gar[unit] * att_loss_rate))
                            def_gar[unit] = max(0, def_gar[unit] - int(def_gar[unit] * def_loss_rate))
                        
                        att_city["morale"] = max(10, att_city["morale"] - 15)
                        def_city["morale"] = max(10, def_city["morale"] - 15)
                        
                        if att_power > def_power:
                            def_city["owner"] = st.session_state.player_country
                            def_city["garrison"]["보병"] = int(att_gar["보병"] * 0.4)
                            att_gar["보병"] -= def_city["garrison"]["보병"]
                            st.success(f"🎉 {to_city}를 점령했습니다!")
                        else:
                            st.error(f"💥 {to_city} 공격 실패! 후퇴했습니다.")
                        st.rerun()

    with tab_air:
        st.markdown("### ✈️ 공군 포격")
        air_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == st.session_state.player_country and v["garrison"]["공군"] > 0]
        all_targets = [k for k, v in st.session_state.cities.items() if v["owner"] != st.session_state.player_country]
        
        air_from = st.selectbox("발진 도시:", air_cities if air_cities else ["공군 없음"])
        air_target = st.selectbox("공습 목표 도시:", all_targets)
        
        if st.button("💣 공습 개시"):
            if air_from == "공군 없음":
                st.error("공군이 주둔한 도시가 없습니다.")
            else:
                target = st.session_state.cities[air_target]
                target["garrison"]["보병"] = max(0, target["garrison"]["보병"] - random.randint(3, 8))
                target["morale"] = max(10, target["morale"] - 20)
                st.warning(f"💥 {air_target} 공습 완료!")
                st.rerun()
