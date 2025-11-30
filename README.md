# AI Employee Onboarding Assistant

A comprehensive AI-powered employee onboarding system that automates the onboarding process, answers questions, tracks progress, and sends reminders.

## Features

- 📄 **Document Management**: Upload and process company PDFs to build a knowledge base
- 🤖 **AI-Powered Q&A**: Answer onboarding questions with citations from company documents
- 📋 **Personalized Onboarding Plans**: Generate customized onboarding plans for each employee
- ✅ **Progress Tracking**: Track employee onboarding progress with checklists
- 📧 **Automated Reminders**: Send email and WhatsApp reminders for tasks and milestones
- 🎨 **Streamlit UI**: Beautiful, intuitive web interface

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Dashboard │ │Documents │ │Employees │ │  Q&A     │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  AI Agent      │  │  Document      │  │  Scheduler     │
│  (agent.py)    │  │  Ingester      │  │  (scheduler.py)│
│                │  │  (ingest.py)   │  │                │
│  - Q&A         │  │                │  │  - Email       │
│  - Plan Gen    │  │  - PDF Parse   │  │  - WhatsApp    │
│  - Checklist   │  │  - Embeddings  │  │  - Reminders   │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  Database      │  │  ChromaDB      │
│  (db.py)       │  │  (Knowledge    │
│                │  │   Base)        │
│  - Employees   │  │                │
│  - Plans       │  │  - Embeddings  │
│  - Progress    │  │  - Vectors     │
│  - Reminders   │  │  - Search      │
└────────────────┘  └────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- (Optional) Email SMTP credentials for reminders
- (Optional) Twilio credentials for WhatsApp reminders

### Setup

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   
   Create a `.env` file or set environment variables:
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional - Email configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   
   # Optional - WhatsApp/Twilio configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`

## Usage Guide

### 1. Upload Documents

1. Navigate to **Document Upload** page
2. Upload PDF files containing company policies, procedures, and onboarding information
3. Click **Process Document** to add it to the knowledge base
4. Wait for processing to complete (documents are chunked and embedded)

### 2. Add Employees

1. Navigate to **Employee Management** page
2. Fill in employee details:
   - Employee ID (unique)
   - Name
   - Email
   - Phone (optional)
   - Role
   - Department
   - Start Date
3. Click **Add Employee**

### 3. Generate Onboarding Plans

1. Navigate to **Onboarding Plans** page
2. Select an employee
3. Click **Generate Onboarding Plan**
4. The AI will create a personalized plan based on:
   - Employee role and department
   - Company documents in knowledge base
   - Best practices

### 4. Track Progress

1. Navigate to **Progress Tracking** page
2. Select an employee
3. View task completion status
4. Mark tasks as complete
5. Monitor completion rate

### 5. Ask Questions

1. Navigate to **Q&A Assistant** page
2. (Optional) Select employee context
3. Enter your question
4. Get AI-powered answers with citations from company documents

### 6. Configure Settings

1. Navigate to **Settings** page
2. Configure API keys and credentials
3. View database and knowledge base information

## Project Structure

```
.
├── app.py              # Streamlit UI application
├── agent.py            # AI agent for Q&A and plan generation
├── ingest.py           # Document ingestion and ChromaDB integration
├── scheduler.py        # Reminder scheduling and sending
├── db.py               # Database management (SQLite)
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── onboarding.db      # SQLite database (created automatically)
├── chroma_db/         # ChromaDB storage (created automatically)
└── uploads/           # Uploaded PDF files (created automatically)
```

## Database Schema

### Employees Table
- `id`: Primary key
- `employee_id`: Unique employee identifier
- `name`: Employee name
- `email`: Email address
- `phone`: Phone number
- `role`: Job role
- `department`: Department
- `start_date`: Employment start date
- `status`: Employee status

### Onboarding Plans Table
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `plan_data`: JSON structure of the plan
- `checklist_items`: JSON array of checklist items

### Progress Table
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `task_id`: Task identifier
- `task_name`: Task description
- `status`: Task status (pending/completed)
- `completed_at`: Completion timestamp

### Reminders Table
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `reminder_type`: Type of reminder
- `message`: Reminder message
- `scheduled_time`: When to send
- `sent_at`: When it was sent
- `status`: Reminder status
- `channel`: Delivery channel (email/whatsapp/both)

### Documents Table
- `id`: Primary key
- `filename`: Document filename
- `file_path`: File system path
- `file_type`: Document type
- `uploaded_at`: Upload timestamp
- `processed_at`: Processing timestamp
- `status`: Processing status

## API Integration

### OpenAI
- Used for generating answers and onboarding plans
- Requires API key in environment variable `OPENAI_API_KEY`
- Model: `gpt-3.5-turbo` (configurable)

### Email (SMTP)
- Sends email reminders
- Configure via environment variables
- Supports Gmail, Outlook, and other SMTP servers

### WhatsApp (Twilio)
- Sends WhatsApp reminders via Twilio API
- Requires Twilio account and credentials
- Configure via environment variables

## Troubleshooting

### OpenAI API Key Error
- Ensure `OPENAI_API_KEY` is set in environment variables
- Check that the API key is valid and has credits

### Document Processing Fails
- Ensure PDF files are not corrupted
- Check file permissions
- Verify ChromaDB storage directory is writable

### Reminders Not Sending
- Check email/WhatsApp credentials in Settings
- Verify SMTP/Twilio configuration
- Check scheduler is running (should start automatically)

### Database Errors
- Ensure write permissions in project directory
- Check if `onboarding.db` file is locked by another process

## Future Enhancements

- [ ] Support for multiple document formats (Word, Excel, etc.)
- [ ] Integration with HR systems (API connectors)
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Customizable onboarding templates
- [ ] Integration with calendar systems
- [ ] Mobile app version
- [ ] Advanced AI models (GPT-4, Claude, etc.)

## License

This project is provided as-is for demonstration and educational purposes.

## Support

For issues or questions, please check:
1. Environment variables are correctly set
2. All dependencies are installed
3. API keys are valid and have sufficient credits
4. Database and storage directories have proper permissions

## Contributing

Contributions are welcome! Please ensure:
- Code follows Python best practices
- All new features are tested
- Documentation is updated
- Dependencies are added to `requirements.txt`

live working link-https://app-agent-n5rhvaqy9ba4xrbz6abuou.streamlit.app
