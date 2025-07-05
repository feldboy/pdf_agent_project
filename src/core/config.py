#!/usr/bin/env python3
"""
Configuration file for PDF Knowledge Base Agent
"""

import os
from pathlib import Path

class PDFAgentConfig:
    """Configuration class for PDF Agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL = "gpt-4o-mini"  # Cost-effective choice
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    
    # Vector Database Configuration
    VECTOR_DB_URI = "tmp/pdf_lancedb"
    VECTOR_DB_TABLE = "pdf_knowledge"
    SEARCH_TYPE = "hybrid"  # Options: "vector", "text", "hybrid"
    
    # PDF Configuration
    DEFAULT_PDF_PATH = "knowledge_base.pdf"
    EXCLUDE_FILES = []  # Files to exclude when processing directories
    
    # Agent Configuration
    AGENT_NAME = "PDF Knowledge Assistant"
    MAX_TOKENS = 4000
    TEMPERATURE = 0.1  # Lower for more consistent responses
    
    # Instructions
    SYSTEM_INSTRUCTIONS = [
        "You are a helpful AI assistant that answers questions based on PDF knowledge.",
        "Always search your knowledge base before answering questions.",
        "If information is not in your knowledge base, say so clearly.",
        "Include relevant details and page numbers when possible.",
        "Use clear and structured formatting in your answers.",
        "Be precise and accurate in your responses.",
    ]
    
    # Features
    ENABLE_REASONING = True
    ENABLE_DEBUG = False
    ENABLE_MARKDOWN = True
    SHOW_TOOL_CALLS = True
    STREAM_RESPONSES = True
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent
    PDF_DIRECTORY = PROJECT_ROOT / "pdfs"
    VECTOR_DB_PATH = PROJECT_ROOT / "tmp" / "pdf_lancedb"
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not Path(cls.DEFAULT_PDF_PATH).exists():
            errors.append(f"Default PDF file not found: {cls.DEFAULT_PDF_PATH}")
        
        return errors
    
    @classmethod
    def get_pdf_sources(cls, pdf_paths=None):
        """Get PDF sources with metadata"""
        if pdf_paths is None:
            pdf_paths = [cls.DEFAULT_PDF_PATH]
        
        sources = []
        for path in pdf_paths:
            if isinstance(path, str):
                sources.append({
                    "path": path,
                    "metadata": {
                        "document_name": Path(path).stem,
                        "file_type": "PDF",
                        "processed_by": "Agno PDF Agent"
                    }
                })
            else:
                sources.append(path)  # Already formatted
        
        return sources
    
    @classmethod
    def get_model_config(cls, model_type="openai"):
        """Get model configuration"""
        if model_type == "openai":
            return {
                "id": cls.DEFAULT_MODEL,
                "max_tokens": cls.MAX_TOKENS,
                "temperature": cls.TEMPERATURE,
            }
        elif model_type == "anthropic":
            return {
                "id": "claude-3-sonnet-20240229",
                "max_tokens": cls.MAX_TOKENS,
                "temperature": cls.TEMPERATURE,
            }
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

# Example usage and validation
if __name__ == "__main__":
    print("🔧 PDF Agent Configuration")
    print("=" * 40)
    
    # Validate configuration
    errors = PDFAgentConfig.validate_config()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuration is valid")
    
    print("\n📋 Current configuration:")
    print(f"   Model: {PDFAgentConfig.DEFAULT_MODEL}")
    print(f"   Embedding: {PDFAgentConfig.EMBEDDING_MODEL}")
    print(f"   Vector DB: {PDFAgentConfig.VECTOR_DB_URI}")
    print(f"   Default PDF: {PDFAgentConfig.DEFAULT_PDF_PATH}")
    print(f"   API Key set: {'Yes' if PDFAgentConfig.OPENAI_API_KEY else 'No'}")
