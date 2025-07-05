#!/usr/bin/env python3
"""
Production deployment script for Email PDF Agent

This script helps deploy the Email PDF Agent in production environments
with proper configuration, monitoring, and error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from email_config import EmailPDFConfig

class ProductionDeployment:
    """Production deployment manager for Email PDF Agent"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.log_dir = self.project_dir / "logs"
        self.config_dir = self.project_dir / "config"
        
    def setup_directories(self):
        """Create necessary directories"""
        print("📁 Setting up directories...")
        
        directories = [
            self.log_dir,
            self.config_dir,
            self.project_dir / "tmp",
            self.project_dir / "data",
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"   ✅ {directory}")
    
    def setup_logging(self):
        """Configure production logging"""
        print("📊 Configuring production logging...")
        
        log_config = f"""
import logging.config

LOGGING_CONFIG = {{
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {{
        'detailed': {{
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        }},
        'simple': {{
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }}
    }},
    'handlers': {{
        'file': {{
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '{self.log_dir}/email_pdf_agent.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'INFO'
        }},
        'error_file': {{
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '{self.log_dir}/email_pdf_agent_errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'ERROR'
        }},
        'console': {{
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        }}
    }},
    'root': {{
        'level': 'INFO',
        'handlers': ['file', 'error_file', 'console']
    }}
}}

def setup_production_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
"""
        
        with open(self.config_dir / "logging_config.py", 'w') as f:
            f.write(log_config)
        
        print("   ✅ Logging configuration created")
    
    def create_systemd_service(self):
        """Create systemd service file"""
        print("🔧 Creating systemd service...")
        
        service_content = f"""[Unit]
Description=Email PDF Processing Agent
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User={os.getenv('USER', 'emailpdf')}
Group={os.getenv('USER', 'emailpdf')}
WorkingDirectory={self.project_dir}
Environment=PATH={sys.executable}
ExecStart={sys.executable} email_pdf_agent.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=email-pdf-agent

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={self.project_dir}

# Resource limits
LimitNOFILE=65536
MemoryLimit=1G

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.project_dir / "email-pdf-agent.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"   ✅ Service file created: {service_file}")
        print("   📝 To install, run:")
        print(f"      sudo cp {service_file} /etc/systemd/system/")
        print("      sudo systemctl daemon-reload")
        print("      sudo systemctl enable email-pdf-agent")
        print("      sudo systemctl start email-pdf-agent")
    
    def create_docker_files(self):
        """Create Docker deployment files"""
        print("🐳 Creating Docker files...")
        
        # Dockerfile
        dockerfile_content = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash emailpdf
RUN chown -R emailpdf:emailpdf /app
USER emailpdf

# Create necessary directories
RUN mkdir -p logs tmp data

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "email_pdf_agent.py"]
"""
        
        with open(self.project_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Docker Compose
        compose_content = """version: '3.8'

services:
  email-pdf-agent:
    build: .
    container_name: email-pdf-agent
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./tmp:/app/tmp
    healthcheck:
      test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/logs/email_pdf_agent.log') else 1)"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Add monitoring with Prometheus/Grafana
  # prometheus:
  #   image: prom/prometheus
  #   ports:
  #     - "9090:9090"
  #   volumes:
  #     - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
"""
        
        with open(self.project_dir / "docker-compose.yml", 'w') as f:
            f.write(compose_content)
        
        print("   ✅ Dockerfile created")
        print("   ✅ docker-compose.yml created")
    
    def create_monitoring_config(self):
        """Create monitoring and alerting configuration"""
        print("📊 Creating monitoring configuration...")
        
        monitoring_dir = self.project_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        # Health check script
        health_check = """#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

def check_log_activity():
    \"\"\"Check if the agent is actively logging\"\"\"
    log_file = Path("logs/email_pdf_agent.log")
    
    if not log_file.exists():
        return False, "Log file does not exist"
    
    # Check if log was modified in the last 10 minutes
    last_modified = log_file.stat().st_mtime
    current_time = time.time()
    
    if current_time - last_modified > 600:  # 10 minutes
        return False, f"Log file not updated in {(current_time - last_modified)/60:.1f} minutes"
    
    return True, "Agent is active"

def check_process():
    \"\"\"Check if the agent process is running\"\"\"
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'email_pdf_agent.py' in cmdline:
                return True, f"Agent process found (PID: {proc.info['pid']})"
        return False, "Agent process not found"
    except ImportError:
        return True, "psutil not available, skipping process check"

def main():
    checks = [
        ("Log Activity", check_log_activity),
        ("Process Check", check_process),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{check_name}: {status} - {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"{check_name}: ❌ ERROR - {e}")
            all_passed = False
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
"""
        
        with open(monitoring_dir / "health_check.py", 'w') as f:
            f.write(health_check)
        
        # Make executable
        os.chmod(monitoring_dir / "health_check.py", 0o755)
        
        print("   ✅ Health check script created")
    
    def create_backup_script(self):
        """Create backup and recovery scripts"""
        print("💾 Creating backup scripts...")
        
        backup_script = f"""#!/bin/bash
# Email PDF Agent Backup Script

BACKUP_DIR="/var/backups/email-pdf-agent"
PROJECT_DIR="{self.project_dir}"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration
echo "📁 Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$PROJECT_DIR" .env config/

# Backup logs (last 7 days)
echo "📊 Backing up recent logs..."
find "$PROJECT_DIR/logs" -name "*.log*" -mtime -7 -exec tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" {{}} +

# Backup data directory
if [ -d "$PROJECT_DIR/data" ]; then
    echo "💾 Backing up data..."
    tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" -C "$PROJECT_DIR" data/
fi

# Clean old backups (keep 30 days)
echo "🧹 Cleaning old backups..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $BACKUP_DIR"
ls -la "$BACKUP_DIR"
"""
        
        backup_file = self.project_dir / "scripts" / "backup.sh"
        backup_file.parent.mkdir(exist_ok=True)
        
        with open(backup_file, 'w') as f:
            f.write(backup_script)
        
        os.chmod(backup_file, 0o755)
        
        print(f"   ✅ Backup script created: {backup_file}")
    
    def create_production_config(self):
        """Create production-specific configuration"""
        print("⚙️ Creating production configuration...")
        
        prod_env = """# Production Configuration for Email PDF Agent
# Copy this to .env and customize for your environment

# === EMAIL CONFIGURATION ===
EMAIL_ADDRESS=
EMAIL_PASSWORD=
SENDER_EMAIL=
SENDER_PASSWORD=
RECIPIENT_EMAIL=

# === EMAIL SERVER SETTINGS ===
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
MONITOR_FOLDER=INBOX

# === PROCESSING SETTINGS ===
CHECK_INTERVAL=300  # 5 minutes for production
MAX_PDF_SIZE=20971520  # 20MB for production
PROCESS_ALL_PDFS=true

# === LLM CONFIGURATION ===
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=
MAX_TOKENS=4000
TEMPERATURE=0.1

# === SECURITY & FILTERING ===
# Comma-separated list of allowed senders (optional)
# SENDER_WHITELIST=trusted@domain.com,reports@company.com

# Comma-separated list of required subject keywords (optional)
# SUBJECT_KEYWORDS=report,document,analysis

# === PRODUCTION FEATURES ===
ENABLE_HEALTH_CHECK=true
ENABLE_METRICS=true
LOG_LEVEL=INFO
"""
        
        with open(self.project_dir / ".env.production", 'w') as f:
            f.write(prod_env)
        
        print("   ✅ Production .env template created")
    
    def deploy(self):
        """Run full production deployment"""
        print("🚀 Starting Production Deployment")
        print("=" * 50)
        
        try:
            self.setup_directories()
            print()
            
            self.setup_logging()
            print()
            
            self.create_production_config()
            print()
            
            self.create_systemd_service()
            print()
            
            self.create_docker_files()
            print()
            
            self.create_monitoring_config()
            print()
            
            self.create_backup_script()
            print()
            
            print("🎉 Production deployment setup completed!")
            print("=" * 50)
            print()
            print("📋 Next Steps:")
            print("1. Copy .env.production to .env and configure your settings")
            print("2. Choose your deployment method:")
            print("   - Systemd: Use the email-pdf-agent.service file")
            print("   - Docker: Run 'docker-compose up -d'")
            print("3. Set up monitoring with scripts/health_check.py")
            print("4. Configure regular backups with scripts/backup.sh")
            print("5. Test your deployment with: python test_email_agent.py")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    deployment = ProductionDeployment()
    deployment.deploy()

if __name__ == "__main__":
    main()
