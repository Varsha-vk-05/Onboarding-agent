"""
Scheduler module for sending reminders via email and WhatsApp.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import schedule
import time
import threading
from db import Database
import requests


class ReminderScheduler:
    """Handles scheduling and sending reminders via email and WhatsApp."""
    
    def __init__(self, 
                 smtp_server: str = None,
                 smtp_port: int = 587,
                 email_user: str = None,
                 email_password: str = None,
                 twilio_account_sid: str = None,
                 twilio_auth_token: str = None,
                 twilio_whatsapp_from: str = None):
        """Initialize scheduler with email and WhatsApp credentials."""
        self.db = Database()
        
        # Email configuration
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.email_user = email_user or os.getenv("EMAIL_USER")
        self.email_password = email_password or os.getenv("EMAIL_PASSWORD")
        
        # WhatsApp/Twilio configuration
        self.twilio_account_sid = twilio_account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = twilio_auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_from = twilio_whatsapp_from or os.getenv("TWILIO_WHATSAPP_FROM")

        # Simulation mode (if true, do not perform external sends; just log)
        simulate = os.getenv("SIMULATE_COMM", "false").lower()
        self.simulate = simulate in ("1", "true", "yes")
        
        self.running = False
        self.scheduler_thread = None
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email reminder."""
        if self.simulate:
            print(f"[SIMULATE] Would send email to {to_email} with subject: {subject}")
            return True

        if not self.email_user or not self.email_password:
            print("Email credentials not configured. Skipping email send.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_whatsapp(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message via Twilio."""
        if self.simulate:
            print(f"[SIMULATE] Would send WhatsApp to {to_number}: {message}")
            return True

        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_whatsapp_from]):
            print("Twilio credentials not configured. Skipping WhatsApp send.")
            return False
        
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            payload = {
                'From': f'whatsapp:{self.twilio_whatsapp_from}',
                'To': f'whatsapp:{to_number}',
                'Body': message
            }
            
            response = requests.post(
                url,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                data=payload
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"Error sending WhatsApp: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False
    
    def send_reminder(self, reminder: Dict) -> bool:
        """Send a reminder via the specified channel."""
        employee = self.db.get_employee(reminder['employee_id'])
        if not employee:
            return False
        
        # Get reminder message
        message = reminder['message']
        reminder_type = reminder['reminder_type']
        
        # Format message based on type
        if reminder_type == 'task_reminder':
            subject = "Onboarding Task Reminder"
            body = f"""
            <html>
            <body>
                <h2>Onboarding Task Reminder</h2>
                <p>Hello {employee['name']},</p>
                <p>{message}</p>
                <p>Please log in to your onboarding portal to complete this task.</p>
                <p>Best regards,<br>Onboarding Assistant</p>
            </body>
            </html>
            """
        elif reminder_type == 'welcome':
            subject = "Welcome to the Company!"
            body = f"""
            <html>
            <body>
                <h2>Welcome to the Company!</h2>
                <p>Hello {employee['name']},</p>
                <p>{message}</p>
                <p>We're excited to have you on board!</p>
                <p>Best regards,<br>Onboarding Assistant</p>
            </body>
            </html>
            """
        else:
            subject = "Onboarding Reminder"
            body = f"""
            <html>
            <body>
                <h2>Onboarding Reminder</h2>
                <p>Hello {employee['name']},</p>
                <p>{message}</p>
                <p>Best regards,<br>Onboarding Assistant</p>
            </body>
            </html>
            """
        
        success = False
        channel = reminder.get('channel', 'email')
        
        if channel == 'email':
            success = self.send_email(employee['email'], subject, body)
        elif channel == 'whatsapp' and employee.get('phone'):
            success = self.send_whatsapp(employee['phone'], message)
        elif channel == 'both':
            email_success = self.send_email(employee['email'], subject, body)
            whatsapp_success = False
            if employee.get('phone'):
                whatsapp_success = self.send_whatsapp(employee['phone'], message)
            success = email_success or whatsapp_success
        
        if success:
            self.db.mark_reminder_sent(reminder['id'])
        
        return success
    
    def process_pending_reminders(self):
        """Process all pending reminders that are due."""
        now = datetime.now().isoformat()
        pending_reminders = self.db.get_pending_reminders(now)
        
        for reminder in pending_reminders:
            self.send_reminder(reminder)
    
    def schedule_reminder(self, employee_id: str, reminder_type: str,
                         message: str, scheduled_time: str, 
                         channel: str = 'email'):
        """Schedule a new reminder."""
        return self.db.add_reminder(
            employee_id=employee_id,
            reminder_type=reminder_type,
            message=message,
            scheduled_time=scheduled_time,
            channel=channel
        )
    
    def schedule_welcome_reminder(self, employee_id: str, start_date: str):
        """Schedule welcome reminder for new employee."""
        welcome_time = datetime.fromisoformat(start_date) + timedelta(days=0)
        message = "Welcome to the company! Your personalized onboarding plan is ready. Please check your onboarding portal to get started."
        return self.schedule_reminder(
            employee_id=employee_id,
            reminder_type='welcome',
            message=message,
            scheduled_time=welcome_time.isoformat(),
            channel='email'
        )
    
    def schedule_task_reminders(self, employee_id: str, task_due_dates: Dict[str, str]):
        """Schedule reminders for specific tasks."""
        for task_id, due_date in task_due_dates.items():
            progress = self.db.get_progress(employee_id)
            task = next((t for t in progress if t['task_id'] == task_id), None)
            
            if task and task['status'] == 'pending':
                reminder_time = datetime.fromisoformat(due_date) - timedelta(days=1)
                message = f"Reminder: Don't forget to complete '{task['task_name']}' by {due_date}."
                self.schedule_reminder(
                    employee_id=employee_id,
                    reminder_type='task_reminder',
                    message=message,
                    scheduled_time=reminder_time.isoformat(),
                    channel='email'
                )
    
    def start_scheduler(self):
        """Start the background scheduler thread."""
        if self.running:
            return
        
        self.running = True
        
        # Schedule reminder processing every minute
        schedule.every(1).minutes.do(self.process_pending_reminders)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("Reminder scheduler started.")
    
    def stop_scheduler(self):
        """Stop the background scheduler thread."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("Reminder scheduler stopped.")

