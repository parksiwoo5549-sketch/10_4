import datetime
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="학사일정 D-day 계산기",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 이미지 속 학사일정 데이터 세션 상태 초기화 (2026년 9월 ~ 2027년 2월 기준)
if "schedules" not in st.session_state:
    st.session_state.schedules = [
        # 9월
        {
            "name": "대학수학능력시험 모의평가(3학년), 전국연합학력평가(1,2학년)",
            "date": datetime.date(2026, 9, 2),
            "category": "시험/성적",
        },
        {
            "name": "추석연휴",
            "date": datetime.date(2026, 9, 24),
            "category": "휴학/방학",
        },
        # 10월
        {
            "name": "개천절",
            "date": datetime.date(2026, 10, 3),
            "category": "휴학/방학",
        },
        {
            "name": "대체공휴일(개천절)",
            "date": datetime.date(2026, 10, 5),
            "category": "휴학/방학",
        },
        {
            "name": "2학기 1회 정기시험 시작",
            "date": datetime.date(2026, 10, 6),
            "category": "시험/성적",
        },
        {
            "name": "한글날",
            "date": datetime.date(2026, 10, 9),
            "category": "휴학/방학",
        },
        {
            "name": "전국연합학력평가(1,2,3학년)",
            "date": datetime.date(2026, 10, 20),
            "category": "시험/성적",
        },
        # 11월
        {
            "name": "수학여행(2학년) 시작",
            "date": datetime.date(2026, 11, 4),
            "category": "학황/기타",
        },
        {
            "name": "현장체험학습(1학년)",
            "date": datetime.date(2026, 11, 6),
            "category": "학황/기타",
        },
        {
            "name": "대학수학능력시험",
            "date": datetime.date(2026, 11, 19),
            "category": "시험/성적",
        },
        {
            "name": "재량휴업일(대학수학능력시험)",
            "date": datetime.date(2026, 11, 20),
            "category": "휴학/방학",
        },
        # 12월
        {
            "name": "현장체험학습(3학년)",
            "date": datetime.date(2026, 12, 4),
            "category": "학황/기타",
        },
        {
            "name": "2학기 2회 정기시험 시작",
            "date": datetime.date(2026, 12, 15),
            "category": "시험/성적",
        },
        {
            "name": "최소성취수준 보장 지도 기간 시작",
            "date": datetime.date(2026, 12, 28),
            "category": "학황/기타",
        },
        # 1월
        {
            "name": "신정",
            "date": datetime.date(2027, 1, 1),
            "category": "휴학/방학",
        },
        {
            "name": "종업식, 졸업식",
            "date": datetime.date(2027, 1, 8),
            "category": "학황/기타",
        },
        # 2월
        {
            "name": "설날연휴 시작",
            "date": datetime.date(2027, 2, 6),
            "category": "휴학/방학",
        },
        {
            "name": "대체공휴일(설날)",
            "date": datetime.date(2027, 2, 9),
            "category": "휴학/방학",
        },
    ]


# D-day 계산 함수
def calculate_dday(target_date):
    today = datetime.date.today()
    delta = (target_date - today).days
    return delta


# 메인 타이틀
st.title("📅 대학/학교 학사일정 D-day 계산기")
st.markdown("등록된 학사일정 및 남은 D-day를 실시간으로 확인하고 새로 추가해보세요.")
st.divider()

# 사이드바: 새 일정 추가 및 관리
with st.sidebar:
    st.header("➕ 새 학사일정 추가")

    with st.form("add_schedule_form", clear_on_submit=True):
        input_name = st.text_input("일정 이름", placeholder="예: 2학기 기말고사")
        input_date = st.date_input("일정 날짜", value=datetime.date.today())
        input_category = st.selectbox(
            "카테고리", ["시험/성적", "수강/등록", "휴학/방학", "학황/기타"]
        )

        submitted = st.form_submit_button("일정 등록하기", use_container_width=True)

        if submitted:
            if not input_name.strip():
                st.error("일정 이름을 입력해 주세요.")
            else:
                new_item = {
                    "name": input_name.strip(),
                    "date": input_date,
                    "category": input_category,
                }
                st.session_state.schedules.append(new_item)
                st.success(f"'{input_name}' 일정이 추가되었습니다!")
                st.rerun()

    st.divider()
    st.caption("Tip: 사용자가 추가하거나 삭제한 정보는 현재 세션 동안 적용됩니다.")

# 상단 통계 요약 (Metrics)
today = datetime.date.today()
total_count = len(st.session_state.schedules)
upcoming_schedules = [
    s for s in st.session_state.schedules if calculate_dday(s["date"]) >= 0
]
nearest_schedule = (
    min(upcoming_schedules, key=lambda x: calculate_dday(x["date"]))
    if upcoming_schedules
    else None
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📌 전체 등록된 일정", value=f"{total_count}개")
with col2:
    st.metric(label="⏳ 다가오는 일정", value=f"{len(upcoming_schedules)}개")
with col3:
    if nearest_schedule:
        days_left = calculate_dday(nearest_schedule["date"])
        st.metric(
            label=f"🔥 가장 임박한 일정 ({nearest_schedule['name']})",
            value=f"D-{days_left}" if days_left > 0 else "D-Day",
        )
    else:
        st.metric(label="🔥 가장 임박한 일정", value="없음")

st.divider()

# 일정 필터링 및 검색
search_col, filter_col = st.columns([2, 1])
with search_col:
    search_term = st.text_input("🔍 일정 검색", placeholder="검색할 일정명을 입력하세요 (예: 시험, 공휴일)")
with filter_col:
    filter_category = st.selectbox(
        "카테고리 필터", ["전체"] + ["시험/성적", "수강/등록", "휴학/방학", "학황/기타"]
    )

# 일정 데이터 필터링 및 정렬
filtered_schedules = st.session_state.schedules.copy()

if search_term:
    filtered_schedules = [
        s for s in filtered_schedules if search_term.lower() in s["name"].lower()
    ]

if filter_category != "전체":
    filtered_schedules = [
        s for s in filtered_schedules if s["category"] == filter_category
    ]

# D-day 기준으로 정렬 (오늘 기준 남은 일수가 적은 순 -> 지난 일순)
filtered_schedules.sort(key=lambda x: calculate_dday(x["date"]))

# D-day 카드 출력
st.subheader("📋 학사일정 목록")

if not filtered_schedules:
    st.info("등록된 일정이 없거나 검색 조건에 맞는 일정이 없습니다.")
else:
    cols = st.columns(3)  # 3열 그리드 레이아웃
    for index, item in enumerate(filtered_schedules):
        d_day = calculate_dday(item["date"])
        date_str = item["date"].strftime("%Y-%m-%d")

        # D-day 뱃지 색상 및 문구 처리
        if d_day > 0:
            badge = f"🟢 D-{d_day}"
            status_text = f"앞으로 **{d_day}일** 남았습니다."
        elif d_day == 0:
            badge = "🔴 D-Day (오늘)"
            status_text = "**오늘 진행되는 일정입니다!**"
        else:
            badge = f"⚪ D+{abs(d_day)}"
            status_text = f"**{abs(d_day)}일** 경과되었습니다."

        # 카드를 3열로 나누어 배치
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"### {item['name']}")
                st.caption(f"📁 {item['category']} | 📆 {date_str}")
                st.markdown(f"#### {badge}")
                st.write(status_text)

                # 삭제 버튼
                if st.button("삭제", key=f"del_{index}_{item['name']}", use_container_width=True):
                    st.session_state.schedules.remove(item)
                    st.toast(f"'{item['name']}' 일정이 삭제되었습니다.")
                    st.rerun()

st.divider()

# 표 형태 데이터 보기 옵션
with st.expander("📊 전체 일정 데이터 표 형태로 확인하기"):
    if st.session_state.schedules:
        df = pd.DataFrame(st.session_state.schedules)
        df["D-Day"] = df["date"].apply(
            lambda x: f"D-{calculate_dday(x)}"
            if calculate_dday(x) > 0
            else ("D-Day" if calculate_dday(x) == 0 else f"D+{abs(calculate_dday(x))}")
        )
        df["날짜"] = df["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df_display = df[["name", "category", "날짜", "D-Day"]].rename(
            columns={"name": "일정명", "category": "카테고리"}
        )
        st.dataframe(df_display, use_container_width=True)
    else:
        st.write("등록된 일정이 없습니다.")
