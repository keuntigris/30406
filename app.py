import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(page_title="1차 세계대전 대전략", layout="wide")

# ----------------------------------------------------
# 1. 게임 데이터 및 세션 초기화
# ----------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_tick = time.time()
    st.session_state.week = 1
    st.session_state.battle_animation = None  # 전투 시각화 상태 저장용
    st.session_state.battle_logs = []         # 전투 진행 상황 로그
    
    # 국가별 고유 색상 및 세부 정보
    st.session_state.countries = {
        # 협상국
        "프랑스": {"faction": "협상국", "color": "#1F4E79", "gold": 600, "pop": 39000, "manpower": 200, "supplies": 300, "civ_factories": 8, "mil_factories": 5},
        "영국": {"faction": "협상국", "color": "#C0392B", "gold": 800, "pop": 45000, "manpower": 220, "supplies": 400, "civ_factories": 10, "mil_factories": 6},
        "러시아 제국": {"faction": "협상국", "color": "#7D3C98", "gold": 400, "pop": 170000, "manpower": 800, "supplies": 200, "civ_factories": 5, "mil_factories": 4},
        "이탈리아": {"faction": "협상국", "color": "#27AE60", "gold": 350, "pop": 35000, "manpower": 150, "supplies": 180, "civ_factories": 5, "mil_factories": 3},
        
        # 동맹국
        "독일 제국": {"faction": "동맹국", "color": "#2C3E50", "gold": 750, "pop": 67000, "manpower": 350, "supplies": 450, "civ_factories": 11, "mil_factories": 8},
        "오스트리아-헝가리": {"faction": "동맹국", "color": "#D4AC0D", "gold": 450, "pop": 52000, "manpower": 250, "supplies": 250, "civ_factories": 6, "mil_factories": 4},
        "오스만 제국": {"faction": "동맹국", "color": "#E67E22", "gold": 300, "pop": 21000, "manpower": 180, "supplies": 150, "civ_factories": 4, "mil_factories": 2},
    }
    
    st.session_state.cities = {
        "파리": {"lat": 48.8566, "lon": 2.3522, "owner": "프랑스", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 30, "포병": 10, "기병": 5, "공군": 5}},
        "베르됭": {"lat": 49.1599, "lon": 5.3843, "owner": "프랑스", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 25, "포병": 15, "기병": 0, "공군": 2}},
        "런던": {"lat": 51.5074, "lon": -0.1278, "owner": "영국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 25, "포병": 10, "기병": 5, "공군": 10}},
        "베를린": {"lat": 52.5200, "lon": 13.4050, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 4, "mil": 3, "garrison": {"보병": 35, "포병": 15, "기병": 10, "공군": 10}},
        "메스": {"lat": 49.1193, "lon": 6.1757, "owner": "독일 제국", "railway": True, "morale": 100, "civ": 1, "mil": 1, "garrison": {"보병": 30, "포병": 20, "기병": 5, "공군": 5}},
        "빈": {"lat": 48.2082, "lon": 16.3738, "owner": "오스트리아-헝가리", "railway": True, "morale": 100, "civ": 3, "mil": 2, "garrison": {"보병": 25, "포병": 10, "기병": 10, "공군": 2}},
        "상트페테르부르크": {"lat": 59.9311, "lon": 30.3609, "owner": "러시아 제국", "railway": True, "morale": 100, "civ": 2, "mil": 2, "garrison": {"보병": 40, "포병": 10, "기병": 15, "공군": 2}},
        "이스탄불": {"lat": 41.0082, "lon": 28.9784, "owner": "오스만 제국", "railway": True, "morale": 100, "civ": 2, "mil": 1, "garrison": {"보병": 20, "포병": 5, "기병": 5, "공군": 0}},
    }
    st.session_state.player_country = "프랑스"

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
st.title("⚔️ 1차 세계대전 대전략 - 전투 시각화 시스템")

selected_country = st.sidebar.selectbox(
    "플레이할 국가 선택:",
    list(st.session_state.countries.keys()),
    index=list(st.session_state.countries.keys()).index(st.session_state.player_country)
)
st.session_state.player_country = selected_country
my_country = st.session_state.countries[selected_country]

# 상단 현황판
c1, c2, c3, c4 = st.columns(4)
c1.metric("진영", my_country["faction"])
c2.metric("골드", f"{my_country['gold']} G")
c3.metric("인력", f"{my_country['manpower']} 명")
c4.metric("보급품", f"{my_country['supplies']} 톤")

# ----------------------------------------------------
# 4. 지도 시각화 (전투 진격선 및 교전 애니메이션 표시)
# ----------------------------------------------------
st.subheader("🗺️ 1914 유럽 전장 지도")

fig = go.Figure()

# 1) 기본 도시 마커 표시
for c_name, c_info in st.session_state.cities.items():
    owner_country = c_info["owner"]
    country_color = st.session_state.countries[owner_country]["color"]
    gar = c_info["garrison"]
    total_army = gar["보병"] + gar["포병"] + gar["기병"]
    
    hover_text = f"<b>{c_name}</b> ({owner_country})<br>사기: {c_info['morale']}%<br>주둔 육군: {total_army}기"
    
    fig.add_trace(go.Scattergeo(
        lat=[c_info["lat"]],
        lon=[c_info["lon"]],
        text=c_name,
        hoverinfo="text",
        hovertext=hover_text,
        mode="markers+text",
        textposition="top center",
        marker=dict(size=14, color=country_color, line=dict(width=1, color="#000000")),
        showlegend=False
    ))

# 2) 진행 중인 전투 시각화 (진격선 및 교전 지점 표시)
if st.session_state.battle_animation:
    anim = st.session_state.battle_animation
    from_c = st.session_state.cities[anim["from"]]
    to_c = st.session_state.cities[anim["to"]]
    
    # 공격 진격선 (빨간 점선)
    fig.add_trace(go.Scattergeo(
        lat=[from_c["lat"], to_c["lat"]],
        lon=[from_c["lon"], to_c["lon"]],
        mode="lines",
        line=dict(width=3, color="#E74C3C", dash="dash"),
        showlegend=False
    ))
    
    # 교전 지점 (목표 도시에 폭발/전투 아이콘 표시)
    fig.add_trace(go.Scattergeo(
        lat=[to_c["lat"]],
        lon=[to_c["lon"]],
        mode="text",
        text=["💥"],
        textfont=dict(size=28),
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
# 5. 전투 진행 상황 및 시각화 로그 출력
# ----------------------------------------------------
if st.session_state.battle_logs:
    st.subheader("📜 실시간 전투 속보")
    with st.expander("전투 상황 진행 뷰어er", expanded=True):
        for log in st.session_state.battle_logs:
            st.write(log)

# ----------------------------------------------------
# 6. 전투 명령 및 실행
# ----------------------------------------------------
st.divider()
st.subheader("⚔️ 전선 타격 및 진격")

my_cities = [k for k, v in st.session_state.cities.items() if v["owner"] == selected_country]
target_cities = [k for k, v in st.session_state.cities.items() if v["owner"] != selected_country]

col_a, col_b = st.columns(2)
with col_a:
    from_city = st.selectbox("출발 도시:", my_cities if my_cities else ["없음"])
with col_b:
    to_city = st.selectbox("공격 목표 도시:", target_cities)

if st.button("⚔️ 전면 진격 시도"):
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
            # 1) 시각화 상태 등록 (진격선 생성)
            st.session_state.battle_animation = {"from": from_city, "to": to_city}
            
            att_gar = att_city["garrison"]
            def_gar = def_city["garrison"]
            
            att_power = (att_gar["보병"]*20 + att_gar["포병"]*50 + att_gar["기병"]*25) * (att_city["morale"]/100.0)
            def_power = (def_gar["보병"]*30 + def_gar["포병"]*10 + def_gar["기병"]*15) * (def_city["morale"]/100.0)
            
            # 2) 전투 손실 계산 및 로그 생성
            att_loss_rate = min(0.7, (def_power / (att_power + 1)) * 0.4 + 0.1)
            def_loss_rate = min(0.7, (att_power / (def_power + 1)) * 0.4 + 0.1)
            
            att_lost_inf = int(att_gar["보병"] * att_loss_rate)
            def_lost_inf = int(def_gar["보병"] * def_loss_rate)
            
            att_gar["보병"] = max(0, att_gar["보병"] - att_lost_inf)
            def_gar["보병"] = max(0, def_gar["보병"] - def_lost_inf)
            
            # 사기 차감
            att_city["morale"] = max(10, att_city["morale"] - 15)
            def_city["morale"] = max(10, def_city["morale"] - 15)
            
            # 전투 로그 업데이트
            logs = [
                f"💣 **[1단계: 진격]** {selected_country}의 부대가 **{from_city}**에서 **{to_city}**로 진격했습니다!",
                f"💥 **[2단계: 교전]** 양측 포격 및 총격전 발생! ({selected_country} 보병 {att_lost_inf}기 손실 / {def_owner} 보병 {def_lost_inf}기 손실)",
            ]
            
            if att_power > def_power:
                def_city["owner"] = selected_country
                def_city["garrison"]["보병"] = int(att_gar["보병"] * 0.4)
                att_gar["보병"] -= def_city["garrison"]["보병"]
                logs.append(f"🎉 **[3단계: 승리]** **{to_city}**를 점령하고 주둔군을 배치했습니다!")
            else:
                logs.append(f"🛡️ **[3단계: 패배]** 적 방어선을 뚫지 못하고 후퇴했습니다.")
                
            st.session_state.battle_logs = logs
            st.rerun()

time.sleep(1)
st.rerun()
