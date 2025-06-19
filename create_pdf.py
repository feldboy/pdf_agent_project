#!/usr/bin/env python3
"""
Convert markdown to PDF using reportlab
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_pdf():
    """Create a sample PDF with AI knowledge"""
    
    # Create the PDF
    pdf_path = "knowledge_base.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor='blue'
    )
    
    # Content
    story = []
    
    # Title
    story.append(Paragraph("AI Knowledge Base", title_style))
    story.append(Spacer(1, 12))
    
    # Content sections
    sections = [
        ("About Artificial Intelligence", 
         "Artificial Intelligence (AI) is a broad field of computer science that focuses on creating intelligent machines capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding."),
        
        ("Machine Learning",
         "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to analyze and draw inferences from patterns in data."),
        
        ("Types of Machine Learning",
         "1. Supervised Learning: Learning with labeled data<br/>2. Unsupervised Learning: Finding patterns in unlabeled data<br/>3. Reinforcement Learning: Learning through trial and error with rewards"),
        
        ("Natural Language Processing",
         "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language. It bridges the gap between human communication and computer understanding."),
        
        ("Applications of NLP",
         "• Chatbots and virtual assistants<br/>• Language translation<br/>• Sentiment analysis<br/>• Text summarization<br/>• Speech recognition"),
        
        ("Deep Learning",
         "Deep Learning is a subset of machine learning that uses neural networks with multiple layers (deep neural networks) to model and understand complex patterns in data."),
        
        ("Key Benefits of AI",
         "1. Automation: AI can automate repetitive tasks<br/>2. Efficiency: Faster processing and decision-making<br/>3. Accuracy: Reduced human error in complex calculations<br/>4. Availability: 24/7 operation without breaks<br/>5. Scalability: Can handle large volumes of data"),
        
        ("Future of AI",
         "The future of AI holds tremendous potential for transforming various industries including healthcare, finance, transportation, and education. However, it also raises important questions about ethics, privacy, and the impact on employment."),
        
        ("Conclusion",
         "AI is rapidly evolving and becoming an integral part of our daily lives. Understanding its capabilities and limitations is crucial for leveraging its benefits while addressing potential challenges.")
    ]
    
    for title, content in sections:
        story.append(Paragraph(title, styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    print(f"PDF created: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_sample_pdf()
