# 📚 Document Q&A System

An intelligent document processing and question-answering system powered by Google Gemini AI. Upload documents and ask questions to get instant, context-aware answers.

## 🚀 Quick Start

### **Option 1: Docker (Recommended for Production)**

```bash
# Using Docker Compose
./scripts/docker-compose-up.sh

# Or manually
docker-compose up -d
```

### **Option 2: Automated Setup & Run**

```bash
./scripts/run.sh
```

This script will:

- Create virtual environment
- Install dependencies
- Check configuration
- Run the web interface

### **Option 3: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with your Gemini API key

# Run the system
python main.py
```

## 🌐 Web Interface

Once running, open your browser to: **http://localhost:8501**

### **Main Features:**

- 📄 **Upload Documents**: PDF, TXT, DOCX (max 10MB)
- 🤖 **AI Processing**: Automatic analysis with Gemini
- 💬 **Q&A Interface**: Ask questions about your documents
- 📚 **Document Management**: View and manage processed documents
- 🔧 **System Status**: Monitor system health and performance

## ⚙️ Configuration

### **Required: Gemini API Key**

1. Get your API key from: https://makersuite.google.com/app/apikey
2. Add it to your `.env` file:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### **Optional Settings** (in `.env`):

```env
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,txt,docx
DATABASE_PATH=data/database/documents.db
STREAMLIT_PORT=8501
DEBUG_MODE=false
```

## 🎯 How to Use

### **1. Upload a Document**

- Go to "Upload Documents" section
- Drag & drop your file or browse to select
- Watch the AI processing (7-15 seconds)
- Get immediate Q&A access

### **2. Ask Questions**

- Click "Ask Questions Now" after upload
- Or go to "Q&A Interface" and select your document
- Type questions like:
  - "What is this document about?"
  - "What are the key points?"
  - "What actions need to be taken?"

### **3. Manage Documents**

- View all documents in "Document Management"
- See processing status and analysis results
- Delete documents you no longer need

## 🔧 Command Line Options

```bash
# Start web interface (default)
python main.py
python main.py --web

# Run system health check
python main.py --check

# Initialize system only
python main.py --init

# Run tests
python -m pytest tests/ -v
```

## 🧹 Cleanup

### **Clean Everything:**

```bash
./scripts/cleanup.sh
```

This will:

- Remove all databases and documents
- Clear logs and cache files
- Remove test files
- Deactivate virtual environment
- Optionally remove venv directory

### **Scripts Documentation:**

For detailed information about all available scripts, see: [`scripts/SCRIPTS_README.md`](scripts/SCRIPTS_README.md)

### **Manual Cleanup:**

```bash
# Remove data
rm -rf data/ logs/

# Remove Python cache
find . -name "__pycache__" -exec rm -rf {} +

# Deactivate venv
deactivate
```

## 📁 Project Structure

```
document-qa-system/
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── storage/         # Database operations
│   ├── ui/              # Streamlit interface
│   ├── utils/           # Utilities and error handling
│   └── workflow/        # Processing workflows
├── tests/               # Unit tests
├── data/                # Runtime data (created automatically)
│   ├── database/        # SQLite database
│   └── documents/       # Uploaded documents
├── logs/                # Application logs
├── scripts/             # Shell scripts for automation
│   ├── run.sh           # Complete setup and run script
│   ├── start.sh         # Quick start script
│   ├── cleanup.sh       # Cleanup script
│   ├── docker-build.sh  # Docker build script
│   ├── docker-run.sh    # Docker run script
│   ├── docker-compose-up.sh # Docker Compose script
│   └── SCRIPTS_README.md # Scripts documentation
├── Dockerfile           # Docker container definition
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker build ignore file
├── DOCKER_README.md     # Docker deployment guide
├── .env                 # Environment configuration
├── requirements.txt     # Python dependencies
└── main.py              # Main entry point
```

## 🛡️ Error Handling & Reliability

### **API Rate Limiting**

- **Smart retry logic** with exponential backoff
- **Graceful fallbacks** when API is overloaded
- **Single API call** processing to reduce rate limit hits

### **Processing Modes**

- **✅ Full Processing**: All AI features work
- **⚠️ Partial Processing**: Some AI features fail, Q&A still works
- **ℹ️ Basic Processing**: AI unavailable, document Q&A still functional

### **Error Recovery**

- Documents always stored for Q&A (even if AI fails)
- Clear error messages with suggested actions
- Automatic retries for temporary failures

## 🧪 Testing

### **Run All Tests:**

```bash
python -m pytest tests/ -v
```

### **Test Specific Components:**

```bash
# Test file handling
python -m pytest tests/test_file_handler.py -v

# Test Q&A engine
python -m pytest tests/test_qa_engine.py -v

# Test error handling
python -m pytest tests/test_error_handling.py -v
```

## 📊 Performance

### **Processing Time:**

- **Text Extraction**: 1-2 seconds
- **AI Processing**: 7-15 seconds (single API call)
- **Fallback Mode**: Instant

### **API Usage (Free Tier Friendly):**

- **1 API call per document** (optimized for rate limits)
- **Automatic retry** with respectful delays
- **Fallback processing** when API unavailable

### **Storage:**

- **SQLite database** for metadata and results
- **Local file storage** for document content
- **Efficient querying** for Q&A operations

## 🔍 Troubleshooting

### **Common Issues:**

**"API key not configured"**

- Edit `.env` file with your Gemini API key
- Get key from: https://makersuite.google.com/app/apikey

**"429 Too Many Requests"**

- System automatically retries with delays
- Uses fallback processing if needed
- Consider upgrading to paid API tier for higher limits

**"Document not appearing in Q&A"**

- Check "Document Management" for processing status
- Wait for processing to complete
- Refresh the page if needed

**"Processing failed"**

- Check internet connection
- Verify API key is valid
- Check system logs in debug mode

### **Debug Mode:**

```bash
# Enable debug mode
export DEBUG_MODE=true
python main.py
```

## 🎉 Features

### **✅ Current Features:**

- File upload with validation (PDF, TXT, DOCX)
- Intelligent text extraction
- AI-powered document analysis
- Context-aware question answering
- Document management and organization
- Real-time processing status
- Comprehensive error handling
- System health monitoring
- Conversation history
- Source attribution for answers

### **🔧 Technical Features:**

- Streamlit web interface
- Google Gemini AI integration
- SQLite database storage
- Comprehensive logging
- Unit test coverage (70+ tests)
- Error recovery and fallbacks
- Rate limit handling
- Modular architecture

## 📝 License

This project is for educational and personal use.

## 🤝 Support

For issues or questions:

1. Check the troubleshooting section above
2. Run system health check: `python main.py --check`
3. Enable debug mode for detailed error information
4. Check application logs in the `logs/` directory

---

## 🎯 Quick Commands Reference

### **Docker Deployment:**

```bash
# Docker Compose (recommended)
./scripts/docker-compose-up.sh

# Docker build and run
./scripts/docker-build.sh
./scripts/docker-run.sh

# Manual Docker
docker-compose up -d
```

### **Local Development:**

```bash
# Setup and run (recommended)
./scripts/run.sh

# Quick start (if already set up)
./scripts/start.sh

# Manual run
python main.py

# System check
python main.py --check

# Clean everything
./scripts/cleanup.sh

# Run tests
python -m pytest tests/ -v
```

### **Docker Documentation:**

For detailed Docker deployment guide, see: [`DOCKER_README.md`](DOCKER_README.md)

**Ready to upload and ask questions about your documents!** 🚀📚💬
