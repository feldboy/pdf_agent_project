#!/usr/bin/env python3
"""
Production PDF Knowledge Base Agent using Agno
Clean, configurable implementation with proper error handling
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.reasoning import ReasoningTools

from config import PDFAgentConfig

class PDFKnowledgeAgent:
    """Production-ready PDF Knowledge Base Agent"""
    
    def __init__(self, pdf_paths: Optional[List[str]] = None, config: Optional[PDFAgentConfig] = None):
        """
        Initialize the PDF Knowledge Agent
        
        Args:
            pdf_paths: List of PDF file paths to process
            config: Configuration object (uses default if None)
        """
        self.config = config or PDFAgentConfig
        self.pdf_paths = pdf_paths or [self.config.DEFAULT_PDF_PATH]
        self.agent = None
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate the setup before creating the agent"""
        errors = self.config.validate_config()
        
        # Check if PDF files exist
        for pdf_path in self.pdf_paths:
            if not Path(pdf_path).exists():
                errors.append(f"PDF file not found: {pdf_path}")
        
        if errors:
            print("❌ Setup errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
    
    def create_agent(self) -> Agent:
        """Create and configure the PDF knowledge agent"""
        
        print("🤖 Creating PDF Knowledge Agent...")
        
        # Prepare PDF sources with metadata
        pdf_sources = self.config.get_pdf_sources(self.pdf_paths)
        
        # Create PDF knowledge base
        pdf_knowledge = PDFKnowledgeBase(
            path=pdf_sources,
            vector_db=LanceDb(
                uri=self.config.VECTOR_DB_URI,
                table_name=self.config.VECTOR_DB_TABLE,
                search_type=getattr(SearchType, self.config.SEARCH_TYPE.lower()),
                embedder=OpenAIEmbedder(
                    id=self.config.EMBEDDING_MODEL,
                    dimensions=self.config.EMBEDDING_DIMENSIONS
                ),
            ),
        )
        
        # Create tools
        tools = []
        if self.config.ENABLE_REASONING:
            tools.append(ReasoningTools(add_instructions=True))
        
        # Create the agent
        self.agent = Agent(
            name=self.config.AGENT_NAME,
            model=OpenAIChat(**self.config.get_model_config("openai")),
            instructions=self.config.SYSTEM_INSTRUCTIONS,
            knowledge=pdf_knowledge,
            tools=tools,
            add_datetime_to_instructions=True,
            markdown=self.config.ENABLE_MARKDOWN,
            show_tool_calls=self.config.SHOW_TOOL_CALLS,
            debug_mode=self.config.ENABLE_DEBUG,
        )
        
        return self.agent
    
    def load_knowledge_base(self, recreate: bool = False):
        """Load the PDF knowledge base"""
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")
        
        print("📚 Loading PDF knowledge base...")
        self.agent.knowledge.load(recreate=recreate)
        print("✅ Knowledge base loaded successfully!")
    
    def ask(self, question: str, stream: bool = None) -> str:
        """Ask a question to the agent"""
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")
        
        if stream is None:
            stream = self.config.STREAM_RESPONSES
        
        response = self.agent.run(question)
        return response.content
    
    def chat_interactive(self):
        """Start an interactive chat session"""
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")
        
        print(f"🎯 {self.config.AGENT_NAME} is ready!")
        print("💡 Ask questions about your PDF documents")
        print("📝 Type 'help' for commands, 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🤔 Your question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                elif user_input.lower() == 'info':
                    self._show_info()
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 Thinking...")
                print("-" * 40)
                
                self.agent.print_response(
                    user_input,
                    stream=self.config.STREAM_RESPONSES,
                    show_full_reasoning=self.config.ENABLE_DEBUG,
                )
                
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if self.config.ENABLE_DEBUG:
                    import traceback
                    traceback.print_exc()
    
    def _show_help(self):
        """Show help information"""
        print("\n📋 Available commands:")
        print("   - Ask any question about your PDF documents")
        print("   - 'info' - Show information about loaded documents")
        print("   - 'help' - Show this help message")
        print("   - 'quit' - Exit the chat")
    
    def _show_info(self):
        """Show information about loaded documents"""
        print("\n📚 Loaded documents:")
        for pdf_path in self.pdf_paths:
            print(f"   - {Path(pdf_path).name}")
        print(f"\n🔧 Configuration:")
        print(f"   - Model: {self.config.DEFAULT_MODEL}")
        print(f"   - Embedding: {self.config.EMBEDDING_MODEL}")
        print(f"   - Search: {self.config.SEARCH_TYPE}")

def main():
    """Main function"""
    print("🚀 PDF Knowledge Base Agent with Agno")
    print("=" * 40)
    
    # You can specify custom PDF paths here
    # pdf_paths = ["your_document1.pdf", "your_document2.pdf"]
    pdf_paths = None  # Uses default from config
    
    try:
        # Create agent
        agent_manager = PDFKnowledgeAgent(pdf_paths=pdf_paths)
        agent = agent_manager.create_agent()
        
        # Load knowledge base
        agent_manager.load_knowledge_base(recreate=False)
        
        # Start interactive chat
        agent_manager.chat_interactive()
        
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
