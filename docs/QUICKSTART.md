# 🚀 Quick Start Guide - Email PDF Agent

Get your automated email-to-PDF processing agent running in under 10 minutes!

## ⚡ Prerequisites

- Python 3.8+
- Gmail account (or other IMAP/SMTP email)
- OpenAI API key (or Anthropic)

## 🏃‍♂️ 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Wizard
```bash
python setup_email_agent.py
```
This creates a `.env` template and shows Gmail setup instructions.

### 3. Configure Gmail
1. **Enable 2FA**: Google Account → Security → 2-Step Verification
2. **Generate App Password**: 2-Step Verification → App passwords → Mail → Other
3. **Copy the 16-character password**

### 4. Edit Configuration
Edit your `.env` file:
```env
# Required settings
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
SENDER_EMAIL=your-email@gmail.com  
SENDER_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=where-to-send-summaries@gmail.com
OPENAI_API_KEY=sk-your-openai-key
```

### 5. Test Everything
```bash
python test_email_agent.py
```

### 6. Start the Agent
```bash
python email_pdf_agent.py
```

## 🎯 Test It Out

1. **Send a test email** with a PDF attachment to your monitoring email
2. **Wait 1-2 minutes** for processing
3. **Check your recipient email** for the AI-generated summary!

## 📧 What Happens Next

The agent will:
- Monitor your inbox every 60 seconds (configurable)
- Process any new emails with PDF attachments
- Extract text from the PDFs
- Generate summaries using AI
- Email you the summaries automatically
- Log all activity for monitoring

## ⚙️ Quick Customization

Edit your `.env` file to customize:

```env
# Check emails every 5 minutes instead of 1 minute
CHECK_INTERVAL=300

# Only process emails from specific senders
SENDER_WHITELIST=boss@company.com,reports@system.com

# Only process emails with specific keywords in subject
SUBJECT_KEYWORDS=report,document,analysis

# Use different AI model
MODEL_NAME=gpt-4o-mini
```

## 🆘 Troubleshooting

**❌ Authentication Failed**
- Verify 2FA is enabled
- Use app password, not regular password
- Check email address is correct

**❌ No Emails Processed**
- Check sender whitelist/keyword filters
- Verify PDFs are under size limit (10MB default)
- Check logs: `tail -f email_pdf_agent.log`

**❌ LLM API Error**
- Verify API key is correct
- Check API usage limits/credits
- Try with smaller PDF first

## 📚 Next Steps

- Read `EMAIL_AGENT_README.md` for complete documentation
- Run `python example_email_agent.py` for advanced usage examples
- Use `python deploy_production.py` for production deployment
- Check logs in `email_pdf_agent.log` for monitoring

## 💡 Pro Tips

1. **Test with small PDFs first** to verify everything works
2. **Use a dedicated email** for monitoring to avoid processing personal emails
3. **Set up sender whitelist** for security in production
4. **Monitor the logs** to see what's happening
5. **Start with frequent checking** (60s) then adjust based on your needs

---

🎉 **You're all set!** Your Email PDF Agent is now automatically processing PDF attachments and sending you summaries. Enjoy the time savings!
