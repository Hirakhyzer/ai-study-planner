# AI Study Planner

A polished Streamlit app that helps students create a realistic study schedule from subjects, exam dates, difficulty levels, confidence levels, and daily available study hours.

The app turns exam deadlines into a prioritized study plan with countdown cards, daily tasks, workload estimates, progress tracking, and downloadable reports.

## Features

- Beautiful Streamlit dashboard UI
- Exam countdown cards
- Subject priority scoring
- Auto-generated day-by-day study schedule
- Difficulty and confidence-aware planning
- Daily study-hour allocation
- Urgency labels: Critical, High, Medium, Low
- Downloadable TXT and JSON study plans
- Built-in sample subjects
- Core planner logic separated from UI
- Unit tests and GitHub Actions workflow

## Tech Stack

- Python
- Streamlit
- Standard-library planning logic
- Pytest

## Project Structure

```text
ai-study-planner/
├── app.py
├── planner.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── sample_data/
│   └── sample_subjects.csv
├── tests/
│   └── test_planner.py
└── .github/
    └── workflows/
        └── python-tests.yml
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest
```

## How It Works

The planner calculates urgency from exam dates, combines it with difficulty and confidence level, estimates total study load, and distributes study blocks across available days. Harder subjects, closer exams, and lower confidence receive higher priority.

## Portfolio Notes

This project is designed for a real-world student problem and demonstrates UI/UX design, scheduling logic, data handling, export features, testing, and clean GitHub documentation.
