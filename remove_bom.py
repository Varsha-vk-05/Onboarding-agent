content = b"""OPENAI_API_KEY=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

# Email Configuration (Optional - for reminders)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# EMAIL_USER=your_email@gmail.com
# EMAIL_PASSWORD=your_app_password

# WhatsApp/Twilio Configuration (Optional - for reminders)
# TWILIO_ACCOUNT_SID=your_twilio_account_sid
# TWILIO_AUTH_TOKEN=your_twilio_auth_token
# TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
"""
with open(".env", "wb") as f:
    f.write(content)
print("Wrote .env in binary mode (no BOM)")
