# Email PDF Processing Agent

An automated agent that monitors email inboxes for PDF attachments, extracts text, generates summaries using LLM, and sends the summaries back via email.

## 🚀 Features

- **📧 Email Monitoring**: Continuously monitors specified email inbox for new messages
- **📄 PDF Processing**: Automatically extracts text from PDF attachments
- **🤖 AI Summarization**: Uses OpenAI or Anthropic LLMs to generate concise summaries
- **📤 Email Automation**: Sends summaries back via email automatically
- **🔍 Smart Filtering**: Optional sender whitelist and subject keyword filtering
- **📊 Logging & Monitoring**: Comprehensive logging for troubleshooting
- **⚙️ Configurable**: Highly customizable via environment variables
- **🛡️ Error Handling**: Robust error handling with notification system

## 📋 Requirements

- Python 3.8+
- OpenAI API key (or Anthropic API key)
- Email account with IMAP/SMTP access (Gmail recommended)
- App-specific passwords for email authentication

## 🔧 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
python setup_email_agent.py
```

This will:
- Create a `.env` template file
- Check dependencies
- Provide Gmail setup instructions
- Validate your configuration

### 3. Configure Email (Gmail Example)

1. **Enable 2-Factor Authentication**:
   - Go to Google Account → Security → 2-Step Verification

2. **Generate App Passwords**:
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and "Other" → Name it "Email PDF Agent"
   - Use the generated 16-character password

3. **Update .env file**:
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=recipient@gmail.com
OPENAI_API_KEY=your-openai-api-key
```

### 4. Test Your Setup

```bash
python test_email_agent.py
```

### 5. Run the Agent

```bash
python email_pdf_agent.py
```

## 📁 Configuration Options

All configuration is done via environment variables (or `.env` file):

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_ADDRESS` | Email to monitor for PDFs | `monitor@gmail.com` |
| `EMAIL_PASSWORD` | App password for monitoring email | `abcd efgh ijkl mnop` |
| `SENDER_EMAIL` | Email to send summaries from | `sender@gmail.com` |
| `SENDER_PASSWORD` | App password for sender email | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Where to send summaries | `recipient@gmail.com` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `CHECK_INTERVAL` | `60` | Seconds between email checks |
| `MAX_PDF_SIZE` | `10485760` | Max PDF size (10MB) |
| `MODEL_PROVIDER` | `openai` | `openai` or `anthropic` |
| `MODEL_NAME` | `gpt-4o-mini` | LLM model to use |
| `SENDER_WHITELIST` | `` | Comma-separated sender emails |
| `SUBJECT_KEYWORDS` | `` | Comma-separated subject keywords |

## 🎯 How It Works

1. **Email Monitoring**: Agent checks configured inbox every N seconds
2. **PDF Detection**: Identifies emails with PDF attachments
3. **Text Extraction**: Uses PyPDF to extract text from PDFs
4. **AI Summarization**: Sends extracted text to LLM for summarization
5. **Email Response**: Sends summary back to configured recipient
6. **Error Handling**: Logs errors and sends notifications for failed processing

## 📧 Email Workflow

### Input Email (Monitored)
- Subject: "Monthly Report"
- From: colleague@company.com
- Attachment: report.pdf

### Output Email (Generated)
```
To: recipient@gmail.com
Subject: PDF Summary: report.pdf

PDF Summary Report
==================

**Original Email Details:**
- From: colleague@company.com
- Subject: Monthly Report
- Date: 2025-06-17 10:30:00
- PDF File: report.pdf

**Summary:**
This monthly report covers Q2 performance metrics...
[AI-generated summary of PDF content]

---
Generated automatically by Email PDF Agent
```

## 🧪 Testing

Run individual tests:
```bash
# Test configuration
python test_email_agent.py config

# Test email connection
python test_email_agent.py email

# Test LLM connection
python test_email_agent.py llm

# Test PDF processing
python test_email_agent.py pdf

# Test email sending
python test_email_agent.py send

# Run all tests
python test_email_agent.py
```

## 📊 Monitoring & Logs

The agent creates detailed logs in `email_pdf_agent.log`:

```
2025-06-17 10:30:00 - INFO - Email PDF Agent initialized
2025-06-17 10:30:01 - INFO - Connected to email server: imap.gmail.com
2025-06-17 10:30:02 - INFO - Found 2 unread emails
2025-06-17 10:30:03 - INFO - Processing email from: colleague@company.com
2025-06-17 10:30:04 - INFO - Found PDF attachment: report.pdf
2025-06-17 10:30:05 - INFO - Successfully extracted 1250 characters from PDF
2025-06-17 10:30:10 - INFO - Successfully generated summary for report.pdf
2025-06-17 10:30:12 - INFO - Summary email sent for report.pdf
```

## 🔒 Security Best Practices

1. **Use App Passwords**: Never use your main email password
2. **Environment Variables**: Keep sensitive data in `.env` file
3. **File Permissions**: Secure your `.env` file: `chmod 600 .env`
4. **API Key Security**: Rotate API keys regularly
5. **Email Filtering**: Use sender whitelist for added security

## 🛠️ Troubleshooting

### Common Issues

**Authentication Errors**:
- Verify app passwords are correctly generated
- Check 2FA is enabled
- Ensure IMAP/SMTP are enabled in email settings

**No Emails Processed**:
- Check sender whitelist and keyword filters
- Verify emails contain PDF attachments
- Check PDF size limits
- Review log file for detailed errors

**LLM API Errors**:
- Verify API key is correct
- Check API usage limits/quotas
- Test with smaller PDF files first

**Email Sending Fails**:
- Verify SMTP settings
- Check sender email credentials
- Ensure recipient email is valid

### Advanced Configuration

**Gmail with Custom Domain**:
```env
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
EMAIL_ADDRESS=you@yourdomain.com
```

**Other Email Providers**:
```env
# Outlook/Hotmail
IMAP_SERVER=outlook.office365.com
SMTP_SERVER=smtp.office365.com
IMAP_PORT=993
SMTP_PORT=587

# Yahoo
IMAP_SERVER=imap.mail.yahoo.com
SMTP_SERVER=smtp.mail.yahoo.com
```

## 🔄 Running as a Service

### Using systemd (Linux)

Create `/etc/systemd/system/email-pdf-agent.service`:
```ini
[Unit]
Description=Email PDF Processing Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/pdf_agent_project
ExecStart=/usr/bin/python3 email_pdf_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable email-pdf-agent
sudo systemctl start email-pdf-agent
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "email_pdf_agent.py"]
```

## 📈 Performance Optimization

- **Batch Processing**: Process multiple PDFs from same email efficiently
- **Model Selection**: Use `gpt-4o-mini` for cost-effectiveness
- **PDF Size Limits**: Set appropriate limits to avoid timeouts
- **Check Intervals**: Balance between responsiveness and resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log files
3. Run the test suite
4. Open an issue with detailed information

---

**Built with [Agno](https://github.com/agno-agi/agno) - The AI Agent Framework**
