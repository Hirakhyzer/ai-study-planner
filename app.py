from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from planner import Subject, build_study_plan, load_subjects_from_csv

BASE_DIR = Path(__file__).parent
SAMPLE_FILE = BASE_DIR / "sample_data" / "sample_subjects.csv"

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.main {
    background: linear-gradient(135deg, #f8fbff 0%, #eef2ff 48%, #fff7ed 100%);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 2.3rem;
    border-radius: 30px;
    background: radial-gradient(circle at top left, rgba(34,197,94,.25), transparent 32%),
                radial-gradient(circle at bottom right, rgba(59,130,246,.24), transparent 36%),
                linear-gradient(135deg, rgba(15,23,42,.97), rgba(30,41,59,.94));
    color: white;
    box-shadow: 0 20px 50px rgba(15, 23, 42, .14);
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-size: 3.1rem;
    line-height: 1.04;
    margin-bottom: .6rem;
}
.hero p {
    font-size: 1.08rem;
    color: rgba(255,255,255,.82);
    max-width: 920px;
}
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1rem;
}
.badge {
    padding: .45rem .75rem;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.20);
    font-size: .86rem;
}
.card {
    padding: 1.15rem;
    border-radius: 24px;
    background: rgba(255,255,255,.84);
    border: 1px solid rgba(148,163,184,.24);
    box-shadow: 0 14px 34px rgba(15,23,42,.08);
    min-height: 138px;
}
.card-label {
    font-size: .84rem;
    color: #64748b;
    margin-bottom: .35rem;
}
.card-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
}
.card-help {
    font-size: .88rem;
    color: #64748b;
    margin-top: .3rem;
}
.count-card {
    padding: 1rem;
    border-radius: 22px;
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(148,163,184,.25);
    box-shadow: 0 12px 28px rgba(15,23,42,.07);
    margin-bottom: .75rem;
}
.count-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f172a;
}
.count-meta {
    color: #64748b;
    font-size: .9rem;
}
.chip-critical, .chip-high, .chip-medium, .chip-low {
    display: inline-block;
    padding: .32rem .65rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: .78rem;
}
.chip-critical { background: #fee2e2; color: #991b1b; }
.chip-high { background: #ffedd5; color: #9a3412; }
.chip-medium { background: #fef9c3; color: #854d0e; }
.chip-low { background: #dcfce7; color: #166534; }
.timeline-item {
    padding: .85rem 1rem;
    border-left: 4px solid #2563eb;
    background: rgba(255,255,255,.82);
    border-radius: 16px;
    margin-bottom: .7rem;
    box-shadow: 0 8px 22px rgba(15,23,42,.06);
}
.small-note {
    color: #64748b;
    font-size: .92rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def urgency_chip(label: str) -> str:
    css_name = label.lower()
    return f'<span class="chip-{css_name}">{label}</span>'


def default_subjects() -> list[dict]:
    start = date.today()
    return [
        {"name": "Machine Learning", "exam_date": start + timedelta(days=12), "difficulty": "Hard", "confidence": "Medium", "syllabus_units": 10, "completed_units": 3},
        {"name": "Database Systems", "exam_date": start + timedelta(days=8), "difficulty": "Medium", "confidence": "High", "syllabus_units": 8, "completed_units": 4},
        {"name": "Software Engineering", "exam_date": start + timedelta(days=18), "difficulty": "Medium", "confidence": "Medium", "syllabus_units": 9, "completed_units": 5},
    ]


def subjects_from_editor(rows: list[dict]) -> list[Subject]:
    subjects = []
    for row in rows:
        if not str(row.get("name", "")).strip():
            continue
        subjects.append(
            Subject(
                name=str(row["name"]).strip(),
                exam_date=row["exam_date"],
                difficulty=str(row["difficulty"]),
                confidence=str(row["confidence"]),
                syllabus_units=max(1, int(row["syllabus_units"])),
                completed_units=max(0, int(row["completed_units"])),
            )
        )
    return subjects


with st.sidebar:
    st.title("📚 Planner Controls")
    st.caption("Create a realistic study plan based on exams, difficulty, confidence, and time.")
    daily_hours = st.slider("Daily available study hours", 1.0, 12.0, 4.0, 0.5)
    st.divider()
    load_sample = st.button("Load sample subjects", use_container_width=True)
    st.divider()
    st.markdown("### Planning formula")
    st.write("Urgency + difficulty + confidence + remaining syllabus")
    st.info("Lower confidence and closer exam dates automatically increase priority.")

if load_sample or "subject_rows" not in st.session_state:
    if SAMPLE_FILE.exists() and load_sample:
        loaded = load_subjects_from_csv(SAMPLE_FILE)
        st.session_state["subject_rows"] = [
            {
                "name": item.name,
                "exam_date": item.exam_date,
                "difficulty": item.difficulty,
                "confidence": item.confidence,
                "syllabus_units": item.syllabus_units,
                "completed_units": item.completed_units,
            }
            for item in loaded
        ]
    else:
        st.session_state["subject_rows"] = default_subjects()

st.markdown(
    """
    <div class="hero">
      <h1>AI Study Planner</h1>
      <p>Build a smart exam countdown and daily study schedule that adjusts to urgency, subject difficulty, confidence level, and your available hours.</p>
      <div class="badge-row">
        <span class="badge">Countdown dashboard</span>
        <span class="badge">Priority scoring</span>
        <span class="badge">Daily schedule</span>
        <span class="badge">Progress tracking</span>
        <span class="badge">Export reports</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. Add your subjects")
st.caption("Edit the table below. Each row becomes part of the generated plan.")

edited_rows = st.data_editor(
    st.session_state["subject_rows"],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "name": st.column_config.TextColumn("Subject"),
        "exam_date": st.column_config.DateColumn("Exam date"),
        "difficulty": st.column_config.SelectboxColumn("Difficulty", options=["Easy", "Medium", "Hard"]),
        "confidence": st.column_config.SelectboxColumn("Confidence", options=["Low", "Medium", "High"]),
        "syllabus_units": st.column_config.NumberColumn("Total units", min_value=1, max_value=50, step=1),
        "completed_units": st.column_config.NumberColumn("Completed units", min_value=0, max_value=50, step=1),
    },
)

subjects = subjects_from_editor(edited_rows)
plan = build_study_plan(subjects, daily_available_hours=daily_hours)

st.markdown("## 2. Dashboard")

metric_a, metric_b, metric_c, metric_d = st.columns(4)
next_exam = min((item.exam_date for item in subjects), default=None)
total_units = sum(item.syllabus_units for item in subjects)
completed_units = sum(item.completed_units for item in subjects)
progress = round((completed_units / total_units) * 100) if total_units else 0
planned_hours = round(sum(item.estimated_hours for item in plan.subject_plans), 1)

cards = [
    (metric_a, "Subjects", len(subjects), "Total subjects in plan"),
    (metric_b, "Next Exam", (next_exam - date.today()).days if next_exam else 0, "Days remaining"),
    (metric_c, "Progress", f"{progress}%", "Syllabus completed"),
    (metric_d, "Study Load", f"{planned_hours}h", "Estimated total hours"),
]

for col, label, value, help_text in cards:
    with col:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">{label}</div>
                <div class="card-value">{value}</div>
                <div class="card-help">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if plan.warnings:
    st.markdown("### Planning warnings")
    for warning in plan.warnings:
        st.warning(warning)

left, right = st.columns([0.95, 1.25], gap="large")

with left:
    st.markdown("### Exam countdown")
    for item in sorted(plan.subject_plans, key=lambda entry: entry.days_left):
        st.markdown(
            f"""
            <div class="count-card">
                <div class="count-title">{item.subject.name}</div>
                <div class="count-meta">Exam: {item.subject.exam_date.isoformat()} · {item.days_left} days left</div>
                <div style="margin-top:.55rem;">{urgency_chip(item.urgency)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(1.0, item.progress_percent / 100))

with right:
    st.markdown("### Subject priorities")
    priority_rows = [
        {
            "Subject": item.subject.name,
            "Urgency": item.urgency,
            "Days left": item.days_left,
            "Progress": f"{item.progress_percent}%",
            "Estimated hours": item.estimated_hours,
            "Avg h/day": item.daily_average_hours,
            "Priority": item.priority_score,
        }
        for item in plan.subject_plans
    ]
    st.dataframe(priority_rows, use_container_width=True, hide_index=True)

st.markdown("## 3. Daily study schedule")

if plan.schedule:
    grouped = {}
    for block in plan.schedule:
        grouped.setdefault(block.study_date, []).append(block)

    for study_day, blocks in list(grouped.items())[:14]:
        st.markdown(f"### {study_day.strftime('%A, %b %d')}")
        for block in blocks:
            st.markdown(
                f"""
                <div class="timeline-item">
                    <strong>{block.subject}</strong> · {block.hours:.1f} hours · {block.focus}<br>
                    <span class="small-note">Urgency: {block.urgency}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info("Add subjects with future exam dates to generate a schedule.")

st.markdown("## 4. Export your plan")
export_col1, export_col2 = st.columns(2)
with export_col1:
    st.download_button(
        "Download JSON plan",
        data=plan.to_json(),
        file_name="study_plan.json",
        mime="application/json",
        use_container_width=True,
    )
with export_col2:
    st.download_button(
        "Download text plan",
        data=plan.to_text(),
        file_name="study_plan.txt",
        mime="text/plain",
        use_container_width=True,
    )
