# CrossFit PR Tracker 🏋️

A Streamlit-based multi-user web application to track Personal Records (PRs) for CrossFit weightlifting movements and benchmark workouts with role-based access control.

## Features

### Core Features
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

### Multi-User Features
- **Authentication System**: Secure login/logout with password hashing using bcrypt
- **User Registration**: Self-registration with automatic "user" role assignment
- **Role-Based Access Control**:
  - **User Role**: Can only view and manage their own PRs
  - **Coach Role**: Read-only access to view all users' data
  - **Admin Role**: Full access to manage all data and users
- **User Management**: Admin interface for creating, editing, and deleting users
- **SQLite3 Database**: Efficient data storage with proper relational structure
- **Data Migration Tool**: Convert existing JSON data to database format

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

3. **First Time Setup**:
   - Default admin account is created automatically
   - Username: `admin`
   - Password: `admin`
   - **⚠️ Important**: Change the admin password immediately after first login!

4. Use the application:
   - **Login/Register**: Create your account or login with existing credentials
   - **Dashboard**: View all your current PRs
   - **Weightlifts**: Add and track weightlifting PRs
   - **Benchmarks**: Add and track benchmark workout times
   - **Progress**: Visualize your improvement over time
   - **Settings**: Change your password
   - **User Management** (Admin only): Manage users and roles

## User Roles

### User Role
- Can register their own PRs and benchmarks
- Can view, edit, and delete **only their own records**
- Dashboard shows only their own PRs
- Cannot see other users' data

### Coach Role
- Can view **all users'** scores and PRs
- Can filter and search by user
- **Read-only access** - cannot modify any records
- Can view progress charts for all users
- No access to user management

### Admin Role
- **Full CRUD operations** on all users' scores and benchmarks
- Can add, edit, and delete any user's records
- **User management interface**:
  - Create new users with any role
  - Edit existing users (change role, reset password)
  - Delete users
  - List all users with their roles
- Can view and manage all data across the system

## Data Migration

If you have existing JSON data files (`weightlifts_prs.json` and `benchmarks_prs.json`), you can migrate them to the new SQLite3 database:

1. Login as admin
2. Go to **User Management** → **Migration Tool** tab
3. Select the user to import data for
4. Specify the JSON file paths (defaults provided)
5. Click "Migrate Data"

The original JSON files will remain untouched and can be used as backup.

## Data Storage

- **Database**: SQLite3 database file (`crossfit_tracker.db`)
- **Schema**: 
  - `users`: User accounts with roles and credentials
  - `weightlifts_prs`: Weightlifting PR records linked to users
  - `benchmarks_prs`: Benchmark workout records linked to users
- **Security**: Passwords are hashed using bcrypt
- **Backup**: Database file can be backed up for data safety

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- bcrypt >= 4.0.0

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **Session Management**: Secure session state with Streamlit
- **SQL Injection Protection**: Parameterized queries throughout
- **Role-Based Access Control**: Enforced on both UI and backend
- **No Plain Text Passwords**: All passwords are hashed before storage

## License

MIT License
