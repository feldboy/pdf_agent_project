# PDF Agent Project - Organized Structure

## 📁 Project Organization

```
pdf_agent_project/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core PDF processing
│   │   ├── pdf_agent.py             # Main PDF agent
│   │   ├── advanced_pdf_agent.py    # Advanced features
│   │   ├── config.py                # Configuration management
│   │   └── create_pdf.py            # PDF generation utilities
│   │
│   ├── 📁 email_agent/              # Email processing
│   │   ├── email_pdf_agent.py       # Email PDF processor
│   │   └── example_email_agent.py   # Example implementation
│   │
│   ├── 📁 legal_system/             # Legal case processing
│   │   ├── legal_case_processor.py  # Case data processing
│   │   ├── legal_case_monitor.py    # Email monitoring
│   │   ├── legal_case_system.py     # System integration
│   │   └── demo_legal_case_system.py # Demo script
│   │
│   ├── 📁 telegram_bot/             # Telegram integration
│   │   └── (setup files moved here)
│   │
│   └── 📁 twitter_monitor/          # Twitter monitoring
│       └── twitter_ai_monitor.py    # AI tweet monitor
│
├── 📁 tests/                        # Test suite
│   ├── test_agent.py                # Core agent tests
│   ├── test_email_agent.py          # Email agent tests
│   ├── test_legal_case_processor.py # Legal system tests
│   ├── test_multi_police_reports.py # Multi-report tests
│   ├── test_telegram_bot.py         # Telegram bot tests
│   └── demo_pdf_agent.py            # Demo script
│
├── 📁 config/                       # Configuration files
│   ├── email_config.py              # Email settings
│   ├── legal_case_config.py         # Legal case settings
│   ├── twitter_monitor_config.json  # Twitter config
│   ├── requirements.txt             # Python dependencies
│   ├── legal_requirements.txt       # Legal system deps
│   └── twitter_ai_requirements.txt  # Twitter deps
│
├── 📁 docs/                         # Documentation
│   ├── README.md                    # Main documentation
│   ├── EMAIL_AGENT_README.md        # Email agent guide
│   ├── LEGAL_CASE_SYSTEM_README.md  # Legal system guide
│   ├── POLICE_REPORT_ENHANCEMENT.md # Police report features
│   ├── PROJECT_SUMMARY.md           # Project overview
│   ├── QUICKSTART.md               # Quick start guide
│   └── QUICK_REFERENCE.md          # Quick reference
│
├── 📁 deployment/                   # Production deployment
│   ├── deploy_production.py         # Deployment script
│   └── production_pdf_agent.py      # Production agent
│
├── 📁 setup/                        # Setup scripts
│   ├── setup_email_agent.py         # Email agent setup
│   ├── setup_legal_case_system.py   # Legal system setup
│   └── setup_telegram_bot.py        # Telegram bot setup
│
├── 📁 logs/                         # Log files
│   ├── email_pdf_agent.log          # Email agent logs
│   ├── legal_case_monitor.log       # Legal monitor logs
│   ├── legal_case_processor.log     # Legal processor logs
│   └── legal_case_system.log        # Legal system logs
│
├── 📁 sample_data/                  # Sample files
│   ├── knowledge_base.pdf           # Sample knowledge base
│   ├── demo_comprehensive_report.txt # Sample report
│   └── sample_legal_case_report.txt # Sample legal report
│
├── .env                             # Environment variables
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Configure Environment**
   - Copy and edit `.env` file with your API keys
   - Update configuration files in `config/` directory

3. **Run Tests**
   ```bash
   python tests/test_agent.py          # Test core functionality
   python tests/test_email_agent.py    # Test email processing
   python tests/test_legal_case_processor.py # Test legal system
   ```

4. **Start Services**
   ```bash
   # Core PDF Agent
   python src/core/pdf_agent.py
   
   # Email Agent
   python src/email_agent/email_pdf_agent.py
   
   # Legal Case System
   python src/legal_system/legal_case_monitor.py
   ```

## 📋 Components

### Core PDF Agent (`src/core/`)
- **pdf_agent.py**: Main PDF processing engine
- **advanced_pdf_agent.py**: Advanced AI-powered features
- **config.py**: Configuration management
- **create_pdf.py**: PDF generation utilities

### Email Agent (`src/email_agent/`)
- **email_pdf_agent.py**: Email-based PDF processing
- **example_email_agent.py**: Example implementation

### Legal Case System (`src/legal_system/`)
- **legal_case_processor.py**: Case data extraction and analysis
- **legal_case_monitor.py**: Email monitoring for legal cases
- **legal_case_system.py**: Integrated legal case processing

### Testing (`tests/`)
- Comprehensive test suite for all components
- Demo scripts and examples
- Integration tests

## 🔧 Configuration

All configuration files are located in the `config/` directory:
- `email_config.py`: Email server settings
- `legal_case_config.py`: Legal case processing settings
- `*.requirements.txt`: Python dependencies for each component

## 📊 Monitoring & Logs

- Log files are stored in the `logs/` directory
- Each component has its own log file
- Structured logging with timestamps and severity levels

## 🚀 Deployment

Production deployment files are in the `deployment/` directory:
- `deploy_production.py`: Automated deployment script
- `production_pdf_agent.py`: Production-ready agent

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:
- Component-specific guides
- API reference
- Quick start tutorials
- Best practices

## 🛠️ Development

1. **Setup Development Environment**
   ```bash
   python setup/setup_email_agent.py
   python setup/setup_legal_case_system.py
   ```

2. **Run in Development Mode**
   ```bash
   python src/core/pdf_agent.py --dev
   ```

3. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

## 📝 License

This project is organized for maximum maintainability and scalability.
Each component is modular and can be deployed independently.
