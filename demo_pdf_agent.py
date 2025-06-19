#!/usr/bin/env python3
"""
Simple PDF Knowledge Base Agent Demo
"""

import os
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.reasoning import ReasoningTools

def demo_pdf_agent():
    """Demonstrate the PDF agent with sample questions"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🤖 Creating PDF Knowledge Base Agent...")
    
    # Create PDF knowledge base
    pdf_knowledge = PDFKnowledgeBase(
        path="knowledge_base.pdf",
        vector_db=LanceDb(
            uri="tmp/pdf_lancedb",
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
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "You are a helpful assistant that answers questions based on PDF knowledge.",
            "Always search your knowledge base before answering.",
            "Include relevant details from the PDF.",
            "Use clear formatting in your answers.",
        ],
        knowledge=pdf_knowledge,
        tools=[ReasoningTools(add_instructions=True)],
        markdown=True,
    )
    
    # Load the knowledge base
    print("📚 Loading PDF knowledge base...")
    agent.knowledge.load(recreate=False)
    
    print("✅ Agent ready! Asking sample questions...\n")
    
    # Sample questions
    questions = [
        "What is Artificial Intelligence?",
        "What are the types of Machine Learning?",
        "What are the applications of Natural Language Processing?",
        "What are the key benefits of AI?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"🤔 Question {i}: {question}")
        print("="*50)
        
        agent.print_response(question, stream=False)
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    demo_pdf_agent()
