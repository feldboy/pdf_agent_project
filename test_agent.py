#!/usr/bin/env python3
"""
Test script for PDF Knowledge Base Agent
"""

import os
import sys
from pathlib import Path

def test_setup():
    """Test if the setup is correct"""
    print("🧪 Testing PDF Agent Setup...")
    print("=" * 40)
    
    errors = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append(f"Python 3.8+ required, found {sys.version}")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check required files
    required_files = [
        "knowledge_base.pdf",
        "requirements.txt",
        "config.py",
        "production_pdf_agent.py"
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ Found: {file}")
        else:
            errors.append(f"Missing file: {file}")
    
    # Check environment variables
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key is set")
    else:
        errors.append("OPENAI_API_KEY environment variable not set")
    
    # Check Python packages
    try:
        import agno
        print(f"✅ Agno version: {agno.__version__}")
    except ImportError:
        errors.append("Agno not installed")
    
    try:
        import pypdf
        print("✅ pypdf installed")
    except ImportError:
        errors.append("pypdf not installed")
    
    try:
        import openai
        print("✅ OpenAI package installed")
    except ImportError:
        errors.append("OpenAI package not installed")
    
    # Show results
    print("\n" + "=" * 40)
    
    if errors:
        print("❌ Setup issues found:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 To fix these issues:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set API key: export OPENAI_API_KEY='your-key'")
        print("   3. Ensure all files are present")
        return False
    else:
        print("✅ Setup is complete and ready to use!")
        return True

def test_pdf_processing():
    """Test PDF processing"""
    print("\n🧪 Testing PDF Processing...")
    print("=" * 40)
    
    try:
        from agno.knowledge.pdf import PDFKnowledgeBase
        from agno.embedder.openai import OpenAIEmbedder
        from agno.vectordb.lancedb import LanceDb, SearchType
        
        # Test creating PDF knowledge base
        pdf_knowledge = PDFKnowledgeBase(
            path="knowledge_base.pdf",
            vector_db=LanceDb(
                uri="tmp/test_lancedb",
                table_name="test_pdf",
                search_type=SearchType.vector,
                embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
            ),
        )
        
        print("✅ PDF knowledge base created successfully")
        
        # Test loading (this will actually process the PDF)
        if os.getenv("OPENAI_API_KEY"):
            print("🔄 Testing PDF loading (this may take a moment)...")
            pdf_knowledge.load(recreate=True)
            print("✅ PDF loaded and processed successfully")
        else:
            print("⚠️  Skipping PDF loading test (no API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF processing test failed: {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    print("\n🧪 Testing Agent Creation...")
    print("=" * 40)
    
    try:
        from production_pdf_agent import PDFKnowledgeAgent
        
        # Test agent creation without API calls
        if os.getenv("OPENAI_API_KEY"):
            agent_manager = PDFKnowledgeAgent()
            agent = agent_manager.create_agent()
            print("✅ Agent created successfully")
            
            # Test loading knowledge base
            agent_manager.load_knowledge_base(recreate=False)
            print("✅ Knowledge base loaded successfully")
            
            return True
        else:
            print("⚠️  Skipping agent test (no API key)")
            return True
            
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PDF Knowledge Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Setup Test", test_setup),
        ("PDF Processing Test", test_pdf_processing),
        ("Agent Creation Test", test_agent_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your PDF agent is ready to use.")
        print("\n🚀 Next steps:")
        print("   - Run: python production_pdf_agent.py")
        print("   - Or try: python demo_pdf_agent.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
