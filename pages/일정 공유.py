import streamlit as st
st.title('일정 공유')
st.write('다가오는 일정을 확인하고 공유하세요')


import json
import uuid
from pathlib import Path
from datetime import date, datetime, time, timedelta
from urllib.parse import urlparse

import streamlit as st

st.set_page_config(
    page_title="모여라 | 일정공유",
    page_icon="📅",
    layout="wide",
)

DATA_FILE = Path("data.json")


def load_data():
    try:
        if DATA_FILE.exists():
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {
                    "events": data.get("events", []),
                    "group_link": data.get("group_link", ""),
                }
    except (OSError, json.JSONDecodeError, TypeError):
        st.warning("저장 데이터를 읽지 못했습니다. 새 데이터로 시작합니다.")
    return {"events": [], "group_link": ""}


def save_data():
    temp = DATA_FILE.with_suffix(".tmp")
    try:
        temp.write_text(
            json.dumps(st.session_state.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp.replace(DATA_FILE)
        return True
    except OSError:
        st.error("저장에 실패했습니다. 파일 권한을 확인해 주세요.")
        return False


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = date.today()


def days_left(event):
    try:
        return (date.fromisoformat(event["date"]) - today).days
    except (ValueError, KeyError, TypeError):
        return None


def status(event):
    days = days_left(event)
    if days is None:
        return "날짜 확인 필요"
    if days < 0:
        return "지난 일정"
    if days == 0:
        return "오늘"
    if days <= 3:
        return "🚨 마감 임박"
    if days <= 7:
        return "이번 주"
    return "예정"


def make_message(event):
    days = days_left(event)
    if days is not None and 0 <= days <= 3:
        heading = "🚨 일정 임박 안내"
    else:
        try:
            created = datetime.fromisoformat(event["created_at"])
            recent = datetime.now() - created <= timedelta(days=7)
        except (ValueError, KeyError, TypeError):
            recent = False
        heading = "🆕 새 일정 안내" if recent else "📣 일정 안내"

    lines = [
        heading,
        "",
        f"📌 {event['title']}",
        f"📅 날짜: {event['date']}",
        f"🕒 시간: {event.get('time', '미정')}",
    ]
    if event.get("location"):
        lines.append(f"📍 장소: {event['location']}")
    if event.get("owner"):
        lines.append(f"🙋 담당자: {event['owner']}")
    if event.get("description"):
        lines.append(f"📝 내용: {event['description']}")
    if days is not None:
        lines.append("⏳ 오늘 진행!" if days == 0 else (
            f"⏳ D-{days}" if days > 0 else f"⏳ {abs(days)}일 지남"
        ))
    lines.extend(["", "일정 확인 부탁드립니다! 🙌"])
    return "\n".join(lines)


st.title("📅 모여라")
st.caption("우리 모임의 일정을 한곳에 모으고 단체 톡방에 공유하세요.")

with st.sidebar:
    st.header("메뉴")
    page = st.radio(
        "이동",
        ["🏠 일정 보드", "➕ 일정 등록", "🗂️ 일정 관리", "📣 톡방 공유"],
        label_visibility="collapsed",
    )
    st.divider()
    st.metric("전체 일정", len(data["events"]))
    urgent = sum(
        1 for e in data["events"]
        if days_left(e) is not None and 0 <= days_left(e) <= 3
    )
    st.metric("3일 이내 일정", urgent)

events = sorted(
    data["events"],
    key=lambda e: (e.get("date", "9999"), e.get("time", "23:59")),
)

if page == "🏠 일정 보드":
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 일정", len(events))
    c2.metric("다가오는 일정", sum(
        1 for e in events if days_left(e) is not None and days_left(e) >= 0
    ))
    c3.metric("임박 일정", urgent)

    st.subheader("🔔 다가오는 일정")
    upcoming = [
        e for e in events
        if days_left(e) is not None and 0 <= days_left(e) <= 3
    ]
    if not upcoming:
        st.success("3일 이내에 예정된 일정이 없습니다.")
    for e in upcoming:
        with st.container(border=True):
            st.markdown(f"### {e['title']}")
            st.write(f"📅 {e['date']} · {e.get('time', '미정')}")
            st.warning(status(e))
            with st.expander("공유 문구 보기"):
                st.code(make_message(e))

    st.subheader("🗓️ 전체 일정")
    keyword = st.text_input("일정 검색", placeholder="일정명, 장소, 담당자")
    filter_option = st.selectbox(
        "일정 필터", ["전체", "임박 일정", "이번 주", "지난 일정"]
    )

    shown = []
    for e in events:
        text = " ".join([
            e.get("title", ""),
            e.get("location", ""),
            e.get("owner", ""),
            e.get("description", ""),
        ]).lower()
        if keyword.lower() not in text:
            continue
        days = days_left(e)
        if filter_option == "임박 일정" and not (
            days is not None and 0 <= days <= 3
        ):
            continue
        if filter_option == "이번 주" and not (
            days is not None and 0 <= days <= 7
        ):
            continue
        if filter_option == "지난 일정" and not (
            days is not None and days < 0
        ):
            continue
        shown.append(e)

    if not shown:
        st.info("표시할 일정이 없습니다.")
    for e in shown:
        with st.container(border=True):
            st.markdown(f"**{e['title']}**")
            st.write(f"📅 {e['date']} · {e.get('time', '미정')}")
            st.write(f"상태: {status(e)}")
            if e.get("location"):
                st.write(f"📍 {e['location']}")
            if e.get("owner"):
                st.write(f"🙋 담당자: {e['owner']}")
            if e.get("description"):
                st.write(e["description"])

elif page == "➕ 일정 등록":
    st.subheader("➕ 새 일정 등록")
    with st.form("new_event", clear_on_submit=True):
        title = st.text_input("일정명 *")
        c1, c2 = st.columns(2)
        event_date = c1.date_input("날짜", value=today + timedelta(days=1))
        event_time = c2.time_input("시간", value=time(18, 0))
        location = st.text_input("장소")
        owner = st.text_input("담당자")
        description = st.text_area("상세 내용")
        submitted = st.form_submit_button(
            "일정 등록하기", type="primary", use_container_width=True
        )

    if submitted:
        if not title.strip():
            st.error("일정명을 입력해 주세요.")
        elif len(title.strip()) > 150:
            st.error("일정명은 150자 이내로 입력해 주세요.")
        else:
            event = {
                "id": str(uuid.uuid4()),
                "title": title.strip(),
                "date": event_date.isoformat(),
                "time": event_time.strftime("%H:%M"),
                "location": location.strip(),
                "owner": owner.strip(),
                "description": description.strip(),
                "created_at": datetime.now().isoformat(),
            }
            data["events"].append(event)
            if save_data():
                st.success("일정이 등록되었습니다!")
                st.code(make_message(event))

elif page == "🗂️ 일정 관리":
    st.subheader("🗂️ 일정 수정 및 삭제")
    if not events:
        st.info("등록된 일정이 없습니다.")
    else:
        options = {
            f"{e['date']} {e.get('time', '')} · {e['title']}": e
            for e in events
        }
        label = st.selectbox("관리할 일정 선택", list(options.keys()))
        event = options[label]

        with st.form("edit_event"):
            title = st.text_input("일정명", value=event.get("title", ""))
            try:
                event_date = date.fromisoformat(event["date"])
            except (ValueError, KeyError, TypeError):
                event_date = today
            try:
                event_time = time.fromisoformat(event.get("time", "09:00"))
            except (ValueError, TypeError):
                event_time = time(9, 0)

            new_date = st.date_input("날짜", value=event_date)
            new_time = st.time_input("시간", value=event_time)
            location = st.text_input("장소", value=event.get("location", ""))
            owner = st.text_input("담당자", value=event.get("owner", ""))
            description = st.text_area(
                "상세 내용", value=event.get("description", "")
            )
            update = st.form_submit_button("변경사항 저장")

        if update:
            if not title.strip():
                st.error("일정명을 입력해 주세요.")
            elif len(title.strip()) > 150:
                st.error("일정명은 150자 이내로 입력해 주세요.")
            else:
                event.update({
                    "title": title.strip(),
                    "date": new_date.isoformat(),
                    "time": new_time.strftime("%H:%M"),
                    "location": location.strip(),
                    "owner": owner.strip(),
                    "description": description.strip(),
                })
                if save_data():
                    st.success("수정했습니다.")
                    st.rerun()

        st.divider()
        confirm = st.checkbox(f"'{event['title']}' 삭제를 확인합니다.")
        if st.button("🗑️ 일정 삭제", disabled=not confirm):
            data["events"] = [
                e for e in data["events"] if e["id"] != event["id"]
            ]
            if save_data():
                st.success("삭제했습니다.")
                st.rerun()

elif page == "📣 톡방 공유":
    st.subheader("📣 단체 톡방 공유")
    st.write("톡방 링크를 저장하고 공유할 일정을 골라 안내 문구를 만드세요.")

    with st.form("group_link"):
        link = st.text_input(
            "단체 톡방 링크",
            value=data.get("group_link", ""),
            placeholder="https://open.kakao.com/o/...",
        )
        save_link = st.form_submit_button("톡방 링크 저장")

    if save_link:
        parsed = urlparse(link.strip()) if link.strip() else None
        if link.strip() and (
            parsed.scheme not in ("http", "https") or not parsed.netloc
        ):
            st.error("http:// 또는 https://로 시작하는 링크를 입력하세요.")
        else:
            data["group_link"] = link.strip()
            if save_data():
                st.success("톡방 링크를 저장했습니다.")

    saved_link = data.get("group_link", "")
    if saved_link:
        st.link_button("💬 단체 톡방 열기", saved_link, use_container_width=True)

    st.divider()
    if not events:
        st.info("먼저 일정을 등록해 주세요.")
    else:
        options = {
            f"{e['date']} {e.get('time', '')} · {e['title']}": e
            for e in events
        }
        label = st.selectbox("공유할 일정 선택", list(options.keys()))
        event = options[label]

        days = days_left(event)
        if days is not None and 0 <= days <= 3:
            st.warning("이 일정은 3일 이내에 진행됩니다.")
        st.markdown("#### 단체 톡방에 보낼 문구")
        st.code(make_message(event), language=None)
        st.caption(
            "문구를 선택해 복사한 다음 톡방에 붙여넣어 전송하세요. "
            "메시지는 자동 발송되지 않습니다."
        )

st.divider()
st.caption("모여라 📅 · 일정은 JSON 파일에 저장됩니다.")
