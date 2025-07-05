#!/usr/bin/env python3
"""
PDF Knowledge Base Agent using Agno
This agent can read from PDF files and answer questions based on the content.
"""

import os
from pathlib import Path
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.reasoning import ReasoningTools

# Set up environment variables (you'll need to set these)
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

def create_pdf_agent():
    """Create an agent that can read from PDF knowledge base"""
    
    # Create PDF knowledge base
    pdf_knowledge = PDFKnowledgeBase(
        path="knowledge_base.pdf",  # Path to your PDF file
        vector_db=LanceDb(
            uri="tmp/pdf_lancedb",  # Local vector database
            table_name="pdf_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(
                id="text-embedding-3-small", 
                dimensions=1536
            ),
        ),
    )
    
    # Create the agent
    agent = Agent(
        name="PDF Knowledge Assistant",
        model=OpenAIChat(id="gpt-4o-mini"),  # Using GPT-4o-mini as it's cost-effective
        instructions=[
            "You are a helpful assistant that can answer questions based on PDF knowledge.",
            "Always search your knowledge base before answering questions.",
            "If the information is not in your knowledge base, say so clearly.",
            "Include relevant details from the PDF in your responses.",
            "Use clear and structured formatting in your answers.",
            "If asked about sources, mention that the information comes from the PDF knowledge base.",
        ],
        knowledge=pdf_knowledge,
        tools=[ReasoningTools(add_instructions=True)],
        add_datetime_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
    )
    
    return agent

def main():
    """Main function to run the PDF agent"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        print("   You can do this by running: export OPENAI_API_KEY='your-api-key-here'")
        print("   Or add it to your .env file")
        return
    
    print("🤖 Creating PDF Knowledge Base Agent...")
    
    # Create the agent
    agent = create_pdf_agent()
    
    # Load the knowledge base (this will process the PDF and create embeddings)
    print("📚 Loading PDF knowledge base...")
    agent.knowledge.load(recreate=False)  # Set to True to recreate if needed
    
    print("✅ PDF Knowledge Base Agent is ready!")
    print("📖 Knowledge base loaded from: knowledge_base.pdf")
    print("\n" + "="*50)
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("\n🤔 Ask me anything about the PDF content (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent is thinking...")
            print("-" * 40)
            
            # Get response from agent
            agent.print_response(
                user_input,
                stream=True,
                show_full_reasoning=True,
            )
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
