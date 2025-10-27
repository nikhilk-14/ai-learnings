# My Companion v2 - Lightweight Agentic AI

A lightweight personal AI assistant that enhances the original v1 with minimal agentic AI capabilities, vector search, and essential guardrails. This is the clean lightweight implementation - for enterprise features see v3.

## 🎯 **Features**

### ✅ **Lightweight Implementation**
- **Only 7 dependencies** (vs 25+ in enterprise version)
- **Simple architecture** with clear, maintainable code
- **Fast startup** and minimal resource usage

### 🤖 **Agentic AI Capabilities**
- **Basic Planning**: Keyword-based query planning with multi-step execution
- **Conversation Memory**: Maintains context across interactions (last 20 messages)
- **Self-Reflection**: Simple execution tracking and stats

### 🔍 **RAG Implementation**
- **Vector Database**: FAISS with sentence-transformers for semantic search
- **Hybrid Search**: Combines vector similarity with keyword matching
- **Auto-Embedding**: Automatically processes your knowledge base into vectors

### 🛡️ **Essential Guardrails**
- **Input Validation**: PII detection and masking, unsafe content blocking
- **Rate Limiting**: 10 requests per minute per user
- **Response Filtering**: Ensures safe AI responses
- **No External Dependencies**: Built-in security without heavy frameworks

### 🐳 **Docker Ready**
- **Lightweight Dockerfile**: Minimal image with essential dependencies
- **Docker Compose**: Ready for deployment with LM Studio integration
- **Health Checks**: Built-in monitoring and restart policies

## 📋 **Prerequisites**

1. **LM Studio** running locally on port 1234
2. **Python 3.11+** 
3. **Docker** (optional, for containerized deployment)

## 🚀 **Quick Start**

### **Local Development**

```bash
# Clone and navigate
cd d:\Ollama\code\my-companion\v2

# Install dependencies (lightweight)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LM Studio settings

# Run the application
streamlit run main.py
```

### **Docker Deployment**

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t companion-v2 .
docker run -p 8501:8501 companion-v2
```

## 📁 **Project Structure**

```
v2/
├── main.py                  # Main Streamlit application (lightweight)
├── core/                    # Core AI components
│   ├── agent.py            # Lightweight agentic AI implementation (Agent class)
│   ├── guardrails.py       # Basic safety and validation (Guardrails class)
│   └── vector_db.py        # FAISS-based vector database (VectorDB class)
├── app/                     # UI forms and components
├── utils/                   # Utilities and data management
├── requirements.txt         # Minimal dependencies (8 packages)
├── Dockerfile              # Lightweight Docker image
├── docker-compose.yml      # Simple container orchestration
├── .env.example            # Environment configuration
└── data/
    └── knowledge_base.json  # Your personal knowledge base
```

## ⚙️ **Configuration**

### **Environment Variables (.env)**

```bash
# LM Studio Configuration
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL=lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF

# Vector Database
VECTOR_MODEL=all-MiniLM-L6-v2
VECTOR_INDEX_PATH=data/vector_index

# Guardrails
MAX_REQUESTS_PER_MINUTE=10
ENABLE_PII_DETECTION=true
```

## 🔧 **Usage**

### **Web Interface**

1. **💬 AI Assistant**: 
   - Ask questions about your profile
   - Get planning-based responses with context
   - View execution details and search results

2. **📋 My Profile**: 
   - Browse your knowledge base sections
   - Same familiar interface as v1

### **Key Features to Try**

```
# Basic questions
"What are my Python skills?"

# Complex analysis (uses planning)
"Analyze my project experience and suggest areas for improvement"

# Context-aware queries (uses memory)
"Based on what we discussed, what should I focus on next?"
```

## 🔍 **How RAG Works**

1. **Document Processing**: Your knowledge base is automatically chunked and embedded
2. **Vector Search**: Questions are semantically matched against your data
3. **Hybrid Retrieval**: Combines vector similarity with keyword matching
4. **Context Building**: Relevant information is provided to the LLM
5. **Response Generation**: AI generates personalized responses using your data

## 🛡️ **Safety Features**

- **PII Detection**: Automatically masks emails, phone numbers, SSNs
- **Content Filtering**: Blocks unsafe or inappropriate content
- **Rate Limiting**: Prevents API abuse
- **Input Sanitization**: Cleans user input before processing
- **Response Validation**: Ensures AI responses are safe

## 📊 **Monitoring**

### **Built-in Stats**
- Conversation history length
- Vector database document count
- Guardrails activity
- Agent execution metrics

### **Health Checks**
- LLM connection status
- Vector database availability
- System component health

## 🔄 **Maintenance**

### **Rebuild Vector Database**
```bash
# Via UI: Click "🔄 Rebuild Vector DB" in sidebar
# Automatically rebuilds when knowledge_base.json changes
```

### **Clear Chat History**
```bash
# Via UI: Click "🧹 Clear Chat History" in sidebar
```

## 🆚 **Version Comparison**

| Feature | v1 | v2 Lightweight | v3 Enterprise |
|---------|----|---------|--------------| 
| Dependencies | 3 | 8 | 25+ |
| AI Capability | Simple Q&A | Agentic Planning | Advanced Agents |
| Search | Keyword only | Vector + Keyword | ChromaDB + Hybrid |
| Memory | None | 20 messages | Persistent Memory |
| Safety | None | Essential guardrails | Enterprise Security |
| Docker | Basic | Lightweight | Production-ready |
| Planning | None | Multi-step execution | Complex Orchestration |
| Use Case | Learning | Personal Use | Production Deployment |

## 🐛 **Troubleshooting**

### **Common Issues**

1. **LM Studio Connection Error**
   - Ensure LM Studio is running on port 1234
   - Check firewall settings
   - Verify model is loaded in LM Studio

2. **Vector Database Issues**
   - Delete `data/vector_index*` files and restart
   - Click "Rebuild Vector DB" in the UI

3. **Memory Issues**
   - Lightweight version uses minimal RAM
   - Vector embeddings cached automatically

## 📈 **Performance**

- **Startup Time**: ~5-10 seconds
- **Memory Usage**: ~200-500MB (depending on model cache)
- **Response Time**: 1-3 seconds for simple queries
- **Vector Search**: Sub-second for typical knowledge base sizes

## 🔮 **What's Next**

This lightweight v2 provides the perfect foundation for:
- Personal AI assistant with agentic capabilities
- Learning about RAG and vector databases
- Experimenting with lightweight AI implementations
- **Upgrading to v3** when you need enterprise features

## 🚀 **Need More Power?**

If you need enterprise features, check out **v3**:
- Advanced agentic AI with multi-agent orchestration
- ChromaDB vector database with production features
- Comprehensive security and audit logging
- Production-grade deployment and monitoring

```bash
# Upgrade to enterprise version
cd ../v3
pip install -r requirements.txt
streamlit run main.py
```

---

## 📝 **License**

Personal use - enhance and extend as needed!

## 🤝 **Support**

This is a lightweight, self-contained implementation. Refer to:
- LM Studio documentation for LLM setup
- Streamlit docs for UI customization
- FAISS documentation for vector database tuning