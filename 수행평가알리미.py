
import json
import os
import calendar
from datetime import date, datetime
from pathlib import Path

import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="수행ON | 수행평가 일정 관리",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "planner_data.json"

SUBJECTS = [
    "국어", "수학", "영어", "통합사회", "통합과학",
    "한국사", "정보", "체육", "음악", "미술", "기타"
]

PAGES = [
    "🏠 홈",
    "📢 일정 공유",
    "🗓️ 전체 캘린더",
    "⏳ 학사일정 D-day",
]


# -----------------------------
# 데이터 관리
# -----------------------------
def default_data():
    return {
        "tasks": [],
        "events": [],
    }


def load_data():
    """JSON 데이터를 읽고, 문제가 있으면 안전하게 기본값을 사용한다."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            return default_data()

        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return default_data()

        if not isinstance(data.get("tasks", []), list):
            data["tasks"] = []

        if not isinstance(data.get("events", []), list):
            data["events"] = []

        data.setdefault("tasks", [])
        data.setdefault("events", [])
        return data

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return default_data()


def save_data(data):
    """파일 저장 오류가 발생해도 앱이 중단되지 않게 한다."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = DATA_DIR / "planner_data.tmp"

        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        os.replace(temp_file, DATA_FILE)
        return True

    except (OSError, TypeError, ValueError) as exc:
        st.error(
            "데이터를 저장하지 못했어. "
            f"저장 권한 또는 배포 환경을 확인해 줟: {exc}"
        )
        return False


def parse_date(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def next_id(items):
    existing = [
        item.get("id", 0)
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("id"), int)
    ]
    return max(existing, default=0) + 1


def days_until(target):
    return (target - date.today()).days


# -----------------------------
# 디자인
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #F5F7FB;
    }
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 2.2rem;
        border-radius: 22px;
        color: white;
        background: linear-gradient(120deg, #14243A, #3157D5);
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: .5rem;
    }
    .hero p {
        color: #E0E8F7;
        font-size: 1.05rem;
    }
    .feature {
        background: white;
        border: 1px solid #E5EAF3;
        padding: 1.2rem;
        border-radius: 16px;
        min-height: 160px;
    }
    .feature h3 {
        margin-top: 0.3rem;
        color: #182A45;
    }
    .muted {
        color: #65738A;
        font-size: .92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# 앱 상태
# -----------------------------
if "planner_data" not in st.session_state:
    st.session_state.planner_data = load_data()

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 홈"

data = st.session_state.planner_data

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.title("📚 수행ON")
    st.caption("수행평가 일정 관리 플랫폼")
    st.divider()

    selected_page = st.radio(
        "메뉴",
        PAGES,
        index=PAGES.index(st.session_state.current_page)
        if st.session_state.current_page in PAGES else 0,
        key="page_navigation",
    )
    st.session_state.current_page = selected_page

    st.divider()
    st.markdown("### 💡 사용 순서")
    st.markdown(
        "1. 일정 공유에서 과제를 등록해.\n"
        "2. 전체 캘린더에서 날짜를 확인해.\n"
        "3. D-day 페이지에서 중요한 날을 관리해."
    )
    st.caption("현재 날짜: " + date.today().strftime("%Y-%m-%d"))


# -----------------------------
# 공통 데이터 요약
# -----------------------------
tasks = [
    task for task in data["tasks"]
    if isinstance(task, dict)
]
events = [
    event for event in data["events"]
    if isinstance(event, dict)
]

today = date.today()
valid_tasks = [
    task for task in tasks
    if parse_date(task.get("due_date")) is not None
]

upcoming_tasks = sorted(
    [
        task for task in valid_tasks
        if parse_date(task.get("due_date")) >= today
        and not task.get("completed", False)
    ],
    key=lambda task: task["due_date"],
)

completed_count = sum(
    1 for task in tasks if task.get("completed", False)
)
total_tasks = len(tasks)
completion_rate = (
    round(completed_count / total_tasks * 100)
    if total_tasks else 0
)


# ============================================================
# PAGE 1: 홈
# ============================================================
if st.session_state.current_page == "🏠 홈":
    st.markdown(
        """
        <div class="hero">
            <h1>📚 수행ON</h1>
            <p><b>수행평가, 이제 한곳에서!</b></p>
            <p>
            일정을 공유하고, 캘린더로 확인하고,
            중요한 학사일까지 D-day로 관리해 보세요.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("📊 나의 일정 한눈에 보기")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 수행평가", f"{total_tasks}개")
    col2.metric("미완료 과제", f"{total_tasks - completed_count}개")
    col3.metric("완료율", f"{completion_rate}%")
    col4.metric("학사일정", f"{len(events)}개")

    st.progress(completion_rate / 100 if total_tasks else 0)

    st.subheader("🚀 어떤 기능을 사용할까?")

    feature_cols = st.columns(3)

    with feature_cols[0]:
        st.markdown(
            """
            <div class="feature">
                <h2>📢</h2>
                <h3>일정 공유</h3>
                <p class="muted">
                수행평가를 등록하고, 과목과 제출 기한을 관리해.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("일정 공유로 이동 →", use_container_width=True):
            st.session_state.current_page = "📢 일정 공유"
            st.rerun()

    with feature_cols[1]:
        st.markdown(
            """
            <div class="feature">
                <h2>🗓️</h2>
                <h3>전체 캘린더</h3>
                <p class="muted">
                날짜별로 수행평가를 모아 보고 특정 날짜의 일정을 확인해.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("캘린더로 이동 →", use_container_width=True):
            st.session_state.current_page = "🗓️ 전체 캘린더"
            st.rerun()

    with feature_cols[2]:
        st.markdown(
            """
            <div class="feature">
                <h2>⏳</h2>
                <h3>학사일정 D-day</h3>
                <p class="muted">
                시험, 방학, 개학 등 중요한 날짜까지 남은 날을 계산해.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("D-day 확인 →", use_container_width=True):
            st.session_state.current_page = "⏳ 학사일정 D-day"
            st.rerun()

    st.subheader("🔔 다가오는 수행평가")

    if upcoming_tasks:
        for task in upcoming_tasks[:5]:
            due = parse_date(task.get("due_date"))
            if due is None:
                continue

            remaining = days_until(due)
            if remaining == 0:
                label = "🔥 오늘 마감"
            elif remaining <= 3:
                label = f"⚠️ D-{remaining}"
            else:
                label = f"D-{remaining}"

            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(
                    f"**{task.get('title', '이름 없는 과제')}**"
                )
                left.caption(
                    f"{task.get('subject', '기타')} · "
                    f"마감 {due.isoformat()}"
                )
                right.markdown(f"**{label}**")
    else:
        st.info("아직 예정된 미완료 수행평가가 없어. 일정 공유에서 추가해 봐!")

    st.caption(
        "※ 이 앱의 기본 데이터는 현재 실행 환경의 JSON 파일에 저장돼. "
        "여러 사용자의 실시간 공유에는 공용 데이터베이스가 필요해."
    )


# ============================================================
# PAGE 2: 일정 공유
# ============================================================
elif st.session_state.current_page == "📢 일정 공유":
    st.title("📢 수행평가 일정 공유")
    st.write("과제와 제출 기한을 등록하고 진행 상태를 관리해.")

    with st.expander("➕ 새 수행평가 등록", expanded=not bool(tasks)):
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input(
                "수행평가 이름 *",
                placeholder="예: 과학 탐구 보고서",
            )

            c1, c2 = st.columns(2)
            subject = c1.selectbox("과목", SUBJECTS)
            due_date = c2.date_input("제출 기한", value=today)

            description = st.text_area(
                "설명 및 준비물",
                placeholder="준비할 내용이나 제출 방법을 적어 줘.",
            )
            author = st.text_input(
                "작성자 (선택)",
                placeholder="예: 2학년 3반",
            )

            submitted = st.form_submit_button(
                "일정 등록하기",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not title.strip():
                    st.error("수행평가 이름을 입력해 줘.")
                else:
                    new_task = {
                        "id": next_id(data["tasks"]),
                        "title": title.strip(),
                        "subject": subject,
                        "due_date": due_date.isoformat(),
                        "description": description.strip(),
                        "author": author.strip(),
                        "completed": False,
                        "created_at": datetime.now().isoformat(
                            timespec="seconds"
                        ),
                    }
                    data["tasks"].append(new_task)

                    if save_data(data):
                        st.session_state.planner_data = data
                        st.success("수행평가 일정을 등록했어!")
                        st.rerun()

    st.divider()
    st.subheader("📋 등록된 일정")

    filter_subject = st.selectbox(
        "과목별 필터",
        ["전체 과목"] + SUBJECTS,
        key="task_subject_filter",
    )
    filter_status = st.selectbox(
        "진행 상태",
        ["전체", "미완료", "완료"],
        key="task_status_filter",
    )

    filtered_tasks = tasks.copy()

    if filter_subject != "전체 과목":
        filtered_tasks = [
            t for t in filtered_tasks
            if t.get("subject") == filter_subject
        ]

    if filter_status == "미완료":
        filtered_tasks = [
            t for t in filtered_tasks
            if not t.get("completed", False)
        ]
    elif filter_status == "완료":
        filtered_tasks = [
            t for t in filtered_tasks
            if t.get("completed", False)
        ]

    filtered_tasks.sort(
        key=lambda t: t.get("due_date", "9999-12-31")
    )

    if not filtered_tasks:
        st.info("조건에 맞는 일정이 없어. 새 일정을 등록해 봐.")
    else:
        for task in filtered_tasks:
            task_id = task.get("id")
            due = parse_date(task.get("due_date"))
            completed = bool(task.get("completed", False))

            with st.container(border=True):
                c1, c2 = st.columns([5, 1])

                c1.markdown(
                    f"### {'✅' if completed else '📝'} "
                    f"{task.get('title', '이름 없는 과제')}"
                )
                c1.caption(
                    f"{task.get('subject', '기타')} · "
                    f"마감일: {due.isoformat() if due else '미정'} · "
                    f"작성자: {task.get('author') or '미입력'}"
                )

                description_text = task.get("description", "")
                if description_text:
                    c1.write(description_text)

                if due:
                    remaining = days_until(due)
                    if completed:
                        c1.success("완료한 과제")
                    elif remaining < 0:
                        c1.error(f"기한 초과: {abs(remaining)}일 지남")
                    elif remaining == 0:
                        c1.warning("오늘 마감!")
                    else:
                        c1.info(f"제출까지 {remaining}일 남음")

                toggle_label = "완료 취소" if completed else "완료 처리"
                if c2.button(
                    toggle_label,
                    key=f"toggle_{task_id}",
                    use_container_width=True,
                ):
                    task["completed"] = not completed
                    if save_data(data):
                        st.session_state.planner_data = data
                        st.rerun()

                with st.expander("일정 관리"):
                    with st.form(f"edit_task_{task_id}"):
                        edited_title = st.text_input(
                            "과제명",
                            value=task.get("title", ""),
                        )
                        edit_col1, edit_col2 = st.columns(2)
                        old_subject = task.get("subject", "기타")
                        subject_index = (
                            SUBJECTS.index(old_subject)
                            if old_subject in SUBJECTS else len(SUBJECTS) - 1
                        )
                        edited_subject = edit_col1.selectbox(
                            "과목",
                            SUBJECTS,
                            index=subject_index,
                        )
                        edited_due = edit_col2.date_input(
                            "제출 기한",
                            value=due or today,
                        )
                        edited_description = st.text_area(
                            "설명",
                            value=description_text,
                        )
                        edited_author = st.text_input(
                            "작성자",
                            value=task.get("author", ""),
                        )

                        save_edit = st.form_submit_button("변경 저장")
                        if save_edit:
                            if not edited_title.strip():
                                st.error("과제명을 입력해 줘.")
                            else:
                                task.update({
                                    "title": edited_title.strip(),
                                    "subject": edited_subject,
                                    "due_date": edited_due.isoformat(),
                                    "description": edited_description.strip(),
                                    "author": edited_author.strip(),
                                })
                                if save_data(data):
                                    st.session_state.planner_data = data
                                    st.success("일정을 수정했어.")
                                    st.rerun()

                    if st.button(
                        "🗑️ 이 일정 삭제",
                        key=f"delete_{task_id}",
                    ):
                        data["tasks"] = [
                            t for t in data["tasks"]
                            if t.get("id") != task_id
                        ]
                        if save_data(data):
                            st.session_state.planner_data = data
                            st.rerun()

    st.divider()
    st.subheader("📤 일정 내보내기")

    try:
        json_text = json.dumps(
            data["tasks"], ensure_ascii=False, indent=2
        )
        st.download_button(
            "JSON으로 일정 다운로드",
            data=json_text.encode("utf-8"),
            file_name="performance_tasks.json",
            mime="application/json",
            use_container_width=True,
        )
    except (TypeError, ValueError):
        st.error("일정 내보내기 중 오류가 발생했어.")


# ============================================================
# PAGE 3: 전체 캘린더
# ============================================================
elif st.session_state.current_page == "🗓️ 전체 캘린더":
    st.title("🗓️ 수행평가 캘린더")
    st.write("월별로 수행평가를 모아 확인해.")

    valid_calendar_tasks = [
        t for t in tasks if parse_date(t.get("due_date"))
    ]

    available_dates = [
        parse_date(t["due_date"]) for t in valid_calendar_tasks
    ]

    if available_dates:
        first_date = min(available_dates)
    else:
        first_date = today

    year_options = list(range(
        min(today.year, first_date.year) - 1,
        max(today.year, first_date.year) + 3,
    ))
    if today.year not in year_options:
        year_options.append(today.year)

    c1, c2 = st.columns(2)
    selected_year = c1.selectbox(
        "연도", sorted(set(year_options)), index=sorted(
            set(year_options)
        ).index(today.year)
    )
    selected_month = c2.selectbox(
        "월", list(range(1, 13)), index=today.month - 1,
        format_func=lambda m: f"{m}월"
    )

    month_matrix = calendar.monthcalendar(
        selected_year, selected_month
    )
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

    st.markdown(
        """
        <style>
        .calendar-day {
            border: 1px solid #DCE3EE;
            background: white;
            border-radius: 10px;
            min-height: 80px;
            padding: 7px;
            margin-bottom: 5px;
        }
        .calendar-today {
            border: 2px solid #3157D5;
            background: #EEF3FF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    header_cols = st.columns(7)
    for idx, name in enumerate(weekday_names):
        header_cols[idx].markdown(f"**{name}**")

    for week in month_matrix:
        week_cols = st.columns(7)
        for idx, day_num in enumerate(week):
            with week_cols[idx]:
                if day_num == 0:
                    st.markdown(
                        '<div class="calendar-day"></div>',
                        unsafe_allow_html=True,
                    )
                    continue

                current_date = date(
                    selected_year, selected_month, day_num
                )
                day_tasks = [
                    t for t in valid_calendar_tasks
                    if parse_date(t.get("due_date")) == current_date
                ]

                if current_date == today:
                    st.markdown(f"**🔵 {day_num}일 · 오늘**")
                else:
                    st.markdown(f"**{day_num}일**")

                if not day_tasks:
                    st.caption("일정 없음")
                else:
                    st.caption(f"📌 {len(day_tasks)}개")

                    for task in day_tasks[:3]:
                        title = task.get("title", "이름 없는 과제")
                        st.markdown(
                            f"- {'✅' if task.get('completed') else '📝'} "
                            f"{title}"
                        )
                    if len(day_tasks) > 3:
                        st.caption(f"+ {len(day_tasks) - 3}개 더")

    st.divider()
    st.subheader(
        f"📍 {selected_year}년 {selected_month}월 일정 목록"
    )

    month_tasks = [
        t for t in valid_calendar_tasks
        if (d := parse_date(t.get("due_date"))) is not None
        and d.year == selected_year
        and d.month == selected_month
    ]
    month_tasks.sort(key=lambda t: t["due_date"])

    if not month_tasks:
        st.info("이번 달에 등록된 수행평가가 없어.")
    else:
        for task in month_tasks:
            status = "완료" if task.get("completed") else "미완료"
            st.markdown(
                f"- **{task.get('due_date')}** — "
                f"{task.get('title', '이름 없는 과제')} "
                f"({task.get('subject', '기타')}, {status})"
            )


# ============================================================
# PAGE 4: 학사일정 D-day
# ============================================================
elif st.session_state.current_page == "⏳ 학사일정 D-day":
    st.title("⏳ 학사일정 D-day")
    st.write("시험, 방학, 개학 등 잊으면 안 되는 날짜를 관리해.")

    with st.expander("➕ 학사일정 추가", expanded=not bool(events)):
        with st.form("add_event_form", clear_on_submit=True):
            event_title = st.text_input(
                "학사일정 이름 *",
                placeholder="예: 2학기 기말고사",
            )
            event_date = st.date_input(
                "날짜",
                value=today,
                key="event_date_input",
            )
            event_category = st.selectbox(
                "종류",
                ["시험", "방학", "개학", "학교 행사", "기타"],
            )
            event_description = st.text_area(
                "메모",
                placeholder="장소, 준비물 또는 참고할 내용을 적어 줘.",
            )

            add_event = st.form_submit_button(
                "D-day 등록하기",
                type="primary",
                use_container_width=True,
            )

            if add_event:
                if not event_title.strip():
                    st.error("학사일정 이름을 입력해 줘.")
                else:
                    data["events"].append({
                        "id": next_id(data["events"]),
                        "title": event_title.strip(),
                        "event_date": event_date.isoformat(),
                        "category": event_category,
                        "description": event_description.strip(),
                    })

                    if save_data(data):
                        st.session_state.planner_data = data
                        st.success("학사일정을 등록했어!")
                        st.rerun()

    st.divider()
    st.subheader("📅 등록된 학사일정")

    valid_events = [
        e for e in events if parse_date(e.get("event_date"))
    ]
    valid_events.sort(key=lambda e: e["event_date"])

    if not valid_events:
        st.info("아직 등록된 학사일정이 없어.")
    else:
        for event in valid_events:
            target = parse_date(event.get("event_date"))
            if target is None:
                continue

            remaining = days_until(target)

            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(
                    f"### 📌 {event.get('title', '이름 없는 일정')}"
                )
                left.caption(
                    f"{event.get('category', '기타')} · "
                    f"{target.isoformat()}"
                )

                if event.get("description"):
                    left.write(event["description"])

                if remaining > 0:
                    right.metric("D-day", f"D-{remaining}")
                elif remaining == 0:
                    right.metric("D-day", "D-DAY")
                else:
                    right.metric("경과", f"D+{abs(remaining)}")

                if st.button(
                    "일정 삭제",
                    key=f"delete_event_{event.get('id')}",
                ):
                    event_id = event.get("id")
                    data["events"] = [
                        e for e in data["events"]
                        if e.get("id") != event_id
                    ]
                    if save_data(data):
                        st.session_state.planner_data = data
                        st.rerun()

    st.divider()
    st.subheader("📦 데이터 백업 및 복원")

    backup_json = json.dumps(
        data, ensure_ascii=False, indent=2
    )
    st.download_button(
        "전체 일정 백업 다운로드 (JSON)",
        data=backup_json.encode("utf-8"),
        file_name="suhaengon_backup.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded = st.file_uploader(
        "백업 JSON 파일 불러오기",
        type=["json"],
        help="복원하면 현재 등록된 수행평가와 학사일정이 백업 내용으로 교체돼.",
    )

    if uploaded is not None:
        if st.button("백업 데이터 복원", type="secondary"):
            try:
                restored = json.loads(
                    uploaded.getvalue().decode("utf-8")
                )
                if (
                    not isinstance(restored, dict)
                    or not isinstance(restored.get("tasks"), list)
                    or not isinstance(restored.get("events"), list)
                ):
                    st.error("올바른 수행ON 백업 파일이 아니야.")
                elif not all(
                    isinstance(item, dict)
                    for item in restored["tasks"] + restored["events"]
                ):
                    st.error("백업 파일의 데이터 형식이 올바르지 않아.")
                else:
                    if save_data(restored):
                        st.session_state.planner_data = restored
                        st.success("백업 데이터를 복원했어.")
                        st.rerun()
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):
                st.error("JSON 파일을 읽지 못했어. 파일을 확인해 줘.")


