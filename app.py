import streamlit as st
import time
import random
import pandas as pd
import streamlit.components.v1 as components
import json
import os
import hashlib
from datetime import datetime, date

# 1. 페이지 설정
st.set_page_config(
    page_title="Focus Center Final",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS: UI 디자인 고도화
st.markdown("""
<style>
/* 전체 배경 및 폰트 */
.stApp { background-color: #1A1C1E; font-family: 'Pretendard', sans-serif; }
header, footer { visibility: hidden; }

/* 메인 컨테이너 최적화 */
.main .block-container {
    max-width: 600px !important;
    margin: 0 auto !important;
    padding-top: 1.5rem !important;
}

/* 캘린더 박스 디자인 */
.calendar-box {
    background-color: #25272B;
    padding: 12px;
    border-radius: 14px;
    border: 1px solid #3D3F46;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 8px;
}
.day-cell {
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    background-color: #1A1C1E;
    color: #4A4D55;
}
.day-success {
    background-color: #FEE500 !important;
    color: #000 !important;
    box-shadow: inset 0 0 5px rgba(255,255,255,0.5);
}

/* 상단 우측 버튼 스타일 */
.stButton > button {
    width: 100% !important;
}
.stButton > button[key="save_btn"], .stButton > button[key="logout_top"] {
    height: 45px !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
    transition: all 0.2s ease;
}
.stButton > button[key="save_btn"]:hover { transform: scale(1.02); background-color: #339AF0 !important; }
.stButton > button[key="save_btn"] { background-color: #4DABF7 !important; color: white !important; border: none !important; }
.stButton > button[key="logout_top"] { background-color: #3D3F46 !important; color: #FFFFFF !important; border: none !important; }

/* 게임 구동 노란 버튼 (핵심) */
div.stButton > button:not([key="save_btn"]):not([key="logout_top"]) {
    background-color: #FEE500 !important;
    color: #000000 !important;
    height: 85px !important;
    font-size: 22px !important;
    font-weight: 900 !important;
    border-radius: 15px !important;
    border: none !important;
    box-shadow: 0 5px 0 #D1BC00;
}
div.stButton > button:not([key="save_btn"]):not([key="logout_top"]):active {
    box-shadow: none;
    transform: translateY(4px);
}

.status-bar { background-color: #25272B; padding: 12px; border-radius: 12px; margin-bottom: 20px; text-align: center; color: #BDBDBD !important; font-weight: 600; border: 1px solid #3D3F46; }
.spacer { height: 80px; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; text-align: center; }
input { background-color: #2D2F34 !important; color: white !important; border: 1px solid #3D3F46 !important; height: 50px !important; border-radius: 8px !important; }

/* 텍스트 컬러 강제 지정 */
h1, h2, h3, p, span, label { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# JS: 버튼 텍스트 가독성 확보
components.html("<script>const fix=()=>{window.parent.document.querySelectorAll('button p, button span, button div').forEach(b=>{const t=b.innerText;if(!t.includes('로그아웃') && !t.includes('저장') && !t.includes('💾') && !t.includes('🚪')){b.style.color='black';b.style.fontWeight='900';}});};setInterval(fix,300);</script>", height=0)

# 3. 데이터 및 세션 로직 (보존)
DB_FILE = "users_complete_v2.json"
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, ensure_ascii=False, indent=2)

# 세션 초기화
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'attendance' not in st.session_state: st.session_state.attendance = []
if 'user_role' not in st.session_state: st.session_state.user_role = "성인"
if 'game_choice' not in st.session_state: st.session_state.game_choice = "🚀 반응 속도 테스트"
if 'game_step' not in st.session_state: st.session_state.game_step = "READY"
if 'history' not in st.session_state: st.session_state.history = []
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'diff_level' not in st.session_state: st.session_state.diff_level = 3
if 'st_t' not in st.session_state: st.session_state.st_t = None

# 4. 로그인 / 회원가입
if not st.session_state.logged_in:
    st.title("🔐 Focus Center")
    t1, t2 = st.tabs(["로그인", "회원가입"])
    with t1:
        u_in = st.text_input("아이디", key="l_u")
        p_in = st.text_input("비밀번호", type="password", key="l_p")
        if st.button("로그인 실행"):
            db = load_db()
            if u_in in db:
                if db[u_in]["password"] == hash_pw(p_in) or db[u_in]["password"] == p_in:
                    st.session_state.logged_in = True
                    st.session_state.user = u_in
                    st.session_state.user_role = db[u_in]["role"]
                    st.session_state.history = db[u_in].get("history", [])
                    st.session_state.attendance = db[u_in].get("attendance", [])
                    today_str = date.today().isoformat()
                    if today_str not in st.session_state.attendance:
                        st.session_state.attendance.append(today_str)
                        db[u_in]["attendance"] = st.session_state.attendance
                        save_db(db)
                    st.rerun()
                else: st.error("정보 불일치")
            else: st.error("계정이 존재하지 않습니다.")
    with t2:
        role = st.radio("사용자 유형", ["아동(자녀)", "성인", "보호자(부모)"])
        nu = st.text_input("새 아이디")
        np = st.text_input("새 비밀번호", type="password")
        if st.button("가입 완료"):
            if nu and np:
                db = load_db()
                db[nu] = {"password": hash_pw(np), "role": role, "history": [], "attendance": [date.today().isoformat()], "streak": 0}
                save_db(db)
                st.success("가입 성공! 로그인 해주세요.")
            else: st.warning("정보를 입력하세요.")
    st.stop()

# 5. 메인 레이아웃 (상단 캘린더 & 제어 버튼)
with st.container():
    col_cal, col_btn = st.columns([1.2, 0.8])
    
    with col_cal:
        st.markdown(f"<p style='font-size:13px; font-weight:600; margin-bottom:8px;'>📅 {datetime.now().month}월 출석 현황</p>", unsafe_allow_html=True)
        att_set = set(st.session_state.attendance)
        html_days = ""
        # 1일부터 31일까지 (해당 월의 마지막 날짜 자동 계산 가능하나 단순화 유지)
        for d in range(1, 32):
            try:
                current_date = date(date.today().year, date.today().month, d)
                status_class = "day-success" if current_date.isoformat() in att_set else ""
                html_days += f'<div class="day-cell {status_class}">{d}</div>'
            except ValueError:
                html_days += f'<div class="day-cell" style="opacity:0;"></div>'
        st.markdown(f'<div class="calendar-box"><div class="calendar-grid">{html_days}</div></div>', unsafe_allow_html=True)
    
    with col_btn:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True) 
        if st.button("💾 데이터 저장", key="save_btn"):
            db = load_db()
            if st.session_state.user in db:
                db[st.session_state.user].update({"history": st.session_state.history, "attendance": st.session_state.attendance})
                save_db(db)
                st.toast("기록이 서버에 저장되었습니다!")
        if st.button("🚪 로그아웃", key="logout_top"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

st.divider()

# 6. 사용자 인사 및 게임 선택
st.markdown(f"### 👋 **{st.session_state.user}**님, 환영합니다!")
if st.session_state.user_role != "보호자(부모)":
    st.session_state.game_choice = st.selectbox("🎯 오늘의 집중력 훈련 선택", ["🚀 반응 속도 테스트", "🔎 숨은 그림 찾기", "🧠 숫자 기억 훈련"])

# 7. 게임 로직 (3종 무삭제 보존)
if st.session_state.user_role == "보호자(부모)":
    st.title("📊 학부모 대시보드")
    db = load_db()
    children = [n for n, d in db.items() if d.get("parent_id") == st.session_state.user]
    if children:
        c_view = st.selectbox("자녀 리포트 확인", children)
        if db[c_view].get("history"): st.line_chart(db[c_view]["history"])
    else: st.info("연동된 자녀 계정이 없습니다.")
else:
    st.markdown(f'<div class="status-bar">🔥 현재 연속 성공: {st.session_state.streak}회</div>', unsafe_allow_html=True)
    
    # [1] 반응 속도 테스트
    if "반응" in st.session_state.game_choice:
        if st.session_state.game_step == 'READY':
            st.markdown('<div class="spacer">START 버튼을 누르면 시작합니다</div>', unsafe_allow_html=True)
            if st.button("START"): st.session_state.game_step = 'WAIT'; st.rerun()
        elif st.session_state.game_step == 'WAIT':
            st.markdown('<div class="spacer" style="color:#FF6B6B;">준비하세요...</div>', unsafe_allow_html=True)
            time.sleep(random.uniform(2.0, 4.0))
            st.session_state.game_step = 'GO'
            st.rerun()
        elif st.session_state.game_step == 'GO':
            st.markdown('<div class="spacer" style="color:#51CF66; font-size:36px;">⚡ 지금 클릭!!!</div>', unsafe_allow_html=True)
            if st.session_state.st_t is None: st.session_state.st_t = time.time()
            if st.button("👆 PUSH"):
                res = round(time.time() - st.session_state.st_t, 3)
                st.session_state.history.append(res)
                st.session_state.streak += 1
                st.session_state.game_step = 'READY'
                st.session_state.st_t = None
                st.rerun()

    # [2] 숨은 그림 찾기
    elif "찾기" in st.session_state.game_choice:
        st.markdown('<div class="spacer">나머지와 다른 ○ 모양을 찾으세요!</div>', unsafe_allow_html=True)
        grid = ["●"] * 5 + ["○"]
        random.shuffle(grid)
        cols = st.columns(3)
        for i, item in enumerate(grid):
            with cols[i % 3]:
                if st.button(item, key=f"g_{i}"):
                    if item == "○": st.session_state.streak += 1
                    else: st.session_state.streak = 0
                    st.rerun()

    # [3] 숫자 기억 훈련
    elif "기억" in st.session_state.game_choice:
        if st.session_state.game_step == 'READY':
            st.markdown(f'<div class="spacer">{st.session_state.diff_level}개의 숫자가 나타납니다</div>', unsafe_allow_html=True)
            if st.button("숫자 보기 (SHOW)"):
                st.session_state.target_nums = [random.randint(1, 9) for _ in range(st.session_state.diff_level)]
                st.session_state.game_step = 'SHOW'; st.rerun()
        elif st.session_state.game_step == 'SHOW':
            num_str = "".join(map(str, st.session_state.target_nums))
            st.markdown(f'<div class="spacer" style="font-size:56px; color:#4DABF7;">{num_str}</div>', unsafe_allow_html=True)
            time.sleep(2.0); st.session_state.game_step = 'INPUT'; st.rerun()
        elif st.session_state.game_step == 'INPUT':
            st.markdown('<div class="spacer">기억한 숫자를 입력하세요</div>', unsafe_allow_html=True)
            ans = st.text_input("숫자 입력 창", key="m_in")
            if st.button("✅ 정답 확인"):
                if ans == "".join(map(str, st.session_state.target_nums)):
                    st.success("정답입니다!")
                    st.session_state.streak += 1
                    if st.session_state.streak % 3 == 0: st.session_state.diff_level += 1
                else: 
                    st.error(f"틀렸습니다! 정답은 { ''.join(map(str, st.session_state.target_nums)) }")
                    st.session_state.streak = 0; st.session_state.diff_level = 3
                st.session_state.game_step = 'READY'; st.rerun()

# 하단 히스토리 차트
if st.session_state.history:
    st.write("---")
    st.markdown("#### 📈 나의 훈련 기록 (반응 속도)")
    chart_data = pd.DataFrame(st.session_state.history, columns=["반응 속도"])
    st.line_chart(chart_data, use_container_width=True)