"""
CrossFit PR Tracker - Multi-User Application with Role-Based Access Control
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
import db
import auth

# Initialize database and ensure default admin exists
db.init_database()
auth.ensure_default_admin()

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

# Streamlit App Configuration
st.set_page_config(
    page_title="CrossFit PR Tracker",
    page_icon="🏋️",
    layout="wide"
)

# Initialize session state
auth.init_session_state()


def show_login_page():
    """Display login and registration page"""
    st.title("🏋️ CrossFit PR Tracker")
    st.markdown("### Welcome! Please login or register to continue")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user = auth.login_user(username, password)
                    if user:
                        auth.set_authenticated_user(user)
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        # Show default admin credentials hint on first run
        if not db.get_all_users() or len(db.get_all_users()) == 1:
            st.info("💡 **First time setup**: Default admin credentials are username: `admin`, password: `admin`. Please change the password after logging in!")
    
    with tab2:
        st.subheader("Register New Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            full_name = st.text_input("Full Name (optional)", key="reg_fullname")
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if new_username and new_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        if auth.register_user(new_username, new_password, full_name or None):
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Username already exists")
                else:
                    st.error("Please enter username and password")


def show_user_header():
    """Display user info and logout button"""
    user = auth.get_current_user()
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("🏋️ CrossFit PR Tracker")
    
    with col2:
        display_name = user.get('full_name') or user['username']
        role_badge = f"[{user['role'].upper()}]"
        st.markdown(f"**{display_name}** {role_badge}")
    
    with col3:
        if st.button("Logout", key="logout_btn"):
            auth.logout()
            st.rerun()


def show_user_management():
    """Display user management interface (admin only)"""
    if not auth.is_admin():
        st.error("Access denied. Admin role required.")
        return
    
    st.header("👥 User Management")
    
    tab1, tab2, tab3 = st.tabs(["All Users", "Create User", "Migration Tool"])
    
    with tab1:
        st.subheader("All Users")
        
        users = db.get_all_users()
        
        if users:
            df = pd.DataFrame(users)
            st.dataframe(
                df[['id', 'username', 'role', 'full_name', 'created_at']],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            st.subheader("Manage User")
            
            user_options = [(u['id'], f"{u['username']} ({u['role']})") for u in users]
            selected_user = st.selectbox(
                "Select user to manage",
                options=user_options,
                format_func=lambda x: x[1]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Change Role**")
                new_role = st.selectbox(
                    "New role",
                    options=['user', 'coach', 'admin'],
                    key="change_role"
                )
                
                if st.button("Update Role"):
                    if db.update_user_role(selected_user[0], new_role):
                        st.success(f"Role updated to {new_role}")
                        st.rerun()
                    else:
                        st.error("Failed to update role")
            
            with col2:
                st.markdown("**Delete User**")
                st.warning("⚠️ This will delete the user and all their data!")
                
                if st.button("Delete User", type="secondary"):
                    if selected_user[0] == auth.get_current_user_id():
                        st.error("You cannot delete your own account")
                    else:
                        if db.delete_user(selected_user[0]):
                            st.success("User deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete user")
        else:
            st.info("No users found")
    
    with tab2:
        st.subheader("Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", options=['user', 'coach', 'admin'])
            new_full_name = st.text_input("Full Name (optional)")
            
            submit = st.form_submit_button("Create User")
            
            if submit:
                if new_username and new_password:
                    password_hash = auth.hash_password(new_password)
                    user_id = db.create_user(
                        new_username, 
                        password_hash, 
                        new_role, 
                        new_full_name or None
                    )
                    
                    if user_id:
                        st.success(f"User '{new_username}' created successfully!")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please enter username and password")
    
    with tab3:
        st.subheader("Migrate JSON Data to Database")
        st.info("This tool migrates existing JSON data files to the database for a specific user.")
        
        users = db.get_all_users()
        if users:
            user_options = [(u['id'], u['username']) for u in users]
            selected_user = st.selectbox(
                "Select user to import data for",
                options=user_options,
                format_func=lambda x: x[1],
                key="migration_user"
            )
            
            weightlifts_file = st.text_input(
                "Weightlifts JSON file", 
                value="weightlifts_prs.json"
            )
            benchmarks_file = st.text_input(
                "Benchmarks JSON file", 
                value="benchmarks_prs.json"
            )
            
            if st.button("Migrate Data"):
                if os.path.exists(weightlifts_file) or os.path.exists(benchmarks_file):
                    w_count, b_count = db.migrate_json_to_db(
                        selected_user[0],
                        weightlifts_file,
                        benchmarks_file
                    )
                    st.success(f"Migrated {w_count} weightlift PRs and {b_count} benchmark PRs for user {selected_user[1]}")
                else:
                    st.error("No JSON files found")
        else:
            st.warning("No users available for migration")


def show_dashboard():
    """Display dashboard with current PRs"""
    st.header("📊 Your Current PRs")
    
    user_id = auth.get_current_user_id()
    
    # For coach/admin, allow viewing other users' data
    if auth.can_view_all_data():
        users = db.get_all_users()
        user_options = [(u['id'], u.get('full_name') or u['username']) for u in users]
        
        selected_user = st.selectbox(
            "View PRs for user:",
            options=user_options,
            format_func=lambda x: x[1],
            index=[i for i, u in enumerate(user_options) if u[0] == user_id][0] if user_id else 0
        )
        
        user_id = selected_user[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏋️ Weightlifting PRs")
        weightlift_prs = db.get_current_prs_weightlifts(user_id)
        
        if weightlift_prs:
            for movement, pr in sorted(weightlift_prs.items()):
                st.metric(
                    label=movement,
                    value=f"{pr['weight']} {pr['unit']}",
                    delta=f"Set on {pr['date'][:10]}"
                )
        else:
            st.info("No weightlifting PRs recorded yet.")
    
    with col2:
        st.subheader("⏱️ Benchmark PRs")
        benchmark_prs = db.get_current_prs_benchmarks(user_id)
        
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
            st.info("No benchmark PRs recorded yet.")


def show_weightlifts():
    """Display weightlifts tab"""
    st.header("💪 Weightlifting PRs")
    
    user_id = auth.get_current_user_id()
    is_admin = auth.is_admin()
    can_edit = not auth.is_coach()  # Users and admins can edit
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if can_edit:
            st.subheader("Add New Weightlifting PR")
            
            # For admin, allow adding for any user
            if is_admin:
                users = db.get_all_users()
                user_options = [(u['id'], u.get('full_name') or u['username']) for u in users]
                selected_user = st.selectbox(
                    "Add PR for user:",
                    options=user_options,
                    format_func=lambda x: x[1],
                    key="weightlift_add_user"
                )
                user_id_for_add = selected_user[0]
            else:
                user_id_for_add = user_id
            
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
                        db.add_weightlift_pr(user_id_for_add, movement, weight, unit, notes)
                        st.success(f"✅ Added {weight} {unit} {movement} PR!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid weight")
        else:
            st.info("👁️ You have view-only access as a coach")
    
    with col2:
        st.subheader("PR History")
        
        # For coach/admin, allow viewing other users' data
        if auth.can_view_all_data():
            users = db.get_all_users()
            user_options = [(-1, "All Users")] + [(u['id'], u.get('full_name') or u['username']) for u in users]
            
            selected_user = st.selectbox(
                "View PRs for:",
                options=user_options,
                format_func=lambda x: x[1],
                key="weightlift_view_user"
            )
            
            if selected_user[0] == -1:
                data = db.get_all_weightlifts()
            else:
                data = db.get_weightlifts_by_user(selected_user[0])
        else:
            data = db.get_weightlifts_by_user(user_id)
        
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
                
                # Display columns based on role
                if auth.can_view_all_data() and 'username' in df.columns:
                    display_cols = ["date", "username", "movement", "weight", "unit", "notes"]
                else:
                    display_cols = ["date", "movement", "weight", "unit", "notes"]
                
                st.dataframe(
                    df[[col for col in display_cols if col in df.columns]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Delete functionality (user can delete own, admin can delete any)
                if can_edit and not auth.is_coach():
                    st.subheader("Delete Entry")
                    
                    # Filter deletable entries
                    if is_admin:
                        deletable_data = filtered_data
                    else:
                        deletable_data = [e for e in filtered_data if e['user_id'] == user_id]
                    
                    if deletable_data:
                        entry_to_delete = st.selectbox(
                            "Select entry to delete",
                            options=[(e["id"], f"{e['date']} - {e['movement']} {e['weight']} {e['unit']}") 
                                     for e in deletable_data],
                            format_func=lambda x: x[1],
                            key="delete_weightlift"
                        )
                        
                        if st.button("Delete Selected Entry", key="delete_weightlift_btn"):
                            db.delete_weightlift_pr(entry_to_delete[0], user_id, is_admin)
                            st.success("Entry deleted!")
                            st.rerun()
                    else:
                        st.info("No deletable entries")
            else:
                st.info("No entries found for this filter")
        else:
            st.info("No weightlifting PRs recorded yet")


def show_benchmarks():
    """Display benchmarks tab"""
    st.header("⏱️ Benchmark Workouts")
    
    user_id = auth.get_current_user_id()
    is_admin = auth.is_admin()
    can_edit = not auth.is_coach()  # Users and admins can edit
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if can_edit:
            st.subheader("Add New Benchmark PR")
            
            # For admin, allow adding for any user
            if is_admin:
                users = db.get_all_users()
                user_options = [(u['id'], u.get('full_name') or u['username']) for u in users]
                selected_user = st.selectbox(
                    "Add PR for user:",
                    options=user_options,
                    format_func=lambda x: x[1],
                    key="benchmark_add_user"
                )
                user_id_for_add = selected_user[0]
            else:
                user_id_for_add = user_id
            
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
                        db.add_benchmark_pr(user_id_for_add, workout, time_minutes, time_seconds, rounds, reps, notes)
                        st.success(f"✅ Added {workout} PR!")
                        st.rerun()
                    else:
                        st.error("Please enter valid time or rounds")
        else:
            st.info("👁️ You have view-only access as a coach")
    
    with col2:
        st.subheader("PR History")
        
        # For coach/admin, allow viewing other users' data
        if auth.can_view_all_data():
            users = db.get_all_users()
            user_options = [(-1, "All Users")] + [(u['id'], u.get('full_name') or u['username']) for u in users]
            
            selected_user = st.selectbox(
                "View PRs for:",
                options=user_options,
                format_func=lambda x: x[1],
                key="benchmark_view_user"
            )
            
            if selected_user[0] == -1:
                data = db.get_all_benchmarks()
            else:
                data = db.get_benchmarks_by_user(selected_user[0])
        else:
            data = db.get_benchmarks_by_user(user_id)
        
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
                
                # Display columns based on role
                if auth.can_view_all_data() and 'username' in df.columns:
                    display_cols = ["date", "username", "workout", "time", "rounds", "reps", "notes"]
                else:
                    display_cols = ["date", "workout", "time", "rounds", "reps", "notes"]
                
                st.dataframe(
                    df[[col for col in display_cols if col in df.columns]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Delete functionality (user can delete own, admin can delete any)
                if can_edit and not auth.is_coach():
                    st.subheader("Delete Entry")
                    
                    # Filter deletable entries
                    if is_admin:
                        deletable_data = filtered_data
                    else:
                        deletable_data = [e for e in filtered_data if e['user_id'] == user_id]
                    
                    if deletable_data:
                        entry_to_delete = st.selectbox(
                            "Select entry to delete",
                            options=[(e["id"], f"{e['date']} - {e['workout']} {e['time_minutes']}:{e['time_seconds']:02d}") 
                                     for e in deletable_data],
                            format_func=lambda x: x[1],
                            key="delete_benchmark"
                        )
                        
                        if st.button("Delete Selected Entry", key="delete_benchmark_btn"):
                            db.delete_benchmark_pr(entry_to_delete[0], user_id, is_admin)
                            st.success("Entry deleted!")
                            st.rerun()
                    else:
                        st.info("No deletable entries")
            else:
                st.info("No entries found for this filter")
        else:
            st.info("No benchmark PRs recorded yet")


def show_progress():
    """Display progress tracking"""
    st.header("📈 Progress Tracking")
    
    user_id = auth.get_current_user_id()
    
    # For coach/admin, allow viewing other users' data
    if auth.can_view_all_data():
        users = db.get_all_users()
        user_options = [(u['id'], u.get('full_name') or u['username']) for u in users]
        
        selected_user = st.selectbox(
            "View progress for user:",
            options=user_options,
            format_func=lambda x: x[1],
            key="progress_user_select"
        )
        
        user_id = selected_user[0]
    
    # Weightlifts Progress
    st.subheader("Weightlifting Progress")
    
    weightlift_data = db.get_weightlifts_by_user(user_id)
    
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
    
    benchmark_data = db.get_benchmarks_by_user(user_id)
    
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
            
            # Validate data
            if df["total_seconds"].isna().any():
                st.warning("Some entries have invalid time data")
                df = df.dropna(subset=["total_seconds"])
            
            if len(df) == 0:
                st.info(f"No valid data for {workout_for_chart}")
            else:
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
                    best_idx = df["total_seconds"].idxmin()
                    best = df.loc[best_idx]
                    st.metric("Best Time", f"{int(best['time_minutes'])}:{int(best['time_seconds']):02d}")
                with col2:
                    first = df.iloc[0]
                    st.metric("First Attempt", f"{int(first['time_minutes'])}:{int(first['time_seconds']):02d}")
                with col3:
                    # Calculate improvement as first time - best time
                    best_time = df["total_seconds"].min()
                    first_time = df.iloc[0]['total_seconds']
                    improvement = first_time - best_time
                    st.metric("Time Saved", f"-{int(improvement)}s")
        else:
            st.info(f"No data recorded for {workout_for_chart} yet")
    else:
        st.info("No benchmark data recorded yet")


def show_account_settings():
    """Display account settings (password change)"""
    st.header("⚙️ Account Settings")
    
    user = auth.get_current_user()
    
    st.subheader("User Information")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Role:** {user['role']}")
    st.write(f"**Full Name:** {user.get('full_name', 'Not set')}")
    st.write(f"**Account Created:** {user.get('created_at', 'Unknown')}")
    
    st.markdown("---")
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Change Password")
        
        if submit:
            if not old_password or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 4:
                st.error("Password must be at least 4 characters")
            else:
                if auth.change_password(user['id'], old_password, new_password):
                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect")


# ==================== Main Application ====================

def main():
    """Main application logic"""
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        show_login_page()
        return
    
    # Show user header
    show_user_header()
    st.markdown("Track your Personal Records for weightlifts and benchmark workouts")
    
    # Create tabs based on user role
    if auth.is_admin():
        tabs = st.tabs([
            "📊 Dashboard",
            "💪 Weightlifts",
            "⏱️ Benchmarks",
            "📈 Progress",
            "👥 User Management",
            "⚙️ Settings"
        ])
        
        with tabs[0]:
            show_dashboard()
        with tabs[1]:
            show_weightlifts()
        with tabs[2]:
            show_benchmarks()
        with tabs[3]:
            show_progress()
        with tabs[4]:
            show_user_management()
        with tabs[5]:
            show_account_settings()
    
    elif auth.is_coach():
        tabs = st.tabs([
            "📊 Dashboard",
            "💪 Weightlifts",
            "⏱️ Benchmarks",
            "📈 Progress",
            "⚙️ Settings"
        ])
        
        with tabs[0]:
            show_dashboard()
        with tabs[1]:
            show_weightlifts()
        with tabs[2]:
            show_benchmarks()
        with tabs[3]:
            show_progress()
        with tabs[4]:
            show_account_settings()
    
    else:  # Regular user
        tabs = st.tabs([
            "📊 Dashboard",
            "💪 Weightlifts",
            "⏱️ Benchmarks",
            "📈 Progress",
            "⚙️ Settings"
        ])
        
        with tabs[0]:
            show_dashboard()
        with tabs[1]:
            show_weightlifts()
        with tabs[2]:
            show_benchmarks()
        with tabs[3]:
            show_progress()
        with tabs[4]:
            show_account_settings()
    
    # Footer
    st.markdown("---")
    st.markdown("💪 Keep crushing those PRs! 🏋️")


if __name__ == "__main__":
    main()
