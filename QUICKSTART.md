# Quick Start Guide

Get your AI Employee Onboarding Assistant up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up OpenAI API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (CMD)
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: In Settings Page**
1. Run the app: `streamlit run app.py`
2. Go to Settings page
3. Enter your API key in the input field

## Step 3: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 4: Upload Documents

1. Navigate to **Document Upload** page
2. Upload a PDF file (e.g., employee handbook, company policies)
3. Click **Process Document**
4. Wait for processing to complete

## Step 5: Add an Employee

1. Navigate to **Employee Management** page
2. Fill in employee details:
   - Employee ID: `EMP001`
   - Name: `John Doe`
   - Email: `john.doe@company.com`
   - Role: `Software Engineer`
   - Department: `Engineering`
   - Start Date: Select a date
3. Click **Add Employee**

## Step 6: Generate Onboarding Plan

1. Navigate to **Onboarding Plans** page
2. Select the employee you just added
3. Click **Generate Onboarding Plan**
4. Wait for the AI to generate a personalized plan
5. Review the plan and checklist

## Step 7: Test Q&A

1. Navigate to **Q&A Assistant** page
2. (Optional) Select employee context
3. Ask a question like: "What is the company's vacation policy?"
4. Get an AI-powered answer with citations

## Step 8: Track Progress

1. Navigate to **Progress Tracking** page
2. Select an employee
3. View tasks and mark them as complete
4. Monitor completion rate

## Optional: Configure Reminders

### Email Reminders

Set environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**Note**: For Gmail, you need to generate an "App Password" in your Google Account settings.

### WhatsApp Reminders

Set environment variables:
```bash
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

**Note**: You need a Twilio account with WhatsApp API access.

## Troubleshooting

### "OpenAI API key is required" Error
- Make sure you've set the `OPENAI_API_KEY` environment variable
- Or enter it in the Settings page
- Verify the API key is valid and has credits

### Document Processing Fails
- Ensure the PDF is not corrupted
- Check file permissions
- Verify ChromaDB directory is writable

### Reminders Not Sending
- Check email/WhatsApp credentials in Settings
- Verify SMTP/Twilio configuration
- Check that scheduler is running (should start automatically)

## Next Steps

- Upload more company documents to improve knowledge base
- Add more employees and generate their onboarding plans
- Customize onboarding plans based on your company's needs
- Set up automated reminders for important milestones

## Example Questions to Try

- "What is the company's remote work policy?"
- "How do I request time off?"
- "What are the benefits available to employees?"
- "What is the dress code policy?"
- "How do I access the company intranet?"

Enjoy your AI Employee Onboarding Assistant! 🚀

