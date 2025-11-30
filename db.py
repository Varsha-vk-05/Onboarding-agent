"""
Database module for managing employees, onboarding plans, and progress tracking.
Uses SQLite for simplicity and portability.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class Database:
    """Database manager for employee onboarding system."""
    
    def __init__(self, db_path: str = "onboarding.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                role TEXT,
                department TEXT,
                start_date DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Onboarding plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS onboarding_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                checklist_items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)
        
        # Progress tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                task_name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)
        
        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                message TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                sent_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                channel TEXT DEFAULT 'email',
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)
        
        # Documents metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_employee(self, employee_id: str, name: str, email: str, 
                    phone: str = None, role: str = None, 
                    department: str = None, start_date: str = None) -> bool:
        """Add a new employee to the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO employees (employee_id, name, email, phone, role, department, start_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, name, email, phone, role, department, start_date))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Get employee by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_employees(self) -> List[Dict]:
        """Get all employees."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def save_onboarding_plan(self, employee_id: str, plan_data: Dict, 
                            checklist_items: List[Dict]) -> int:
        """Save onboarding plan for an employee."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO onboarding_plans (employee_id, plan_data, checklist_items)
            VALUES (?, ?, ?)
        """, (employee_id, json.dumps(plan_data), json.dumps(checklist_items)))
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id
    
    def get_onboarding_plan(self, employee_id: str) -> Optional[Dict]:
        """Get onboarding plan for an employee."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM onboarding_plans 
            WHERE employee_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (employee_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            plan = dict(row)
            plan['plan_data'] = json.loads(plan['plan_data'])
            plan['checklist_items'] = json.loads(plan['checklist_items'])
            return plan
        return None
    
    def update_task_status(self, employee_id: str, task_id: str, 
                          status: str, notes: str = None):
        """Update task status in progress tracking."""
        conn = self.get_connection()
        cursor = conn.cursor()
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        cursor.execute("""
            UPDATE progress 
            SET status = ?, completed_at = ?, notes = ?
            WHERE employee_id = ? AND task_id = ?
        """, (status, completed_at, notes, employee_id, task_id))
        conn.commit()
        conn.close()
    
    def add_progress_task(self, employee_id: str, task_id: str, 
                         task_name: str, status: str = 'pending'):
        """Add a new task to progress tracking."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO progress (employee_id, task_id, task_name, status)
            VALUES (?, ?, ?, ?)
        """, (employee_id, task_id, task_name, status))
        conn.commit()
        conn.close()
    
    def get_progress(self, employee_id: str) -> List[Dict]:
        """Get all progress tasks for an employee."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM progress 
            WHERE employee_id = ? 
            ORDER BY created_at ASC
        """, (employee_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_reminder(self, employee_id: str, reminder_type: str, 
                    message: str, scheduled_time: str, channel: str = 'email'):
        """Add a reminder."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (employee_id, reminder_type, message, scheduled_time, channel)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, reminder_type, message, scheduled_time, channel))
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    def get_pending_reminders(self, before_time: str = None) -> List[Dict]:
        """Get pending reminders."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if before_time:
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE status = 'pending' AND scheduled_time <= ?
                ORDER BY scheduled_time ASC
            """, (before_time,))
        else:
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE status = 'pending'
                ORDER BY scheduled_time ASC
            """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_reminder_sent(self, reminder_id: int):
        """Mark reminder as sent."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders 
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reminder_id,))
        conn.commit()
        conn.close()
    
    def add_document(self, filename: str, file_path: str, 
                    file_type: str = 'pdf') -> int:
        """Add document metadata."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (filename, file_path, file_type)
            VALUES (?, ?, ?)
        """, (filename, file_path, file_type))
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def update_document_status(self, doc_id: int, status: str):
        """Update document processing status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        processed_at = datetime.now().isoformat() if status == 'processed' else None
        cursor.execute("""
            UPDATE documents 
            SET status = ?, processed_at = ?
            WHERE id = ?
        """, (status, processed_at, doc_id))
        conn.commit()
        conn.close()
    
    def get_documents(self) -> List[Dict]:
        """Get all documents."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

