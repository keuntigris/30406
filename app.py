import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="1차 세계대전 대전략", layout="wide")

# ----------------------------------------------------
# 1. 게임 데이터 초기화 (확장된 도시 및 병종 데이터)
# ----------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    st.session_state.battle_animation = None
    st.session_state.battle_logs = []
    
    st.session_state.countries = {
        "프랑스": {"faction": "협상국", "color": "#1F4E79", "gold": 800, "pop": 39000, "manpower": 300, "supplies": 400, "civ_factories": 10, "mil_factories": 6},
        "영국": {"faction": "협상국", "color": "#C0392B", "gold": 1000, "pop": 45000, "manpower": 350, "supplies": 500, "civ_factories": 12, "mil_factories": 8},
        "러시아 제국": {"faction": "협상국", "color": "#7D3C98", "gold": 500, "pop": 170000, "manpower": 1000, "supplies": 300, "civ_factories": 7, "mil_factories": 5},
        "이탈리아": {"faction": "협상국", "color": "#27AE60", "gold": 450, "pop": 35000, "manpower": 200, "supplies": 250, "civ_factories": 6, "mil_factories": 4},
        "독일 제국": {"faction": "동맹국", "color": "#2C3E50", "gold": 900, "pop": 67000, "manpower": 500, "supplies": 600, "civ_factories": 14, "mil_factories": 10},
        "오스트리아-헝가리": {"faction": "동맹국", "color": "#D4AC0D", "gold": 600, "pop": 52000, "manpower": 350, "supplies": 350, "civ_factories": 8, "mil_factories": 5},
        "오스만 제국": {"faction": "동맹국", "color": "#E67E22", "gold": 400, "pop": 21000, "manpower": 250, "supplies": 200, "civ_factories": 5, "mil_factories": 3},
    }
    
    # 유럽 전역 20개 주요 도시 데이터
    st.session_state.cities = {
        # 프랑스
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "morale": 100, "civ": 4, "mil": 2, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5}},
        "베르됭": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "railway": True, "morale": 100, "civ": 1, "mil": 2, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2}},
        "마르세유": {"lat": 43.2965, "lon": 5.3698, "owner": "프랑스", "railway": True, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        "리용": {"lat": 45.7640, "lon": 4.8357, "owner": "프랑스", "railway": False, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0}},
        
        # 영국
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "morale": 100, "civ": 5, "mil": 3, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10}},
        "맨체스터": {"lat": 53.4808, "lon": -2.2426, "owner": "영국", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0}},
        "에든버러": {"lat": 55.9533, "lon": -3.1883, "owner": "영국", "railway": False, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 10, "포병": 0, "기병": 2, "공군": 0}},
        
        # 독일 제국
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 5, "mil": 4, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10}},
        "메스": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 1, "mil": 2, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5}},
        "함부르크": {"lat": 53.5511, "lon": 9.9937, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 15, "포병": 5, "기병": 0, "공군": 0}},
        "뮌헨": {"lat": 48.1351, "lon": 11.5820, "owner": "독일 제국", "railway": False, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 15, "포병": 5, "기병": 5, "공군": 0}},
        
        # 오스트리아-헝가리
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 4, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2}},
        "부다페스트": {"lat": 47.4979, "lon": 19.0402, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0}},
        "프라하": {"lat": 50.0755, "lon": 14.4378, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 10, "포병": 5, "기병": 0, "공군": 0}},
        "사라예보": {"lat": 43.8563, "lon": 18.4131, "owner": "오스트리아-헝가리", "railway": False, "morale": 85, "civ": 1, "mil": 0, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        
        # 러시아 제국
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2}},
        "모스크바": {"lat": 55.7558, "lon": 37.6173, "owner": "러시아 제국", "railway": True, "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 30, "포병": 5, "기병": 10, "공군": 0}},
        "바르샤바": {"lat": 52.2297, "lon": 21.0122, "owner": "러시아 제국", "railway": False, "morale": 85, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
        
        # 이탈리아 & 오스만
        "로마": {"lat": 41.9028, "lon": 12.4964, "owner": "이탈리아", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 2}},
        "이스탄불": {"lat": 41.0082, "lon": 28.9784, "owner": "오스만 제국", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
    }
    st.session_state.player_country = "프랑스"

# 병종별 요구 자원 스펙
UNIT_SPECS = {
    "보병": {"gold": 30, "manpower": 50, "supplies": 20, "atk": 20, "def": 30},
    "포병": {"gold": 80, "manpower": 20, "supplies": 60, "atk": 50, "def": 10},
    "기병": {"gold": 50, "manpower": 30, "supplies": 30, "atk": 25, "def": 15},
    "공군": {"gold": 120, "manpower": 10, "supplies": 80, "atk": 60, "def": 5},
}

# ----------------------------------------------------
# 2. 타이머 연동 (10초 = 1주)
# ----------------------------------------------------
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    for c_name, c_data in st.session_state.countries.items():
        c_data["gold"] += c_data["civ_factories"] * 25
        c_data["manpower"] += int(c_data["pop"] * 0.002)
        c_data["supplies"] += c_data["mil_factories"] * 20

# ----------------------------------------------------
# 3. UI 및 헤더
# ----------------------------------------------------
st.title("⚔️ 1차 세계대전 대전략 - 확장 전장")

selected_country = st.sidebar.selectbox(
    "플레이할 국가 선택:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country
my_country = st.session_state.countries[selected_country]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("진영", my_country["faction"])
c2.metric("골드", f"{my_country['gold']} G")
c3.metric("인력", f"{my_country['manpower']} 명")
c4.metric("보급품", f"{my_country['supplies']} 톤")
c5.metric("공장(민/군)", f"{my_country['civ_factories']} / {my_country['mil_factories']}")

# ----------------------------------------------------
# 4. 유럽 전장 지도 시각화
# ----------------------------------------------------
st.subheader("🗺️ 1914 유럽 전장 지도 (20개 주요 도시)")

fig = go.Figure()

for c_name, c_info in st.session_state.cities.items():
    owner_country = c_info["owner"]
    country_color = st.session_state.countries[owner_country]["color"]
    gar = c_info["garrison"]
    total_army = gar["보병"] + gar["포병"] + gar["기병"]
    
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
        marker=dict(size=13, color=country_color, line=dict(width=1, color="#000000")),
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
        line=dict(width=3, color="#E74C3C", dash="dash"),
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

# ----------------------------------------------------
# 5. 전장 명령 & 개편된 군대 양성 시스템
# ----------------------------------------------------
st.divider()
st.subheader("🛠️ 군사 및 내정 관리")

tab_train, tab_attack, tab_air = st.tabs(["🎖️ 군대 양성", "⚔️ 육군 진격/전투", "✈️ 공군 포격"])

# 자국 소유 도시 목록
my_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country]
target_cities = [k for k, v in st.session_state.cities.items() if v["owner"] != selected_country]

with tab_train:
    st.markdown("### 🪖 도시별 군대 양성 훈련소")
    if not my_cities:
        st.error("소유한 도시가 없어 병력을 양성할 수 없습니다.")
    else:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            train_city = st.selectbox("병력을 모병 및 배치할 도시:", my_cities)
            unit_type = st.selectbox("양성할 병종:", list(UNIT_SPECS.keys()))
            unit_count = st.slider("양성 수량:", 1, 10, 1)
            
            spec = UNIT_SPECS[unit_type]
            req_gold = spec["gold"] * unit_count
            req_mp = spec["manpower"] * unit_count
            req_sup = spec["supplies"] * unit_count
            
            st.markdown(f"""
            **필요 자원:**
            - 💰 골드: `{req_gold}` G
            - 🪖 인력: `{req_mp}` 명
            - 📦 보급품: `{req_sup}` 톤
            """)
            
            if st.button("🚀 군대 훈련 및 배치 명령"):
                if my_country["gold"] < req_gold:
                    st.error("골드가 부족합니다!")
                elif my_country["manpower"] < req_mp:
                    st.error("인력이 부족합니다!")
                elif my_country["supplies"] < req_sup:
                    st.error("보급품이 부족합니다!")
                else:
                    # 자원 차감 및 병력 충원
                    my_country["gold"] -= req_gold
                    my_country["manpower"] -= req_mp
                    my_country["supplies"] -= req_sup
                    
                    st.session_state.cities[train_city]["garrison"][unit_type] += unit_count
                    st.success(f"{train_city}에 {unit_type} {unit_count}기 훈련을 완료했습니다!")
                    st.rerun()

        with col_t2:
            st.markdown("### 📋 병종 정보")
            spec_df = pd.DataFrame.from_dict(UNIT_SPECS, orient="index")
            st.dataframe(spec_df[["gold", "manpower", "supplies", "atk", "def"]], use_container_width=True)

with tab_attack:
    col_a, col_b = st.columns(2)
    with col_a:
        from_city = st.selectbox("출발 도시:", my_cities if my_cities else ["없음"])
    with col_b:
        to_city = st.selectbox("공격 목표 도시:", target_cities)

    if st.button("⚔️ 공격 개시"):
        if not my_cities:
            st.error("소유 도시가 없습니다.")
        else:
            att_city = st.session_state.cities[from_city]
            def_city = st.session_state.cities[to_city]
            def_owner = def_city["owner"]
            def_faction = st.session_state.countries[def_owner]["faction"]
            
            if def_faction == my_country["faction"]:
                st.warning("같은 진영 국가의 영토는 공격할 수 없습니다.")
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
                    def_city["owner"] = selected_country
                    def_city["garrison"]["보병"] = int(att_gar["보병"] * 0.4)
                    att_gar["보병"] -= def_city["garrison"]["보병"]
                    st.success(f"🎉 {to_city}를 점령했습니다!")
                else:
                    st.error(f"💥 {to_city} 공격 실패! 후퇴했습니다.")
                st.rerun()

with tab_air:
    air_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country and v["garrison"]["공군"] > 0]
    air_from = st.selectbox("발진 도시:", air_cities if air_cities else ["공군 없음"])
    air_target = st.selectbox("목표 도시:", target_cities)
    
    if st.button("💣 공습 개시"):
        if air_from == "공군 없음":
            st.error("공군이 있는 도시가 없습니다.")
        else:
            target = st.session_state.cities[air_target]
            target["garrison"]["보병"] = max(0, target["garrison"]["보병"] - random.randint(3, 8))
            target["morale"] = max(10, target["morale"] - 20)
            st.warning(f"💥 {air_target} 공습 완료!")
            st.rerun()

time.sleep(1)
st.rerun()
