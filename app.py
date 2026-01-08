import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# File paths for data storage
WEIGHTLIFTS_DATA_FILE = "weightlifts_prs.json"
BENCHMARKS_DATA_FILE = "benchmarks_prs.json"

# Define weightlifting movements
WEIGHTLIFTS = [
    "Back Squat",
    "Front Squat",
    "Overhead Squat",
    "Deadlift",
    "Bench Press",
    "Shoulder Press",
    "Push Press",
    "Push Jerk",
    "Clean",
    "Clean & Jerk",
    "Snatch",
    "Power Clean",
    "Power Snatch",
    "Thruster",
    "Sumo Deadlift High Pull"
]

# Define benchmark workouts
BENCHMARK_WORKOUTS = [
    "Fran",
    "Cindy",
    "Murph",
    "Helen",
    "Diane",
    "Grace",
    "Isabel",
    "Karen",
    "Annie",
    "Chelsea",
    "DT",
    "Jackie",
    "Mary",
    "Nancy",
    "Eva",
    "Filthy Fifty",
    "Fight Gone Bad",
    "The Seven",
    "Badger",
    "King Kong"
]

def load_data(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def add_weightlift_pr(movement, weight, unit, notes=""):
    """Add a new weightlift PR"""
    data = load_data(WEIGHTLIFTS_DATA_FILE)
    entry = {
        "id": len(data) + 1,
        "movement": movement,
        "weight": weight,
        "unit": unit,
        "notes": notes,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(entry)
    save_data(data, WEIGHTLIFTS_DATA_FILE)
    return True

def add_benchmark_pr(workout, time_minutes, time_seconds, rounds, reps, notes=""):
    """Add a new benchmark PR"""
    data = load_data(BENCHMARKS_DATA_FILE)
    entry = {
        "id": len(data) + 1,
        "workout": workout,
        "time_minutes": time_minutes,
        "time_seconds": time_seconds,
        "rounds": rounds,
        "reps": reps,
        "notes": notes,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(entry)
    save_data(data, BENCHMARKS_DATA_FILE)
    return True

def get_current_prs_weightlifts():
    """Get current PRs for all weightlifts"""
    data = load_data(WEIGHTLIFTS_DATA_FILE)
    if not data:
        return {}
    
    prs = {}
    for entry in data:
        movement = entry["movement"]
        if movement not in prs or entry["weight"] > prs[movement]["weight"]:
            prs[movement] = entry
    
    return prs

def get_current_prs_benchmarks():
    """Get current PRs (best times) for all benchmarks"""
    data = load_data(BENCHMARKS_DATA_FILE)
    if not data:
        return {}
    
    prs = {}
    for entry in data:
        workout = entry["workout"]
        total_seconds = entry["time_minutes"] * 60 + entry["time_seconds"]
        
        if workout not in prs:
            prs[workout] = entry
        else:
            current_total = prs[workout]["time_minutes"] * 60 + prs[workout]["time_seconds"]
            if total_seconds < current_total and total_seconds > 0:
                prs[workout] = entry
    
    return prs

def delete_entry(entry_id, filename):
    """Delete an entry by ID"""
    data = load_data(filename)
    data = [entry for entry in data if entry["id"] != entry_id]
    save_data(data, filename)
    return True

# Streamlit App Configuration
st.set_page_config(
    page_title="CrossFit PR Tracker",
    page_icon="🏋️",
    layout="wide"
)

# Main Title
st.title("🏋️ CrossFit PR Tracker")
st.markdown("Track your Personal Records for weightlifts and benchmark workouts")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "💪 Weightlifts",
    "⏱️ Benchmarks",
    "📈 Progress"
])

# Dashboard Tab
with tab1:
    st.header("Your Current PRs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏋️ Weightlifting PRs")
        weightlift_prs = get_current_prs_weightlifts()
        
        if weightlift_prs:
            for movement, pr in sorted(weightlift_prs.items()):
                st.metric(
                    label=movement,
                    value=f"{pr['weight']} {pr['unit']}",
                    delta=f"Set on {pr['date'][:10]}"
                )
        else:
            st.info("No weightlifting PRs recorded yet. Add your first PR in the Weightlifts tab!")
    
    with col2:
        st.subheader("⏱️ Benchmark PRs")
        benchmark_prs = get_current_prs_benchmarks()
        
        if benchmark_prs:
            for workout, pr in sorted(benchmark_prs.items()):
                time_display = f"{pr['time_minutes']}:{pr['time_seconds']:02d}"
                rounds_display = f" ({pr['rounds']} rounds + {pr['reps']} reps)" if pr.get('rounds', 0) > 0 else ""
                st.metric(
                    label=workout,
                    value=time_display + rounds_display,
                    delta=f"Set on {pr['date'][:10]}"
                )
        else:
            st.info("No benchmark PRs recorded yet. Add your first PR in the Benchmarks tab!")

# Weightlifts Tab
with tab2:
    st.header("💪 Weightlifting PRs")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Weightlifting PR")
        
        with st.form("weightlift_form"):
            movement = st.selectbox("Select Movement", WEIGHTLIFTS)
            
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                weight = st.number_input("Weight", min_value=0.0, step=2.5, format="%.1f")
            with col_w2:
                unit = st.selectbox("Unit", ["lbs", "kg"])
            
            notes = st.text_area("Notes (optional)", placeholder="e.g., Felt strong today!")
            
            submitted = st.form_submit_button("Record PR")
            
            if submitted:
                if weight > 0:
                    add_weightlift_pr(movement, weight, unit, notes)
                    st.success(f"✅ Added {weight} {unit} {movement} PR!")
                    st.rerun()
                else:
                    st.error("Please enter a valid weight")
    
    with col2:
        st.subheader("PR History")
        
        data = load_data(WEIGHTLIFTS_DATA_FILE)
        
        if data:
            # Filter by movement
            movement_filter = st.selectbox(
                "Filter by movement",
                ["All"] + WEIGHTLIFTS,
                key="weightlift_filter"
            )
            
            filtered_data = data if movement_filter == "All" else [
                entry for entry in data if entry["movement"] == movement_filter
            ]
            
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                df = df.sort_values("date", ascending=False)
                
                # Display as table
                st.dataframe(
                    df[["date", "movement", "weight", "unit", "notes"]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Delete functionality
                st.subheader("Delete Entry")
                entry_to_delete = st.selectbox(
                    "Select entry to delete",
                    options=[(e["id"], f"{e['date']} - {e['movement']} {e['weight']} {e['unit']}") 
                             for e in filtered_data],
                    format_func=lambda x: x[1],
                    key="delete_weightlift"
                )
                
                if st.button("Delete Selected Entry", key="delete_weightlift_btn"):
                    delete_entry(entry_to_delete[0], WEIGHTLIFTS_DATA_FILE)
                    st.success("Entry deleted!")
                    st.rerun()
            else:
                st.info("No entries found for this filter")
        else:
            st.info("No weightlifting PRs recorded yet")

# Benchmarks Tab
with tab3:
    st.header("⏱️ Benchmark Workouts")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Benchmark PR")
        
        with st.form("benchmark_form"):
            workout = st.selectbox("Select Workout", BENCHMARK_WORKOUTS)
            
            st.markdown("**Time to Complete**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                time_minutes = st.number_input("Minutes", min_value=0, step=1)
            with col_t2:
                time_seconds = st.number_input("Seconds", min_value=0, max_value=59, step=1)
            
            st.markdown("**For AMRAP workouts (leave at 0 for time-based)**")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                rounds = st.number_input("Rounds", min_value=0, step=1)
            with col_r2:
                reps = st.number_input("Reps", min_value=0, step=1)
            
            notes = st.text_area("Notes (optional)", placeholder="e.g., RX or scaled?", key="benchmark_notes")
            
            submitted = st.form_submit_button("Record PR")
            
            if submitted:
                if time_minutes > 0 or time_seconds > 0 or rounds > 0:
                    add_benchmark_pr(workout, time_minutes, time_seconds, rounds, reps, notes)
                    st.success(f"✅ Added {workout} PR!")
                    st.rerun()
                else:
                    st.error("Please enter valid time or rounds")
    
    with col2:
        st.subheader("PR History")
        
        data = load_data(BENCHMARKS_DATA_FILE)
        
        if data:
            # Filter by workout
            workout_filter = st.selectbox(
                "Filter by workout",
                ["All"] + BENCHMARK_WORKOUTS,
                key="benchmark_filter"
            )
            
            filtered_data = data if workout_filter == "All" else [
                entry for entry in data if entry["workout"] == workout_filter
            ]
            
            if filtered_data:
                df = pd.DataFrame(filtered_data)
                df = df.sort_values("date", ascending=False)
                df["time"] = df.apply(lambda row: f"{row['time_minutes']}:{row['time_seconds']:02d}", axis=1)
                
                # Display as table
                display_cols = ["date", "workout", "time", "rounds", "reps", "notes"]
                st.dataframe(
                    df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Delete functionality
                st.subheader("Delete Entry")
                entry_to_delete = st.selectbox(
                    "Select entry to delete",
                    options=[(e["id"], f"{e['date']} - {e['workout']} {e['time_minutes']}:{e['time_seconds']:02d}") 
                             for e in filtered_data],
                    format_func=lambda x: x[1],
                    key="delete_benchmark"
                )
                
                if st.button("Delete Selected Entry", key="delete_benchmark_btn"):
                    delete_entry(entry_to_delete[0], BENCHMARKS_DATA_FILE)
                    st.success("Entry deleted!")
                    st.rerun()
            else:
                st.info("No entries found for this filter")
        else:
            st.info("No benchmark PRs recorded yet")

# Progress Tab
with tab4:
    st.header("📈 Progress Tracking")
    
    # Weightlifts Progress
    st.subheader("Weightlifting Progress")
    
    weightlift_data = load_data(WEIGHTLIFTS_DATA_FILE)
    
    if weightlift_data:
        movement_for_chart = st.selectbox(
            "Select movement to track",
            WEIGHTLIFTS,
            key="progress_movement"
        )
        
        movement_history = [e for e in weightlift_data if e["movement"] == movement_for_chart]
        
        if movement_history:
            df = pd.DataFrame(movement_history)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            # Create line chart
            fig = px.line(
                df,
                x="date",
                y="weight",
                title=f"{movement_for_chart} Progress Over Time",
                markers=True,
                labels={"weight": f"Weight ({df.iloc[0]['unit']})", "date": "Date"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current PR", f"{df.iloc[-1]['weight']} {df.iloc[-1]['unit']}")
            with col2:
                st.metric("Starting Weight", f"{df.iloc[0]['weight']} {df.iloc[0]['unit']}")
            with col3:
                improvement = df.iloc[-1]['weight'] - df.iloc[0]['weight']
                st.metric("Total Improvement", f"+{improvement} {df.iloc[0]['unit']}")
        else:
            st.info(f"No data recorded for {movement_for_chart} yet")
    else:
        st.info("No weightlifting data recorded yet")
    
    st.markdown("---")
    
    # Benchmarks Progress
    st.subheader("Benchmark Workout Progress")
    
    benchmark_data = load_data(BENCHMARKS_DATA_FILE)
    
    if benchmark_data:
        workout_for_chart = st.selectbox(
            "Select workout to track",
            BENCHMARK_WORKOUTS,
            key="progress_benchmark"
        )
        
        workout_history = [e for e in benchmark_data if e["workout"] == workout_for_chart]
        
        if workout_history:
            df = pd.DataFrame(workout_history)
            df["date"] = pd.to_datetime(df["date"])
            df["total_seconds"] = df["time_minutes"] * 60 + df["time_seconds"]
            df = df.sort_values("date")
            
            # Create line chart
            fig = px.line(
                df,
                x="date",
                y="total_seconds",
                title=f"{workout_for_chart} Progress Over Time",
                markers=True,
                labels={"total_seconds": "Time (seconds)", "date": "Date"}
            )
            
            # Invert y-axis since lower time is better
            fig.update_yaxes(autorange="reversed")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                best = df.loc[df["total_seconds"].idxmin()]
                st.metric("Best Time", f"{int(best['time_minutes'])}:{int(best['time_seconds']):02d}")
            with col2:
                first = df.iloc[0]
                st.metric("First Attempt", f"{int(first['time_minutes'])}:{int(first['time_seconds']):02d}")
            with col3:
                improvement = df.iloc[0]['total_seconds'] - df.iloc[-1]['total_seconds']
                st.metric("Time Saved", f"-{int(improvement)}s")
        else:
            st.info(f"No data recorded for {workout_for_chart} yet")
    else:
        st.info("No benchmark data recorded yet")

# Footer
st.markdown("---")
st.markdown("💪 Keep crushing those PRs! 🏋️")
