import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="1차 세계대전 대전략", layout="wide")

# ----------------------------------------------------
# 1. 게임 데이터 초기화 (이미지 지도 기반 진영 설정)
# ----------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    
    # 전쟁 상태 (시작과 동시에 협상국 vs 동맹국 전쟁 시작)
    st.session_state.war_status = True
    
    # 국가 데이터 (이미지상의 Allied / Central / Neutral 구분)
    st.session_state.countries = {
        # 협상국 (Allied Powers - 이미지의 녹색/연두색 계열)
        "프랑스": {"faction": "협상국", "gold": 600, "pop": 39000, "manpower": 200, "supplies": 300, "civ_factories": 8, "mil_factories": 5},
        "영국": {"faction": "협상국", "gold": 800, "pop": 45000, "manpower": 220, "supplies": 400, "civ_factories": 10, "mil_factories": 6},
        "러시아 제국": {"faction": "협상국", "gold": 400, "pop": 170000, "manpower": 800, "supplies": 200, "civ_factories": 5, "mil_factories": 4},
        "이탈리아": {"faction": "협상국", "gold": 350, "pop": 35000, "manpower": 150, "supplies": 180, "civ_factories": 5, "mil_factories": 3},
        "세르비아": {"faction": "협상국", "gold": 200, "pop": 4500, "manpower": 80, "supplies": 100, "civ_factories": 2, "mil_factories": 1},
        
        # 동맹국 (Central Powers - 이미지의 핑크/분홍색 계열)
        "독일 제국": {"faction": "동맹국", "gold": 750, "pop": 67000, "manpower": 350, "supplies": 450, "civ_factories": 11, "mil_factories": 8},
        "오스트리아-헝가리": {"faction": "동맹국", "gold": 450, "pop": 52000, "manpower": 250, "supplies": 250, "civ_factories": 6, "mil_factories": 4},
        "오스만 제국": {"faction": "동맹국", "gold": 300, "pop": 21000, "manpower": 180, "supplies": 150, "civ_factories": 4, "mil_factories": 2},
        "불가리아": {"faction": "동맹국", "gold": 200, "pop": 5500, "manpower": 90, "supplies": 100, "civ_factories": 2, "mil_factories": 1},
        
        # 중립국 (Neutral Powers - 이미지의 노란색 계열)
        "스페인": {"faction": "중립국", "gold": 400, "pop": 20000, "manpower": 100, "supplies": 100, "civ_factories": 4, "mil_factories": 1},
        "스위스": {"faction": "중립국", "gold": 500, "pop": 3800, "manpower": 50, "supplies": 100, "civ_factories": 5, "mil_factories": 1},
    }
    
    # 주요 도시 데이터 (위도, 경도, 소유국, 사기, 보급망, 주둔군)
    st.session_state.cities = {
        # 프랑스
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5}},
        "베르됭": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2}},
        # 영국
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10}},
        # 독일 제국
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10}},
        "메스": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5}},
        # 오스트리아-헝가리
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2}},
        "사라예보": {"lat": 43.8563, "lon": 18.4131, "owner": "오스트리아-헝가리", "railway": False, "morale": 90, "civ": 1, "mil": 0, "garrison": {"보병": 15, "포병": 5, "기병": 2, "공군": 0}},
        # 러시아 제국
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2}},
        "바르샤바": {"lat": 52.2297, "lon": 21.0122, "owner": "러시아 제국", "railway": False, "morale": 85, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 0}},
        # 오스만 제국
        "이스탄불": {"lat": 41.0082, "lon": 28.9784, "owner": "오스만 제국", "railway": True, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0}},
        # 중립국
        "마드리드": {"lat": 40.4168, "lon": -3.7038, "owner": "스페인", "railway": True, "morale": 100, "civ": 2, "mil": 0, "garrison": {"보병": 10, "포병": 0, "기병": 0, "공군": 0}},
    }
    
    st.session_state.player_country = "프랑스"

UNIT_SPECS = {
    "보병": {"gold": 30, "manpower": 50, "supplies": 20, "atk": 20, "def": 30},
    "포병": {"gold": 80, "manpower": 20, "supplies": 60, "atk": 50, "def": 10},
    "기병": {"gold": 50, "manpower": 30, "supplies": 30, "atk": 25, "def": 15},
    "공군": {"gold": 120, "manpower": 10, "supplies": 80, "atk": 60, "def": 5},
}

# ----------------------------------------------------
# 2. 실시간 시간 경과 및 자원/사기 관리 (10초 = 1주)
# ----------------------------------------------------
current_time = time.time()
if current_time - st.session_state.last_tick >= 10:
    st.session_state.week += 1
    st.session_state.last_tick = current_time
    
    # 주간 자원 및 사기 회복 로직
    for c_name, c_data in st.session_state.countries.items():
        c_data["gold"] += c_data["civ_factories"] * 25
        c_data["manpower"] += int(c_data["pop"] * 0.002)
        c_data["supplies"] += c_data["mil_factories"] * 20
        
    for city_name, city_info in st.session_state.cities.items():
        # 사기 천천히 회복 (최대 100)
        city_info["morale"] = min(100, city_info["morale"] + 2)

# ----------------------------------------------------
# 3. UI 및 대시보드
# ----------------------------------------------------
st.title("⚔️ 1차 세계대전: 대전착 실시간 전장")

# 전쟁 상태 안내
st.error("🔥 **[전쟁 상태]** 협상국(Allied Powers)과 동맹국(Central Powers) 간의 전면전이 진행 중입니다!")

selected_country = st.sidebar.selectbox(
    "플레이할 국가 선택:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country

my_country = st.session_state.countries[selected_country]
my_faction = my_country["faction"]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("소속 진영", my_faction)
col2.metric("골드", f"{my_country['gold']} G")
col3.metric("인력", f"{my_country['manpower']} 명")
col4.metric("보급품", f"{my_country['supplies']} 톤")
col5.metric("공장(민/군)", f"{my_country['civ_factories']} / {my_country['mil_factories']}")

# ----------------------------------------------------
# 4. 이미지 기반 지도 시각화 (Plotly)
# ----------------------------------------------------
st.subheader("🗺️ 1914 유럽 전장 지도")

fig = go.Figure()

# 이미지 지도 기반 색상 정의
FACTION_COLORS = {
    "협상국": "#5B8C5A",   # 연두/녹색 (Allied Powers)
    "동맹국": "#D98880",   # 분홍/연붉은색 (Central Powers)
    "중립국": "#F7DC6F"    # 노란색 (Neutral Powers)
}

# 도시 마커 추가
for c_name, c_info in st.session_state.cities.items():
    owner_country = c_info["owner"]
    faction = st.session_state.countries[owner_country]["faction"]
    marker_color = FACTION_COLORS[faction]
    
    gar = c_info["garrison"]
    total_army = gar["보병"] + gar["포병"] + gar["기병"]
    
    hover_text = f"<b>{c_name}</b><br>소유국: {owner_country} ({faction})<br>사기: {c_info['morale']}%<br>철도: {'있음' if c_info['railway'] else '없음 (보급 감소)'}<br>육군 수: {total_army}"
    
    fig.add_trace(go.Scattergeo(
        lat=[c_info["lat"]],
        lon=[c_info["lon"]],
        text=c_name,
        hoverinfo="text",
        hovertext=hover_text,
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=14,
            color=marker_color,
            line=dict(width=1.5, color="#2C3E50")
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
# 5. 전투 및 영토 점령 시스템
# ----------------------------------------------------
st.divider()
st.subheader("⚔️ 진격 및 전투 명령")

tab_attack, tab_air, tab_train = st.tabs(["🪖 육군 진격/전투", "✈️ 공장/도시 포격", "🎖️ 군사 훈련"])

with tab_attack:
    c1, c2 = st.columns(2)
    with c1:
        my_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country]
        from_city = st.selectbox("출발 도시:", my_cities if my_cities else ["없음"])
        
    with c2:
        # 타국 도시 전체
        target_cities = [k for k, v in st.session_state.cities.items() if v["owner"] != selected_country]
        to_city = st.selectbox("목표 공격/점령 도시:", target_cities)

    if st.button("⚔️ 공격 개시"):
        if not my_cities:
            st.error("소유한 도시가 없습니다.")
        else:
            attacker_city = st.session_state.cities[from_city]
            defender_city = st.session_state.cities[to_city]
            
            defender_owner = defender_city["owner"]
            defender_faction = st.session_state.countries[defender_owner]["faction"]
            
            if defender_faction == my_faction:
                st.warning("같은 진영의 국가는 공격할 수 없습니다.")
            else:
                # 공격력 및 방어력 계산 (사기 및 보급/철도 반영)
                att_gar = attacker_city["garrison"]
                def_gar = defender_city["garrison"]
                
                # 사기 및 철도 보너스/패널티
                att_morale_mult = attacker_city["morale"] / 100.0
                def_morale_mult = defender_city["morale"] / 100.0
                
                att_rail_mult = 1.0 if attacker_city["railway"] else 0.7
                def_rail_mult = 1.0 if defender_city["railway"] else 0.7
                
                att_power = (att_gar["보병"]*20 + att_gar["포병"]*50 + att_gar["기병"]*25) * att_morale_mult * att_rail_mult
                def_power = (def_gar["보병"]*30 + def_gar["포병"]*10 + def_gar["기병"]*15) * def_morale_mult * def_rail_mult
                
                # 주둔군 손실 난수 연산
                if att_power > def_power:
                    # 공격 성공: 도시 점령 처리
                    st.session_state.cities[to_city]["owner"] = selected_country
                    # 공장 이관
                    civ_stolen = defender_city["civ"]
                    mil_stolen = defender_city["mil"]
                    st.session_state.countries[defender_owner]["civ_factories"] = max(0, st.session_state.countries[defender_owner]["civ_factories"] - civ_stolen)
                    st.session_state.countries[defender_owner]["mil_factories"] = max(0, st.session_state.countries[defender_owner]["mil_factories"] - mil_stolen)
                    my_country["civ_factories"] += civ_stolen
                    my_country["mil_factories"] += mil_stolen
                    
                    # 주둔군 및 사기 차감
                    defender_city["garrison"] = {"보병": 5, "포병": 0, "기병": 0, "공군": 0}
                    attacker_city["morale"] = max(10, attacker_city["morale"] - 20)
                    
                    st.success(f"🎉 승리! {to_city}을(를) 점령했습니다! (공장 {civ_stolen + mil_stolen}개 확보)")
                    st.rerun()
                else:
                    # 공격 실패: 최근 전투로 사기 저하
                    attacker_city["morale"] = max(10, attacker_city["morale"] - 35)
                    st.error(f"💥 패배! {to_city} 방어선 돌파에 실패했습니다. (공격 부대 사기 감소)")

with tab_air:
    st.markdown("### ✈️ 공군 포격 (상대 도시 공장 파괴 및 병력 피해)")
    air_from = st.selectbox("발진 도시 (공군 보유 필요):", [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country and v["garrison"]["공군"] > 0] or ["공군 없음"])
    air_target = st.selectbox("포격 목표 도시:", [k for k, v in st.session_state.cities.items() if v["owner"] != selected_country])
    
    if st.button("💣 공습 개시"):
        if air_from == "공군 없음":
            st.error("공군을 보유한 도시가 없습니다.")
        else:
            target = st.session_state.cities[air_target]
            target_owner = st.session_state.countries[target["owner"]]
            
            # 피격 처리: 공장 파괴 및 육군 피해
            if target["civ"] > 0 and random.random() > 0.5:
                target["civ"] -= 1
                target_owner["civ_factories"] = max(0, target_owner["civ_factories"] - 1)
            elif target["mil"] > 0:
                target["mil"] -= 1
                target_owner["mil_factories"] = max(0, target_owner["mil_factories"] - 1)
                
            target["garrison"]["보병"] = max(0, target["garrison"]["보병"] - 5)
            target["morale"] = max(10, target["morale"] - 15)
            
            st.warning(f"💥 {air_target}에 성공적으로 포격을 가했습니다! (시설 파괴 및 병력 피격)")
            st.rerun()

with tab_train:
    st.markdown("### 🎖️ 군사 양성")
    train_city = st.selectbox("양성할 도시:", my_cities if my_cities else ["없음"])
    unit_type = st.selectbox("병종:", list(UNIT_SPECS.keys()))
    
    if st.button("훈련 시작"):
        spec = UNIT_SPECS[unit_type]
        if my_country["gold"] >= spec["gold"] and my_country["manpower"] >= spec["manpower"] and my_country["supplies"] >= spec["supplies"]:
            my_country["gold"] -= spec["gold"]
            my_country["manpower"] -= spec["manpower"]
            my_country["supplies"] -= spec["supplies"]
            st.session_state.cities[train_city]["garrison"][unit_type] += 1
            st.success(f"{train_city}에 {unit_type} 1개 유닛을 생성했습니다.")
            st.rerun()
        else:
            st.error("자원이 부족합니다.")

time.sleep(1)
st.rerun()
