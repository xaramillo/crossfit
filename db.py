"""
Database module for CrossFit PR Tracker
Handles all database operations with SQLite3
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


DATABASE_FILE = "crossfit_tracker.db"


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            full_name TEXT
        )
    """)
    
    # Create weightlifts_prs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weightlifts_prs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movement TEXT NOT NULL,
            weight REAL NOT NULL,
            unit TEXT NOT NULL,
            notes TEXT,
            date TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create benchmarks_prs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS benchmarks_prs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            workout TEXT NOT NULL,
            time_minutes INTEGER NOT NULL,
            time_seconds INTEGER NOT NULL,
            rounds INTEGER DEFAULT 0,
            reps INTEGER DEFAULT 0,
            notes TEXT,
            date TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def migrate_json_to_db(user_id: int, weightlifts_file: str = "weightlifts_prs.json", 
                       benchmarks_file: str = "benchmarks_prs.json") -> Tuple[int, int]:
    """
    Migrate data from JSON files to database for a specific user
    Returns: (weightlifts_count, benchmarks_count)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    weightlifts_count = 0
    benchmarks_count = 0
    
    # Migrate weightlifts
    if os.path.exists(weightlifts_file):
        try:
            with open(weightlifts_file, 'r') as f:
                weightlifts_data = json.load(f)
                for entry in weightlifts_data:
                    cursor.execute("""
                        INSERT INTO weightlifts_prs 
                        (user_id, movement, weight, unit, notes, date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        entry.get('movement'),
                        entry.get('weight'),
                        entry.get('unit'),
                        entry.get('notes', ''),
                        entry.get('date')
                    ))
                    weightlifts_count += 1
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error migrating weightlifts: {e}")
    
    # Migrate benchmarks
    if os.path.exists(benchmarks_file):
        try:
            with open(benchmarks_file, 'r') as f:
                benchmarks_data = json.load(f)
                for entry in benchmarks_data:
                    cursor.execute("""
                        INSERT INTO benchmarks_prs 
                        (user_id, workout, time_minutes, time_seconds, rounds, reps, notes, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        entry.get('workout'),
                        entry.get('time_minutes'),
                        entry.get('time_seconds'),
                        entry.get('rounds', 0),
                        entry.get('reps', 0),
                        entry.get('notes', ''),
                        entry.get('date')
                    ))
                    benchmarks_count += 1
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error migrating benchmarks: {e}")
    
    conn.commit()
    conn.close()
    
    return weightlifts_count, benchmarks_count


# ==================== User Operations ====================

def create_user(username: str, password_hash: str, role: str = 'user', 
                full_name: Optional[str] = None) -> Optional[int]:
    """Create a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, full_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_all_users() -> List[Dict]:
    """Get all users (admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name, created_at FROM users ORDER BY username")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_user_password(user_id: int, password_hash: str) -> bool:
    """Update user password"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                      (password_hash, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_user_role(user_id: int, role: str) -> bool:
    """Update user role (admin only)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def delete_user(user_id: int) -> bool:
    """Delete user and all associated data (admin only)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ==================== Weightlifts Operations ====================

def add_weightlift_pr(user_id: int, movement: str, weight: float, 
                      unit: str, notes: str = "") -> bool:
    """Add a new weightlift PR"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weightlifts_prs (user_id, movement, weight, unit, notes, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, movement, weight, unit, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_weightlifts_by_user(user_id: int) -> List[Dict]:
    """Get all weightlifts for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weightlifts_prs 
        WHERE user_id = ? 
        ORDER BY date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_weightlifts() -> List[Dict]:
    """Get all weightlifts (coach/admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.*, u.username, u.full_name
        FROM weightlifts_prs w
        JOIN users u ON w.user_id = u.id
        ORDER BY w.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_current_prs_weightlifts(user_id: int) -> Dict:
    """Get current PRs for all weightlifts for a specific user"""
    data = get_weightlifts_by_user(user_id)
    if not data:
        return {}
    
    prs = {}
    for entry in data:
        movement = entry["movement"]
        if movement not in prs or entry["weight"] > prs[movement]["weight"]:
            prs[movement] = entry
    
    return prs


def delete_weightlift_pr(pr_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Delete a weightlift PR (only if user owns it or is admin)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if is_admin:
            cursor.execute("DELETE FROM weightlifts_prs WHERE id = ?", (pr_id,))
        else:
            cursor.execute("DELETE FROM weightlifts_prs WHERE id = ? AND user_id = ?", 
                         (pr_id, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ==================== Benchmarks Operations ====================

def add_benchmark_pr(user_id: int, workout: str, time_minutes: int, 
                     time_seconds: int, rounds: int = 0, reps: int = 0, 
                     notes: str = "") -> bool:
    """Add a new benchmark PR"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO benchmarks_prs 
            (user_id, workout, time_minutes, time_seconds, rounds, reps, notes, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, workout, time_minutes, time_seconds, rounds, reps, notes, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_benchmarks_by_user(user_id: int) -> List[Dict]:
    """Get all benchmarks for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM benchmarks_prs 
        WHERE user_id = ? 
        ORDER BY date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_benchmarks() -> List[Dict]:
    """Get all benchmarks (coach/admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, u.username, u.full_name
        FROM benchmarks_prs b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_current_prs_benchmarks(user_id: int) -> Dict:
    """Get current PRs (best times) for all benchmarks for a specific user"""
    data = get_benchmarks_by_user(user_id)
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


def delete_benchmark_pr(pr_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Delete a benchmark PR (only if user owns it or is admin)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if is_admin:
            cursor.execute("DELETE FROM benchmarks_prs WHERE id = ?", (pr_id,))
        else:
            cursor.execute("DELETE FROM benchmarks_prs WHERE id = ? AND user_id = ?", 
                         (pr_id, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
