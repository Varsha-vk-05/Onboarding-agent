import os
from pathlib import Path
print('PYTHON:', os.sys.executable)
print('CWD:', Path.cwd())
from dotenv import load_dotenv
load_dotenv()
print('OPENAI set:', bool(os.getenv('OPENAI_API_KEY')))
print('OPENAI preview:', (os.getenv('OPENAI_API_KEY') or '<empty>')[:6] + '...' if os.getenv('OPENAI_API_KEY') else '<empty>')
print('SMTP set:', bool(os.getenv('EMAIL_USER')))
print('SIMULATE_COMM:', os.getenv('SIMULATE_COMM'))

# Check Streamlit process
try:
    import psutil
    streamlit_running = any('streamlit' in ' '.join(p.cmdline()).lower() for p in psutil.process_iter())
    print('Streamlit running (psutil):', streamlit_running)
except Exception:
    print('psutil not available; skipping process check')

# Import project modules and show basic state
try:
    from db import Database
    db = Database()
    emps = db.get_all_employees()
    docs = db.get_documents()
    reminders = db.get_pending_reminders('9999-01-01T00:00:00')
    print('DB employees:', len(emps))
    print('DB documents:', len(docs))
    print('DB pending reminders (example):', len(reminders))
except Exception as e:
    print('DB error:', repr(e))

try:
    from agent import OnboardingAgent
    ag = None
    try:
        ag = OnboardingAgent()
        print('Agent initialized OK')
    except Exception as e:
        print('Agent init error:', repr(e))
except Exception as e:
    print('Agent import error:', repr(e))

try:
    from scheduler import ReminderScheduler
    sched = ReminderScheduler()
    print('Scheduler simulate flag:', sched.simulate)
    # Try simulated send (will not send real email if SIMULATE_COMM=true)
    ok = sched.send_email('test@example.com', 'Test', '<p>Test</p>')
    print('send_email() returned:', ok)
except Exception as e:
    print('Scheduler error:', repr(e))

print('SMOKE TEST COMPLETE')
