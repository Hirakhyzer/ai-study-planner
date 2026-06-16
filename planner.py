"""Core planning logic for the AI Study Planner app."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

DIFFICULTY_WEIGHT = {"Easy": 1.0, "Medium": 1.35, "Hard": 1.75}
CONFIDENCE_WEIGHT = {"High": 0.85, "Medium": 1.15, "Low": 1.55}


@dataclass
class Subject:
    name: str
    exam_date: date
    difficulty: str
    confidence: str
    syllabus_units: int
    completed_units: int = 0

    @property
    def remaining_units(self) -> int:
        return max(0, self.syllabus_units - self.completed_units)

    @property
    def progress_percent(self) -> int:
        if self.syllabus_units <= 0:
            return 0
        return round((self.completed_units / self.syllabus_units) * 100)


@dataclass
class SubjectPlan:
    subject: Subject
    days_left: int
    urgency: str
    priority_score: float
    estimated_hours: float
    daily_average_hours: float
    progress_percent: int


@dataclass
class StudyBlock:
    study_date: date
    subject: str
    hours: float
    focus: str
    urgency: str


@dataclass
class StudyPlan:
    generated_on: date
    daily_available_hours: float
    subject_plans: list[SubjectPlan]
    schedule: list[StudyBlock]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "generated_on": self.generated_on.isoformat(),
            "daily_available_hours": self.daily_available_hours,
            "subject_plans": [
                {
                    **asdict(item),
                    "subject": {
                        **asdict(item.subject),
                        "exam_date": item.subject.exam_date.isoformat(),
                    },
                }
                for item in self.subject_plans
            ],
            "schedule": [
                {**asdict(block), "study_date": block.study_date.isoformat()}
                for block in self.schedule
            ],
            "warnings": self.warnings,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_text(self) -> str:
        lines = [
            "AI Study Planner Report",
            "=======================",
            f"Generated on: {self.generated_on.isoformat()}",
            f"Daily available hours: {self.daily_available_hours}",
            "",
            "Subject priorities:",
        ]
        for item in self.subject_plans:
            lines.append(
                f"- {item.subject.name}: {item.urgency}, {item.days_left} days left, "
                f"{item.estimated_hours:.1f} estimated hours, {item.progress_percent}% complete"
            )
        lines.append("")
        lines.append("Study schedule:")
        for block in self.schedule:
            lines.append(
                f"- {block.study_date.isoformat()}: {block.subject} for {block.hours:.1f}h "
                f"({block.focus}, {block.urgency})"
            )
        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in self.warnings)
        return "\n".join(lines) + "\n"


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def load_subjects_from_csv(path: str | Path) -> list[Subject]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return [
            Subject(
                name=row["name"],
                exam_date=parse_date(row["exam_date"]),
                difficulty=row["difficulty"],
                confidence=row["confidence"],
                syllabus_units=int(row["syllabus_units"]),
                completed_units=int(row.get("completed_units", 0) or 0),
            )
            for row in rows
        ]


def urgency_label(days_left: int) -> str:
    if days_left <= 3:
        return "Critical"
    if days_left <= 7:
        return "High"
    if days_left <= 14:
        return "Medium"
    return "Low"


def estimate_hours(subject: Subject) -> float:
    difficulty = DIFFICULTY_WEIGHT.get(subject.difficulty, 1.35)
    confidence = CONFIDENCE_WEIGHT.get(subject.confidence, 1.15)
    return max(1.0, subject.remaining_units * 1.5 * difficulty * confidence)


def build_subject_plan(subject: Subject, today: date) -> SubjectPlan:
    days_left = max(0, (subject.exam_date - today).days)
    urgency_factor = 1 / max(1, days_left)
    hours = estimate_hours(subject)
    priority = hours * (1 + urgency_factor * 10)
    daily_average = hours / max(1, days_left)
    return SubjectPlan(
        subject=subject,
        days_left=days_left,
        urgency=urgency_label(days_left),
        priority_score=round(priority, 2),
        estimated_hours=round(hours, 1),
        daily_average_hours=round(daily_average, 2),
        progress_percent=subject.progress_percent,
    )


def choose_focus(subject: Subject) -> str:
    if subject.completed_units == 0:
        return "Start core concepts"
    if subject.progress_percent < 50:
        return "Cover remaining syllabus"
    if subject.progress_percent < 80:
        return "Practice problems and weak areas"
    return "Revision and mock test"


def generate_schedule(subject_plans: list[SubjectPlan], today: date, daily_available_hours: float, max_days: int = 30) -> list[StudyBlock]:
    schedule: list[StudyBlock] = []
    active = [item for item in subject_plans if item.days_left >= 0 and item.subject.remaining_units > 0]
    if not active or daily_available_hours <= 0:
        return schedule

    planning_days = min(max_days, max(1, max(item.days_left for item in active)))
    remaining = {item.subject.name: item.estimated_hours for item in active}

    for day_offset in range(planning_days):
        current_day = today + timedelta(days=day_offset)
        todays_candidates = [
            item for item in active
            if item.subject.exam_date >= current_day and remaining[item.subject.name] > 0
        ]
        todays_candidates.sort(key=lambda item: (item.days_left, -item.priority_score))
        hours_left_today = daily_available_hours

        for item in todays_candidates[:3]:
            if hours_left_today <= 0:
                break
            recommended = min(
                remaining[item.subject.name],
                max(0.5, min(2.0, item.daily_average_hours + 0.5)),
                hours_left_today,
            )
            recommended = round(recommended * 2) / 2
            if recommended <= 0:
                continue
            schedule.append(
                StudyBlock(
                    study_date=current_day,
                    subject=item.subject.name,
                    hours=recommended,
                    focus=choose_focus(item.subject),
                    urgency=item.urgency,
                )
            )
            remaining[item.subject.name] = max(0, remaining[item.subject.name] - recommended)
            hours_left_today = round(hours_left_today - recommended, 2)

    return schedule


def build_study_plan(subjects: list[Subject], daily_available_hours: float, today: date | None = None) -> StudyPlan:
    today = today or date.today()
    subject_plans = [build_subject_plan(subject, today) for subject in subjects]
    subject_plans.sort(key=lambda item: (-item.priority_score, item.days_left))
    schedule = generate_schedule(subject_plans, today, daily_available_hours)

    warnings = []
    if not subjects:
        warnings.append("Add at least one subject to generate a study plan.")
    if daily_available_hours <= 0:
        warnings.append("Daily available study hours must be greater than zero.")
    for item in subject_plans:
        if item.subject.exam_date < today:
            warnings.append(f"{item.subject.name} exam date is in the past.")
        if item.daily_average_hours > daily_available_hours:
            warnings.append(
                f"{item.subject.name} may need {item.daily_average_hours:.1f}h/day, "
                f"which is higher than your available {daily_available_hours:.1f}h/day."
            )

    return StudyPlan(
        generated_on=today,
        daily_available_hours=daily_available_hours,
        subject_plans=subject_plans,
        schedule=schedule,
        warnings=warnings,
    )
