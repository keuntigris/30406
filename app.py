import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="1차 세계대전 대전략", layout="wide")

# ----------------------------------------------------
# 1. 게임 데이터 초기화 (국가별 고유 색상 설정)
# ----------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    st.session_state.war_status = True
    
    # 국가별 고유 색상 및 세부 정보
    st.session_state.countries = {
        # 협상국 (Allied Powers)
        "프랑스": {"faction": "협상국", "color": "#1F4E79", "gold": 600, "pop": 39000, "manpower": 200, "supplies": 300, "civ_factories": 8, "mil_factories": 5},
        "영국": {"faction": "협상국", "color": "#C0392B", "gold": 800, "pop": 45000, "manpower": 220, "supplies": 400, "civ_factories": 10, "mil_factories": 6},
        "러시아 제국": {"faction": "협상국", "color": "#7D3C98", "gold": 400, "pop": 170000, "manpower": 800, "supplies": 200, "civ_factories": 5, "mil_factories": 4},
        "이탈리아": {"faction": "협상국", "color": "#27AE60", "gold": 350, "pop": 35000, "manpower": 150, "supplies": 180, "civ_factories": 5, "mil_factories": 3},
        "세르비아": {"faction": "협상국", "color": "#2980B9", "gold": 200, "pop": 4500, "manpower": 80, "supplies": 100, "civ_factories": 2, "mil_factories": 1},
        
        # 동맹국 (Central Powers)
        "독일 제국": {"faction": "동맹국", "color": "#2C3E50", "gold": 750, "pop": 67000, "manpower": 350, "supplies": 450, "civ_factories": 11, "mil_factories": 8},
        "오스트리아-헝가리": {"faction": "동맹국", "color": "#D4AC0D", "gold": 450, "pop": 52000, "manpower": 250, "supplies": 250, "civ_factories": 6, "mil_factories": 4},
        "오스만 제국": {"faction": "동맹국", "color": "#E67E22", "gold": 300, "pop": 21000, "manpower": 180, "supplies": 150, "civ_factories": 4, "mil_factories": 2},
        "불가리아": {"faction": "동맹국", "color": "#A04000", "gold": 200, "pop": 5500, "manpower": 90, "supplies": 100, "civ_factories": 2, "mil_factories": 1},
        
        # 중립국 (Neutral Powers)
        "스페인": {"faction": "중립국", "color": "#F39C12", "gold": 400, "pop": 20000, "manpower": 100, "supplies": 100, "civ_factories": 4, "mil_factories": 1},
        "스위스": {"faction": "중립국", "color": "#BDC3C7", "gold": 500, "pop": 3800, "manpower": 50, "supplies": 100, "civ_factories": 5, "mil_factories": 1},
    }
    
    # 주요 도시 정보
    st.session_state.cities = {
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5}},
        "베르됭": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2}},
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10}},
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10}},
        "메스": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5}},
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2}},
        "사라예보": {"lat": 43.8563, "lon": 18.4131, "owner": "오스트리아-헝가리", "railway": False, "morale": 90, "civ": 1, "mil": 0, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2}},
        "바르샤바": {"lat": 52.2297, "lon": 21.0122, "owner": "러시아 제국", "railway": False, "morale": 85, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
        "이스탄불": {"lat": 41.0082, "lon": 28.9784, "owner": "오스만 제국", "railway": True, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0}},
        "마드리드": {"lat": 40.4168, "lon": -3.7038, "owner": "스페인", "railway": True, "morale": 100, "civ": 2, "mil": 0, "garrison": {"보병": 10, "포병": 0, "기병": 0, "공군": 0}},
    }
    st.session_state.player_country = "프랑스"

UNIT_SPECS = {
    "보병": {"gold": 30, "manpower": 50, "supplies": 20},
    "포병": {"gold": 80, "manpower": 20, "supplies": 60},
    "기병": {"gold": 50, "manpower": 30, "supplies": 30},
    "공군": {"gold": 120, "manpower": 10, "supplies": 80},
}

# ----------------------------------------------------
# 2. 타이머 & 주간 루프 (10초 = 1주)
# ----------------------------------------------------
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    
    for c_name, c_data in st.session_state.countries.items():
        c_data["gold"] += c_data["civ_factories"] * 25
        c_data["manpower"] += int(c_data["pop"] * 0.002)
        c_data["supplies"] += c_data["mil_factories"] * 20
        
    for city_name, city_info in st.session_state.cities.items():
        city_info["morale"] = min(100, city_info["morale"] + 2)

# ----------------------------------------------------
# 3. UI 및 헤더
# ----------------------------------------------------
st.title("⚔️ 1차 세계대전 대전략")
st.error("🔥 **[전쟁 진행 중]** 협상국 vs 동맹국 전면전")

selected_country = st.sidebar.selectbox(
    "플레이할 국가 선택:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country

my_country = st.session_state.countries[selected_country]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("소속 진영", my_country["faction"])
col2.metric("골드", f"{my_country['gold']} G")
col3.metric("인력", f"{my_country['manpower']} 명")
col4.metric("보급품", f"{my_country['supplies']} 톤")
col5.metric("공장(민/군)", f"{my_country['civ_factories']} / {my_country['mil_factories']}")

# ----------------------------------------------------
# 4. 지도 시각화 (국가별 고유 색상 적용)
# ----------------------------------------------------
st.subheader("🗺️ 1914 유럽 전장 지도")

fig = go.Figure()

for c_name, c_info in st.session_state.cities.items():
    owner_country = c_info["owner"]
    # 국가 고유 색상 불러오기
    country_color = st.session_state.countries[owner_country]["color"]
    faction = st.session_state.countries[owner_country]["faction"]
    
    gar = c_info["garrison"]
    total_army = gar["보병"] + gar["포병"] + gar["기병"]
    
    hover_text = (
        f"<b>{c_name}</b><br>"
        f"소유국: {owner_country} ({faction})<br>"
        f"사기: {c_info['morale']}%<br>"
        f"철도: {'있음' if c_info['railway'] else '없음 (보급 감소)'}<br>"
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
        marker=dict(
            size=15,
            color=country_color,
            line=dict(width=1.5, color="#000000")
        ),
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

fig.update_layout(height=500, margin={"r":0, "t":10, "l":0, "b":0})
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 5. 전투 및 군사 소모 시스템
# ----------------------------------------------------
st.divider()
st.subheader("⚔️ 전투 및 전략 명령")

tab_attack, tab_air, tab_train = st.tabs(["🪖 육군 진격/전투", "✈️ 공군 포격", "🎖️ 군사 훈련"])

with tab_attack:
    c1, c2 = st.columns(2)
    my_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country]
    target_cities = [k for k, v in st.session_state.cities.items() if v["owner"] != selected_country]
    
    with c1:
        from_city = st.selectbox("출발 도시:", my_cities if my_cities else ["없음"])
    with c2:
        to_city = st.selectbox("공격 목표 도시:", target_cities)

    if st.button("⚔️ 공격 개시"):
        if not my_cities:
            st.error("소유한 도시가 없습니다.")
        else:
            att_city = st.session_state.cities[from_city]
            def_city = st.session_state.cities[to_city]
            
            def_owner = def_city["owner"]
            def_faction = st.session_state.countries[def_owner]["faction"]
            
            if def_faction == my_country["faction"]:
                st.warning("동맹국은 공격할 수 없습니다.")
            else:
                att_gar = att_city["garrison"]
                def_gar = def_city["garrison"]
                
                # 사기 및 보급(철도) 계수
                att_m = att_city["morale"] / 100.0
                def_m = def_city["morale"] / 100.0
                att_r = 1.0 if att_city["railway"] else 0.7
                def_r = 1.0 if def_city["railway"] else 0.7
                
                # 공격력 / 방어력 계산
                att_power = (att_gar["보병"]*20 + att_gar["포병"]*50 + att_gar["기병"]*25) * att_m * att_r
                def_power = (def_gar["보병"]*30 + def_gar["포병"]*10 + def_gar["기병"]*15) * def_m * def_r
                
                if att_power <= 0:
                    st.error("공격 도시의 주둔군이 부족합니다.")
                else:
                    # --- 병력 소모 연산 (전투 손실) ---
                    # 승패 여부에 상관없이 서로 피해를 입음
                    att_casualty_rate = min(0.8, (def_power / (att_power + 1)) * 0.5 + 0.1)
                    def_casualty_rate = min(0.8, (att_power / (def_power + 1)) * 0.5 + 0.1)
                    
                    # 주둔군 소모 적용
                    for unit in ["보병", "포병", "기병"]:
                        att_loss = int(att_gar[unit] * att_casualty_rate)
                        def_loss = int(def_gar[unit] * def_casualty_rate)
                        att_gar[unit] = max(0, att_gar[unit] - att_loss)
                        def_gar[unit] = max(0, def_gar[unit] - def_loss)
                    
                    # 전투 후 사기 감소
                    att_city["morale"] = max(10, att_city["morale"] - 15)
                    def_city["morale"] = max(10, def_city["morale"] - 15)
                    
                    # 판정
                    if att_power > def_power:
                        # 점령 성공: 남아있는 방어군이 적으면 점령
                        def_city["owner"] = selected_country
                        
                        # 공장 이관
                        civ_stolen, mil_stolen = def_city["civ"], def_city["mil"]
                        st.session_state.countries[def_owner]["civ_factories"] = max(0, st.session_state.countries[def_owner]["civ_factories"] - civ_stolen)
                        st.session_state.countries[def_owner]["mil_factories"] = max(0, st.session_state.countries[def_owner]["mil_factories"] - mil_stolen)
                        my_country["civ_factories"] += civ_stolen
                        my_country["mil_factories"] += mil_stolen
                        
                        # 일부 점령군 이동
                        def_city["garrison"] = {
                            "보병": int(att_gar["보병"] * 0.5),
                            "포병": int(att_gar["포병"] * 0.5),
                            "기병": int(att_gar["기병"] * 0.5),
                            "공군": 0
                        }
                        att_gar["보병"] -= def_city["garrison"]["보병"]
                        att_gar["포병"] -= def_city["garrison"]["포병"]
                        att_gar["기병"] -= def_city["garrison"]["기병"]
                        
                        st.success(f"🎉 승리! {to_city}을(를) 점령했습니다. (양측 전투로 손실 발생)")
                    else:
                        st.error(f"💥 패배! {to_city} 방어선 돌파에 실패했습니다. (공격군 사기 감소 및 손실 발생)")
                    
                    st.rerun()

with tab_air:
    st.markdown("### ✈️ 공군 포격")
    air_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country and v["garrison"]["공군"] > 0]
    air_from = st.selectbox("발진 도시:", air_cities if air_cities else ["공군 없음"])
    air_target = st.selectbox("목표 도시:", target_cities)
    
    if st.button("💣 공습 개시"):
        if air_from == "공군 없음":
            st.error("공군이 있는 도시가 없습니다.")
        else:
            target = st.session_state.cities[air_target]
            target_owner = st.session_state.countries[target["owner"]]
            
            # 시설 및 주둔군 소모
            loss_infantry = min(target["garrison"]["보병"], random.randint(3, 8))
            target["garrison"]["보병"] -= loss_infantry
            target["morale"] = max(10, target["morale"] - 20)
            
            if target["civ"] > 0 and random.random() > 0.5:
                target["civ"] -= 1
                target_owner["civ_factories"] = max(0, target_owner["civ_factories"] - 1)
            elif target["mil"] > 0:
                target["mil"] -= 1
                target_owner["mil_factories"] = max(0, target_owner["mil_factories"] - 1)
                
            st.warning(f"💥 {air_target} 공습 완료! (적 보병 {loss_infantry}기 손실 및 시설 피격)")
            st.rerun()

with tab_train:
    st.markdown("### 🎖️ 군사 훈련")
    train_city = st.selectbox("훈련 도시:", my_cities if my_cities else ["없음"])
    unit_type = st.selectbox("병종:", list(UNIT_SPECS.keys()))
    
    if st.button("훈련 시작"):
        spec = UNIT_SPECS[unit_type]
        if my_country["gold"] >= spec["gold"] and my_country["manpower"] >= spec["manpower"] and my_country["supplies"] >= spec["supplies"]:
            my_country["gold"] -= spec["gold"]
            my_country["manpower"] -= spec["manpower"]
            my_country["supplies"] -= spec["supplies"]
            st.session_state.cities[train_city]["garrison"][unit_type] += 1
            st.success(f"{train_city}에 {unit_type} 1기를 충원했습니다.")
            st.rerun()
        else:
            st.error("자원이 부족합니다.")

time.sleep(1)
st.rerun()
