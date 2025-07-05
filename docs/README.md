# PDF Knowledge Base Agent with Agno

This project demonstrates how to create an AI agent using Agno that can read from PDF knowledge bases and answer questions based on the content.

## Features

- **PDF Processing**: Automatically extracts text from PDF files
- **Vector Database**: Uses LanceDB with OpenAI embeddings for semantic search
- **RAG (Retrieval Augmented Generation)**: Combines retrieval and generation for accurate answers
- **Reasoning Tools**: Uses Agno's reasoning capabilities for better responses
- **Interactive Chat**: Ask questions and get answers based on PDF content

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Create Your PDF Knowledge Base

The project includes a sample PDF (`knowledge_base.pdf`) about AI topics. You can:

- Use the existing sample PDF
- Replace it with your own PDF file
- Modify the `path` parameter in the agent to point to your PDF

To create a new sample PDF:
```bash
python create_pdf.py
```

## Usage

### Quick Demo

Run the demo script to see the agent answer sample questions:

```bash
python demo_pdf_agent.py
```

### Interactive Chat

For an interactive chat experience:

```bash
python pdf_agent.py
```

## How It Works

1. **PDF Processing**: The agent uses `PDFKnowledgeBase` to extract text from PDF files using `pypdf`
2. **Embedding**: Text chunks are converted to embeddings using OpenAI's `text-embedding-3-small`
3. **Vector Storage**: Embeddings are stored in LanceDB for efficient similarity search
4. **Retrieval**: When asked a question, the agent searches for relevant chunks in the knowledge base
5. **Generation**: The agent uses the retrieved context to generate accurate answers using GPT-4o-mini

## Code Structure

- `pdf_agent.py` - Main interactive PDF agent
- `demo_pdf_agent.py` - Simple demo with sample questions
- `create_pdf.py` - Script to create a sample PDF
- `knowledge_base.pdf` - Sample PDF with AI knowledge
- `requirements.txt` - Python dependencies

## Key Components

### PDFKnowledgeBase
```python
pdf_knowledge = PDFKnowledgeBase(
    path="knowledge_base.pdf",
    vector_db=LanceDb(
        uri="tmp/pdf_lancedb",
        table_name="pdf_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
    ),
)
```

### Agent Configuration
```python
agent = Agent(
    name="PDF Knowledge Assistant",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[...],
    knowledge=pdf_knowledge,
    tools=[ReasoningTools(add_instructions=True)],
    markdown=True,
)
```

## Customization

### Using Your Own PDF
1. Replace `knowledge_base.pdf` with your PDF file
2. Update the `path` parameter in the agent code
3. Recreate the knowledge base: `agent.knowledge.load(recreate=True)`

### Different Models
You can use different models by changing the `model` parameter:
```python
# Using Anthropic Claude
from agno.models.anthropic import Claude
model=Claude(id="claude-3-sonnet-20240229")

# Using other OpenAI models
model=OpenAIChat(id="gpt-4")
```

### Advanced Features

- **Multiple PDFs**: Pass a list of PDF paths to process multiple documents
- **Metadata**: Add custom metadata to enhance search and retrieval
- **Different Embedders**: Use different embedding models for better performance
- **Custom Instructions**: Modify agent instructions for specific use cases

## Troubleshooting

### Common Issues

1. **OpenAI API Key**: Make sure your API key is set correctly
2. **PDF Format**: Ensure your PDF contains extractable text (not just images)
3. **Dependencies**: Install all required packages from `requirements.txt`
4. **Vector Database**: The LanceDB will be created automatically in `tmp/pdf_lancedb/`

### Performance Tips

- Use `SearchType.hybrid` for better search results
- Adjust chunk size for different document types
- Consider using different embedding models for specialized content

## Next Steps

- Add support for multiple PDF files
- Implement conversation memory
- Add web interface with Streamlit
- Integrate with other knowledge sources
- Add conversation history and context

## License

This project is open source and available under the MIT License.
