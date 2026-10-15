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

# 세션 상태 초기화 (샘플 데이터 제공)
if "schedules" not in st.session_state:
    today = datetime.date.today()
    st.session_state.schedules = [
        {"name": "중간고사", "date": today + datetime.timedelta(days=14), "category": "시험/성적"},
        {"name": "기말고사", "date": today + datetime.timedelta(days=60), "category": "시험/성적"},
        {"name": "여름방학 / 수강신청", "date": today + datetime.timedelta(days=80), "category": "휴학/방학"},
        {"name": "개강일", "date": today - datetime.timedelta(days=30), "category": "학황"},
    ]


# D-day 계산 함수
def calculate_dday(target_date):
    today = datetime.date.today()
    delta = (target_date - today).days
    return delta


# 메인 타이틀
st.title("📅 대학 학사일정 D-day 계산기")
st.markdown("중요한 학사일정을 입력하고 남은 D-day를 실시간으로 확인하세요.")
st.divider()

# 사이드바: 새 일정 추가 및 관리
with st.sidebar:
    st.header("➕ 새 학사일정 추가")

    with st.form("add_schedule_form", clear_on_submit=True):
        input_name = st.text_input("일정 이름", placeholder="예: 수강신청, 중간고사")
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
    st.caption("Tip: 사용자가 추가한 일정은 세션이 유지되는 동안 저장됩니다.")

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
    search_term = st.text_input("🔍 일정 검색", placeholder="검색할 일정명을 입력하세요")
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

# D-day 기준으로 정렬 (D-day가 임박한 것부터, 이미 지난 것은 맨 뒤로)
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
            status_text = "**오늘 처리해야 할 일정입니다!**"
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
with st.expander("📊 표 형태로 전체 일정 확인하기"):
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
