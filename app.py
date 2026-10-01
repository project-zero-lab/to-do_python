"""my_Taskz — Project Zero. Each browser tab gets its own private task list; nothing is saved to a database."""

import random
from datetime import date, datetime, time as dtime

import streamlit as st

st.set_page_config(page_title="my_Taskz · Project Zero", page_icon="✅", layout="wide")

PRIORITIES = ["🔴 High", "🟡 Medium", "🟢 Low"]
STATUSES = ["Not started", "In progress", "Done"]
SORT_OPTIONS = ["Deadline (soonest)", "Priority (high first)", "Newest first", "Oldest first"]
PRIORITY_RANK = {"🔴 High": 0, "🟡 Medium": 1, "🟢 Low": 2}
STATUS_EMOJI = {"Not started": "⬜", "In progress": "🟦", "Done": "✅"}
ACCENT = "#C96A1E"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --pz-bg: #FAF7F1; --pz-card: #FFFFFF; --pz-ink: #23262E;
            --pz-dim: #6B7080; --pz-line: #E4DFD2; --pz-chip-bg: #F7E9D9;
        }}

        .stApp, .stApp * {{
            color: var(--pz-ink) !important;
        }}
        .stApp {{ background-color: var(--pz-bg) !important; }}
        section[data-testid="stSidebar"] {{ background-color: var(--pz-bg) !important; }}
        input, textarea, select, [data-baseweb="select"] > div, [data-baseweb="input"] {{
            background-color: #FFFFFF !important;
        }}

        .pz-title {{
            font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em;
            line-height: 1.05;
        }}
        .pz-title span {{ color: {ACCENT} !important; }}
        .pz-sub {{ color: var(--pz-dim) !important; font-size: 0.95rem; margin-top: 2px; }}
        .pz-note {{
            color: var(--pz-dim) !important; font-size: 0.8rem; margin-top: 6px;
        }}
        .pz-nudge {{
            display: flex; align-items: center; gap: 8px;
            background: var(--pz-chip-bg) !important; border: 1px solid {ACCENT};
            border-radius: 10px; padding: 8px 14px; margin-top: 10px;
            font-size: 0.85rem; font-weight: 600; color: {ACCENT} !important;
            width: fit-content;
        }}
        .pz-nudge .arrow {{ font-size: 1.1rem; animation: pz-bounce 1.4s infinite; }}
        @keyframes pz-bounce {{
            0%, 100% {{ transform: translateX(0); }}
            50% {{ transform: translateX(-4px); }}
        }}

        .pz-card {{
            background: var(--pz-card) !important; border: 1px solid var(--pz-line);
            border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
        }}
        .pz-card.done {{ opacity: 0.55; }}

        .pz-chip {{
            display: inline-block; font-size: 0.75rem; font-weight: 600;
            padding: 2px 10px; border-radius: 999px; margin: 2px 6px 2px 0;
            background: var(--pz-chip-bg) !important; color: {ACCENT} !important;
        }}
        .pz-overdue {{ color: #C8382E !important; font-weight: 700; }}
        .pz-empty {{ text-align: center; padding: 40px 12px; color: var(--pz-dim) !important; }}

        .pz-board-card {{
            background: var(--pz-card) !important; border: 1px solid var(--pz-line);
            border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;
        }}

        [data-testid="InputInstructions"] {{ display: none !important; }}

        .pz-actions button {{ padding: 0.25rem 0.6rem !important; min-height: 2.1rem !important; width: auto !important; }}

        .pz-deadline {{ white-space: nowrap; display: inline-block; }}

        .block-container {{ max-width: 100% !important; padding-left: 1.2rem !important; padding-right: 1.2rem !important; }}

        @media (max-width: 640px) {{
            section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div {{
                width: 100% !important; min-width: 100% !important;
            }}
            .pz-title {{ font-size: 1.9rem; }}
            .block-container {{ padding-left: 0.8rem !important; padding-right: 0.8rem !important; }}
            .pz-card, .pz-board-card {{ width: 100% !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "tasks": [],
        "next_id": 1,
        "editing_id": None,
        "confirm_delete_id": None,
        "confirm_clear_done": False,
        "seeded": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def new_task(title, owner, deadline_date, deadline_time, priority, status, notes) -> dict:
    """One task = one dictionary. Blank person defaults to 'You'."""
    task_id = st.session_state.next_id
    st.session_state.next_id += 1
    return {
        "id": task_id,
        "title": title.strip(),
        "owner": owner.strip() if owner and owner.strip() else "You",
        "deadline": datetime.combine(deadline_date, deadline_time) if deadline_date else None,
        "priority": priority,
        "status": status,
        "notes": notes.strip() if notes else "",
        "created": datetime.now(),
    }


def seed_demo_tasks() -> None:
    if st.session_state.seeded:
        return
    st.session_state.seeded = True
    demo = [
        ("Finish my_TaskStack", "You", 2, dtime(18, 0), "🔴 High", "In progress", "Needs the while-loop menu"),
        ("Submit Session quiz", "You", 1, dtime(21, 0), "🟡 Medium", "Not started", ""),
        ("Read ch.3 — dictionaries", "You", 4, dtime(12, 0), "🟢 Low", "Not started", ""),
    ]
    for title, owner, days, t, pr, stat, notes in demo:
        d = date.fromordinal(date.today().toordinal() + days)
        st.session_state.tasks.append(new_task(title, owner, d, t, pr, stat, notes))


def is_overdue(task: dict) -> bool:
    return bool(task["deadline"]) and task["deadline"] < datetime.now() and task["status"] != "Done"


def sort_tasks(tasks: list, how: str) -> list:
    if how == "Deadline (soonest)":
        return sorted(tasks, key=lambda t: (t["deadline"] is None, t["deadline"] or datetime.max))
    if how == "Priority (high first)":
        return sorted(tasks, key=lambda t: PRIORITY_RANK[t["priority"]])
    if how == "Newest first":
        return sorted(tasks, key=lambda t: t["created"], reverse=True)
    if how == "Oldest first":
        return sorted(tasks, key=lambda t: t["created"])
    return tasks


def find_index_by_id(task_id: int):
    for i, t in enumerate(st.session_state.tasks):
        if t["id"] == task_id:
            return i
    return None


def delete_task(task_id: int) -> None:
    idx = find_index_by_id(task_id)
    if idx is not None:
        del st.session_state.tasks[idx]
    st.session_state.confirm_delete_id = None


def clear_completed() -> None:
    st.session_state.tasks = [t for t in st.session_state.tasks if t["status"] != "Done"]
    st.session_state.confirm_clear_done = False


def render_sidebar() -> tuple:
    with st.sidebar:
        st.markdown("### ➕ Add a task")
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Task name *", placeholder="e.g. Finish S04 after-work")
            owner = st.text_input("Person (optional — defaults to You)", placeholder="e.g. Aarav")
            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input("Deadline date", value=date.today())
            with c2:
                t = st.time_input("Deadline time", value=dtime(18, 0))
            c3, c4 = st.columns(2)
            with c3:
                priority = st.selectbox("Priority", PRIORITIES, index=1)
            with c4:
                status = st.selectbox("Status", STATUSES, index=0)
            notes = st.text_area("Notes (optional)", height=70, placeholder="Any extra detail…")
            submitted = st.form_submit_button("Add task", use_container_width=True, type="primary")

            if submitted:
                if not title.strip():
                    st.warning("Give the task a name first — nothing was added.")
                else:
                    st.session_state.tasks.append(new_task(title, owner, d, t, priority, status, notes))
                    st.toast(f"Added “{title.strip()}”", icon="✅")

        st.divider()
        st.markdown("### 📊 Overview")
        total = len(st.session_state.tasks)
        done = sum(1 for t in st.session_state.tasks if t["status"] == "Done")
        overdue = sum(1 for t in st.session_state.tasks if is_overdue(t))
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", total)
        c2.metric("Done", done)
        c3.metric("Overdue", overdue)
        if total:
            st.progress(done / total, text=f"{done}/{total} complete")

        st.divider()
        st.markdown("### 🔍 Filter & sort")
        status_filter = st.multiselect("Status", STATUSES, default=STATUSES)
        priority_filter = st.multiselect("Priority", PRIORITIES, default=PRIORITIES)
        search = st.text_input("Search by name or person", placeholder="Type to filter…")
        sort_by = st.selectbox("Sort by", SORT_OPTIONS, index=0)

        st.divider()
        with st.expander("🎲 Pick a random task"):
            st.caption("Same `random.choice()` pattern from Session 3.")
            if st.button("Spin", use_container_width=True):
                pending = [t for t in st.session_state.tasks if t["status"] != "Done"]
                st.session_state["_spun"] = random.choice(pending) if pending else None
                if not pending:
                    st.info("Nothing pending to pick from.")
            spun = st.session_state.get("_spun")
            if spun:
                st.success(f"👉 **{spun['title']}** — {spun['owner']}")

        st.divider()
        if st.button("🗑️ Clear completed tasks", use_container_width=True):
            st.session_state.confirm_clear_done = True
        if st.session_state.confirm_clear_done:
            st.warning("Remove all tasks marked Done? This can't be undone.")
            cc1, cc2 = st.columns(2)
            if cc1.button("Yes, clear", use_container_width=True, type="primary"):
                clear_completed()
                st.rerun()
            if cc2.button("Cancel", use_container_width=True):
                st.session_state.confirm_clear_done = False
                st.rerun()

        st.divider()
        st.caption("Built in **Project Zero** · runs entirely in your browser tab")

    return status_filter, priority_filter, search, sort_by


def format_deadline(task: dict) -> str:
    if not task["deadline"]:
        return "No deadline"
    return task["deadline"].strftime("%a, %d %b · %I:%M %p")


def render_task_card(task: dict) -> None:
    overdue = is_overdue(task)
    done = task["status"] == "Done"

    with st.container():
        st.markdown(f'<div class="pz-card{" done" if done else ""}">', unsafe_allow_html=True)

        title_html = f"~~{task['title']}~~" if done else f"**{task['title']}**"
        st.markdown(title_html)

        deadline_str = format_deadline(task)
        deadline_html = (
            f'<span class="pz-overdue pz-deadline">⚠ Overdue — was due {deadline_str}</span>'
            if overdue else f'<span class="pz-deadline">🗓️ {deadline_str}</span>'
        )
        st.markdown(
            f'<span class="pz-chip">{task["priority"]}</span>'
            f'<span class="pz-chip">{STATUS_EMOJI[task["status"]]} {task["status"]}</span>'
            f'<span class="pz-chip">👤 {task["owner"]}</span>'
            f'&nbsp;&nbsp;{deadline_html}',
            unsafe_allow_html=True,
        )
        if task["notes"]:
            st.caption(task["notes"])

        st.markdown('<div class="pz-actions">', unsafe_allow_html=True)
        col_check, col_edit, col_del, _ = st.columns([1, 1, 1, 6])
        with col_check:
            checked = st.checkbox("done", value=done, key=f"chk_{task['id']}", label_visibility="collapsed")
            if checked != done:
                idx = find_index_by_id(task["id"])
                if idx is not None:
                    st.session_state.tasks[idx]["status"] = "Done" if checked else "Not started"
                    st.rerun()
        with col_edit:
            if st.button("✏️", key=f"edit_{task['id']}", help="Edit"):
                st.session_state.editing_id = None if st.session_state.editing_id == task["id"] else task["id"]
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{task['id']}", help="Delete"):
                st.session_state.confirm_delete_id = task["id"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.confirm_delete_id == task["id"]:
        st.warning(f"Delete “{task['title']}”? This can't be undone.")
        dc1, dc2 = st.columns(2)
        if dc1.button("Yes, delete", key=f"confirmdel_{task['id']}", type="primary", use_container_width=True):
            delete_task(task["id"])
            st.rerun()
        if dc2.button("Cancel", key=f"canceldel_{task['id']}", use_container_width=True):
            st.session_state.confirm_delete_id = None
            st.rerun()

    if st.session_state.editing_id == task["id"]:
        with st.form(f"edit_form_{task['id']}"):
            st.markdown(f"**Editing: {task['title']}**")
            new_title = st.text_input("Task name", value=task["title"])
            new_owner = st.text_input("Person", value=task["owner"])
            e1, e2 = st.columns(2)
            with e1:
                new_date = st.date_input("Deadline date", value=task["deadline"].date() if task["deadline"] else date.today())
            with e2:
                new_time = st.time_input("Deadline time", value=task["deadline"].time() if task["deadline"] else dtime(18, 0))
            e3, e4 = st.columns(2)
            with e3:
                new_priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(task["priority"]))
            with e4:
                new_status = st.selectbox("Status", STATUSES, index=STATUSES.index(task["status"]))
            new_notes = st.text_area("Notes", value=task["notes"], height=70)

            s1, s2 = st.columns(2)
            save = s1.form_submit_button("💾 Save", use_container_width=True, type="primary")
            cancel = s2.form_submit_button("Cancel", use_container_width=True)

            if save:
                if not new_title.strip():
                    st.warning("Task name can't be empty.")
                else:
                    idx = find_index_by_id(task["id"])
                    st.session_state.tasks[idx].update({
                        "title": new_title.strip(),
                        "owner": new_owner.strip() if new_owner and new_owner.strip() else "You",
                        "deadline": datetime.combine(new_date, new_time),
                        "priority": new_priority,
                        "status": new_status,
                        "notes": new_notes.strip(),
                    })
                    st.session_state.editing_id = None
                    st.toast("Saved", icon="💾")
                    st.rerun()
            if cancel:
                st.session_state.editing_id = None
                st.rerun()


def filter_tasks(tasks: list, status_filter, priority_filter, search: str) -> list:
    search = search.lower().strip()
    return [
        t for t in tasks
        if t["status"] in status_filter
        and t["priority"] in priority_filter
        and (not search or search in t["title"].lower() or search in t["owner"].lower())
    ]


def render_board_view(visible: list) -> None:
    cols = st.columns(3)
    for col, status_name in zip(cols, STATUSES):
        with col:
            st.markdown(f"#### {STATUS_EMOJI[status_name]} {status_name}")
            col_tasks = [t for t in visible if t["status"] == status_name]
            if not col_tasks:
                st.caption("Nothing here.")
            for t in col_tasks:
                overdue_mark = "⚠️ " if is_overdue(t) else ""
                st.markdown(
                    f'<div class="pz-board-card">'
                    f'<b>{overdue_mark}{t["title"]}</b><br>'
                    f'<span class="pz-chip">{t["priority"]}</span>'
                    f'<span class="pz-chip">👤 {t["owner"]}</span>'
                    f'<div class="pz-deadline" style="font-size:0.78rem;color:var(--pz-dim);margin-top:4px;">{format_deadline(t)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def main() -> None:
    inject_css()
    init_state()
    seed_demo_tasks()

    st.markdown('<div class="pz-title">my_<span>Taskz</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pz-sub">Your own private task list — nobody else visiting this page can see it.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="pz-note">Works best with your browser set to light theme — '
        "dark mode can make some text hard to read.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="pz-nudge"><span class="arrow">»</span> '
        "Tap the arrow to add a task, and scroll for more</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    status_filter, priority_filter, search, sort_by = render_sidebar()
    visible = sort_tasks(filter_tasks(st.session_state.tasks, status_filter, priority_filter, search), sort_by)

    tab_list, tab_board = st.tabs(["📋 List view", "🗂️ Board view"])

    with tab_list:
        if not visible:
            msg = "No tasks yet.<br>Add your first one from the sidebar 👈" if not st.session_state.tasks else "No tasks match your filters."
            st.markdown(f'<div class="pz-empty">{msg}</div>', unsafe_allow_html=True)
        else:
            for task in visible:
                render_task_card(task)

    with tab_board:
        render_board_view(visible)


if __name__ == "__main__":
    main()