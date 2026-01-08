# CrossFit PR Tracker 🏋️

A Streamlit-based web application to track Personal Records (PRs) for CrossFit weightlifting movements and benchmark workouts.

## Features

- **Weightlifting PR Tracking**: Record and track PRs for 15+ weightlifting movements including:
  - Olympic lifts (Snatch, Clean & Jerk)
  - Powerlifts (Squat, Deadlift, Bench Press)
  - CrossFit movements (Thruster, Push Press, etc.)

- **Benchmark Workout Tracking**: Track completion times for 20+ classic CrossFit benchmark workouts:
  - Girls (Fran, Cindy, Helen, etc.)
  - Heroes (Murph, DT, etc.)
  - Other benchmarks (Fight Gone Bad, Filthy Fifty, etc.)

- **Progress Visualization**: Interactive charts showing your improvement over time

- **Dashboard**: Quick view of all your current PRs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/xaramillo/crossfit.git
cd crossfit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Use the tabs to:
   - **Dashboard**: View all your current PRs
   - **Weightlifts**: Add and track weightlifting PRs
   - **Benchmarks**: Add and track benchmark workout times
   - **Progress**: Visualize your improvement over time

## Data Storage

- PRs are stored locally in JSON files:
  - `weightlifts_prs.json`: Weightlifting PR data
  - `benchmarks_prs.json`: Benchmark workout data

- Data persists between sessions

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- pandas >= 2.0.0
- plotly >= 5.17.0

## License

MIT License
