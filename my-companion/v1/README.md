# My Companion App

A personal companion application built with Streamlit that helps you manage and interact with your professional profile, skills, projects, and experiences using a local LLM.

## Features

- **👤 Basic Information**: Manage your personal and professional details
- **⚙️ Technical Skills**: Organize skills by categories with dynamic management
- **🧱 Projects**: Document your projects with detailed descriptions and responsibilities
- **🌟 Other Activities**: Track additional activities, achievements, and experiences
- **🧠 Knowledge Base**: View all your data in structured and raw JSON formats
- **💬 Ask Companion**: AI-powered Q&A using your profile data with local LLM

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11
- **LLM**: Local LLM server (LM Studio compatible)
- **Search**: FAISS vector search with sentence transformers
- **Data**: JSON file-based storage
- **Deployment**: Docker support

## Prerequisites

- Python 3.11+
- Local LLM server running on `localhost:1234` (e.g., LM Studio)
- Docker (optional, for containerized deployment)

## Quick Start

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd my-companion/v1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

5. **Access the app:**
   Open `http://localhost:8501` in your browser

### Docker Deployment

1. **Build and run with Docker:**
   ```bash
   docker-compose up --build
   ```

2. **Access the app:**
   Open `http://localhost:8501` in your browser

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```properties
# LLM Configuration
LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
LLM_MODEL=local-model
LLM_TIMEOUT=300
LLM_TEMPERATURE=0.7

# Data Configuration
DATA_FILE=data/knowledge_base.json
ATTACHMENTS_DIR=data/attachments

# Ask Companion Configuration
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
TOP_K=6
CHUNK_SIZE=400
```

## Project Structure

```
v1/
├── app/                          # Application modules
│   ├── basic_info.py            # Basic information management
│   ├── technical_skills.py      # Technical skills management
│   ├── projects.py              # Project management
│   ├── other_activities.py      # Activities management
│   ├── knowledge_base.py        # Knowledge base viewer
│   └── ask_companion.py         # AI Q&A interface
├── utils/                       # Utility modules
│   ├── data_store.py           # Data persistence layer
│   └── local_llm.py            # LLM integration
├── data/                        # Data directory (not in Docker image)
│   ├── knowledge_base.json     # Main data file
│   └── attachments/            # File uploads
├── main.py                     # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── Dockerfile                  # Docker image definition
└── docker-compose.yml         # Docker compose configuration
```

## Usage

### Work Experience Tabs

The main interface organizes your professional information into tabs:

- **Basic Information**: Personal details, profile summary, attachments, and URLs
- **Technical Skills**: Categorized skill management with dynamic categories
- **Projects**: Project documentation with domain, role, description, and responsibilities
- **Other Activities**: Additional experiences, achievements, and related activities

### Knowledge Base

View your data in two formats:
- **Raw JSON**: Complete data structure in JSON format
- **Readable View**: Formatted, user-friendly presentation

### Ask Companion

AI-powered interface that:
- Builds a searchable index from your profile data and attachments
- Uses vector similarity search to find relevant context
- Queries your local LLM with context-aware prompts
- Provides accurate answers based on your personal data

## File Attachments

The app supports file uploads for:
- **Basic Info**: CV, certificates, documents
- **Other Activities**: Supporting documents, images, PDFs

Supported formats: PDF, DOCX, TXT, PNG, JPG

## Local LLM Setup

1. **Install LM Studio** or compatible local LLM server
2. **Start the server** on `localhost:1234`
3. **Load a model** (e.g., Llama, Mistral)
4. **Update `.env`** with your model name and endpoint

## Docker Notes

- **Data Persistence**: Local `data/` folder is mounted as volume
- **LLM Connection**: Uses `host.docker.internal:1234` to reach host LLM
- **Lightweight**: Data and cache folders excluded from image
- **Development**: Code changes reflect immediately with volume mounts

## Development

### Adding New Features

1. Create new module in `app/` directory
2. Import and add to main navigation in `main.py`
3. Update data structure in `utils/data_store.py` if needed
4. Add environment variables to `.env.example`

### Data Format

The application stores data in JSON format with the following structure:

```json
{
  "user_profile": {
    "name": "string",
    "current_role": "string",
    "profile_summary": "string",
    "attachments": ["file1.pdf"],
    "urls": ["https://example.com"]
  },
  "technical_skills": {
    "category": ["skill1", "skill2"]
  },
  "projects": [{
    "domain": "string",
    "role": "string", 
    "description": "string",
    "responsibilities": "string",
    "related_skills": ["skill1"],
    "tags": ["tag1"]
  }],
  "other_activities": [{
    "title": "string",
    "description": "string", 
    "related_skills": ["skill1"],
    "attachments": ["file1.pdf"],
    "urls": ["https://example.com"],
    "tags": ["tag1"]
  }]
}
```

## Troubleshooting

### Common Issues

1. **LLM Connection Failed**:
   - Ensure local LLM server is running on `localhost:1234`
   - Check firewall settings
   - Verify model is loaded in LM Studio

2. **Docker Connection Issues**:
   - Use `host.docker.internal:1234` instead of `localhost:1234` in Docker
   - Ensure Docker Desktop is running

3. **File Upload Issues**:
   - Check directory permissions
   - Ensure `data/attachments` directories exist

4. **Slow Performance**:
   - Increase `LLM_TIMEOUT` in `.env`
   - Reduce `CHUNK_SIZE` for faster indexing
   - Lower `TOP_K` for faster retrieval

## License

This project is for personal use and learning purposes.
