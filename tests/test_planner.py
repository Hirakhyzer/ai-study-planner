from datetime import date, timedelta

from planner import Subject, build_study_plan, estimate_hours, urgency_label


def test_urgency_label():
    assert urgency_label(2) == "Critical"
    assert urgency_label(6) == "High"
    assert urgency_label(12) == "Medium"
    assert urgency_label(20) == "Low"


def test_estimate_hours_harder_subject_needs_more_time():
    easy = Subject("Easy Course", date(2026, 7, 20), "Easy", "High", 10, 5)
    hard = Subject("Hard Course", date(2026, 7, 20), "Hard", "Low", 10, 5)
    assert estimate_hours(hard) > estimate_hours(easy)


def test_build_study_plan_creates_schedule():
    today = date(2026, 6, 16)
    subjects = [
        Subject("Machine Learning", today + timedelta(days=10), "Hard", "Low", 10, 2),
        Subject("Database Systems", today + timedelta(days=15), "Medium", "Medium", 8, 4),
    ]
    plan = build_study_plan(subjects, daily_available_hours=4.0, today=today)
    assert len(plan.subject_plans) == 2
    assert plan.subject_plans[0].priority_score >= plan.subject_plans[1].priority_score
    assert len(plan.schedule) > 0
    assert plan.schedule[0].hours <= 4.0


def test_export_contains_subject_name():
    today = date(2026, 6, 16)
    subject = Subject("Research Methods", today + timedelta(days=5), "Easy", "High", 6, 2)
    plan = build_study_plan([subject], daily_available_hours=2.0, today=today)
    assert "Research Methods" in plan.to_text()
    assert "Research Methods" in plan.to_json()
