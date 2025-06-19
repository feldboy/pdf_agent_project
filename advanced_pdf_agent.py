#!/usr/bin/env python3
"""
Advanced PDF Knowledge Base Agent with Multiple PDFs and Custom Features
"""

import os
from pathlib import Path
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.reasoning import ReasoningTools

def create_advanced_pdf_agent():
    """Create an advanced PDF agent with multiple documents and custom features"""
    
    # Example of using multiple PDFs with metadata
    pdf_sources = [
        {
            "path": "knowledge_base.pdf",
            "metadata": {
                "document_type": "AI_Knowledge",
                "source": "Internal Documentation",
                "created_by": "AI Team",
                "topic": "Artificial Intelligence Basics"
            }
        }
        # You can add more PDFs here:
        # {
        #     "path": "another_document.pdf", 
        #     "metadata": {"document_type": "Research", "topic": "Machine Learning"}
        # }
    ]
    
    # Create PDF knowledge base with multiple sources
    pdf_knowledge = PDFKnowledgeBase(
        path=pdf_sources,  # List of dictionaries with path and metadata
        vector_db=LanceDb(
            uri="tmp/advanced_pdf_lancedb",
            table_name="advanced_pdf_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(
                id="text-embedding-3-small", 
                dimensions=1536
            ),
        ),
    )
    
    # Create the agent with enhanced instructions
    agent = Agent(
        name="Advanced PDF Knowledge Assistant",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "You are an advanced AI assistant specialized in answering questions from PDF knowledge bases.",
            "Always search your knowledge base thoroughly before answering.",
            "When possible, mention the source document and page number of your information.",
            "If information comes from multiple sources, indicate this clearly.",
            "Provide comprehensive answers with relevant details.",
            "Use structured formatting (bullet points, numbered lists) when appropriate.",
            "If asked about the knowledge base itself, describe what documents you have access to.",
            "Be precise about what you know and don't know based on your knowledge base.",
        ],
        knowledge=pdf_knowledge,
        tools=[ReasoningTools(add_instructions=True)],
        add_datetime_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
        debug_mode=False,  # Set to True for debugging
    )
    
    return agent

def demonstrate_advanced_features():
    """Demonstrate advanced features of the PDF agent"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        return
    
    print("🚀 Creating Advanced PDF Knowledge Base Agent...")
    
    agent = create_advanced_pdf_agent()
    
    print("📚 Loading PDF knowledge base with metadata...")
    agent.knowledge.load(recreate=False)
    
    print("✅ Advanced Agent ready!\n")
    
    # Advanced questions that test different capabilities
    advanced_questions = [
        "What documents do you have access to?",
        "Compare the different types of machine learning mentioned in your knowledge base.",
        "Create a structured summary of AI benefits with examples.",
        "What are the ethical considerations around AI mentioned in your documents?",
        "Explain the relationship between AI, Machine Learning, and Deep Learning.",
    ]
    
    for i, question in enumerate(advanced_questions, 1):
        print(f"🧠 Advanced Question {i}: {question}")
        print("="*60)
        
        response = agent.run(question)
        print(response.content)
        
        # Show which sources were used (if available)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print("\n📖 Sources used:")
            for tool_call in response.tool_calls:
                if 'search' in tool_call.function.name.lower():
                    print(f"   - Knowledge base search performed")
        
        print("\n" + "="*60 + "\n")

def interactive_advanced_chat():
    """Interactive chat with advanced features"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        return
    
    print("🚀 Starting Advanced PDF Knowledge Assistant...")
    
    agent = create_advanced_pdf_agent()
    
    print("📚 Loading knowledge base...")
    agent.knowledge.load(recreate=False)
    
    print("✅ Ready for advanced interactions!")
    print("\n🎯 Special commands:")
    print("   - 'help' - Show available commands")
    print("   - 'sources' - List available documents")
    print("   - 'debug' - Toggle debug mode")
    print("   - 'quit' - Exit")
    print("\n" + "="*50)
    
    debug_mode = False
    
    while True:
        try:
            user_input = input("\n🤔 Ask me anything (or use special commands): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            elif user_input.lower() == 'help':
                print("\n📋 Available commands:")
                print("   - Ask any question about the PDF content")
                print("   - 'sources' - List available documents")
                print("   - 'debug' - Toggle debug mode")
                print("   - 'quit' - Exit")
                continue
                
            elif user_input.lower() == 'sources':
                print("\n📚 Available knowledge sources:")
                print("   - AI Knowledge Base (knowledge_base.pdf)")
                print("   - Topics: AI, Machine Learning, NLP, Deep Learning")
                continue
                
            elif user_input.lower() == 'debug':
                debug_mode = not debug_mode
                agent.debug_mode = debug_mode
                print(f"\n🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
                continue
            
            if not user_input:
                continue
            
            print(f"\n🤖 {'[DEBUG] ' if debug_mode else ''}Agent is thinking...")
            print("-" * 50)
            
            agent.print_response(
                user_input,
                stream=True,
                show_full_reasoning=debug_mode,
            )
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            if debug_mode:
                import traceback
                traceback.print_exc()
            continue

if __name__ == "__main__":
    print("🔥 Advanced PDF Knowledge Base Agent")
    print("Choose an option:")
    print("1. Run demonstration with sample questions")
    print("2. Start interactive chat")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        demonstrate_advanced_features()
    elif choice == "2":
        interactive_advanced_chat()
    else:
        print("Invalid choice. Running demonstration...")
        demonstrate_advanced_features()
