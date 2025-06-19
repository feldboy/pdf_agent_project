# Legal Case Processing System - Quick Reference

## 🚀 Quick Start Commands

```bash
# 1. Setup (run once)
python setup_legal_case_system.py

# 2. Test system  
python legal_case_system.py --mode test

# 3. See demo
python legal_case_system.py --mode demo
python demo_legal_case_system.py

# 4. Start monitoring
python legal_case_system.py --mode monitor
```

## 📧 Email Setup (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create App Password**: Google Account → Security → 2-Step Verification → App passwords
3. **Update .env file**:
   ```bash
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-16-digit-app-password
   RECIPIENT_EMAIL=ron@yourcompany.com
   ```

## 🔑 API Key Setup

### OpenAI (Recommended)
1. Visit: https://platform.openai.com/api-keys
2. Create new API key
3. Add credits to your account
4. Update .env: `OPENAI_API_KEY=sk-...`

### Anthropic (Alternative)
1. Visit: https://console.anthropic.com/
2. Create API key  
3. Update .env: `ANTHROPIC_API_KEY=sk-ant-...`

## 📋 System Files Overview

| File | Purpose |
|------|---------|
| `legal_case_system.py` | Main startup script |
| `legal_case_processor.py` | Core AI processing |
| `legal_case_monitor.py` | Email monitoring |
| `demo_legal_case_system.py` | No-API demo |
| `setup_legal_case_system.py` | Easy setup |
| `.env` | Configuration settings |

## 🔍 Testing Individual Components

```bash
# Test specific components
python test_legal_case_processor.py extraction
python test_legal_case_processor.py location  
python test_legal_case_processor.py attorney
python test_legal_case_processor.py pipeline
```

## 📊 Sample Email Processing

### Input: Law Firm Email
```
Subject: Auto Accident Case - Jane Doe
From: attorney@lawfirm.com
Attachments: medical_records.pdf, police_report.pdf

Dear Ron,
Please find attached case materials...
```

### Output: AI Analysis Report
```
# Case Summary: Jane Doe | Auto Accident | Los Angeles, CA

## 📄 Case Summary
- Client: Jane Doe  
- Date of Loss: May 3, 2024
- Injuries: Neck strain, back pain
- Attorney: Sarah Levine (verified)

## ❗ Missing Information
- Policy limits unknown
- Treatment timeline incomplete
- Prior injuries not disclosed

## 🌍 Location Risk: HIGH
- Los Angeles = Tort-friendly jurisdiction
- Expect higher settlement demands

## 📊 Recommendations
- Obtain policy limits immediately
- Consider early settlement discussions
```

## ⚙️ Configuration Options

### Email Settings
```bash
CHECK_INTERVAL=300         # Check every 5 minutes
MONITOR_FOLDER=INBOX      # Email folder to watch
MAX_PDF_SIZE=20971520     # 20MB PDF limit
```

### AI Settings  
```bash
MODEL_PROVIDER=openai     # openai, anthropic, google
MODEL_NAME=gpt-4o        # AI model to use
MAX_TOKENS=8000          # Response length limit
TEMPERATURE=0.1          # Creativity (0.1 = focused)
```

## 🚨 Troubleshooting

### Email Connection Issues
- ✅ Use Gmail app passwords (not main password)
- ✅ Enable IMAP access in Gmail settings
- ✅ Check firewall/antivirus blocking

### API Issues
- ✅ Verify API key is correct and active
- ✅ Check account has sufficient credits
- ✅ Confirm model name is valid

### Processing Issues
- ✅ Check PDF files aren't password protected  
- ✅ Verify PDF files under size limit
- ✅ Review logs for detailed errors

## 📁 Log Files

| File | Contains |
|------|----------|
| `legal_case_system.log` | Main system events |
| `legal_case_monitor.log` | Email monitoring |
| `legal_case_processor.log` | AI processing |

## 🎯 Production Checklist

- [ ] Python 3.8+ installed
- [ ] All packages installed
- [ ] .env file configured  
- [ ] Email credentials working
- [ ] API key valid with credits
- [ ] System tests passing
- [ ] Demo runs successfully

## 📞 Getting Help

1. **Run diagnostics**: `python legal_case_system.py --mode test`
2. **Check logs**: Review .log files for errors
3. **Try demo mode**: `python demo_legal_case_system.py`
4. **Read documentation**: `LEGAL_CASE_SYSTEM_README.md`

---

**Ready to process legal cases automatically?** 
Run `python legal_case_system.py --mode monitor` to start!
