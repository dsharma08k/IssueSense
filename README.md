# IssueSense 🐛

**ML-Powered Error Knowledge Base**

IssueSense helps developers avoid re-debugging the same programming errors by capturing error context, using semantic search to find similar past issues, and linking verified solutions.

---

## 🌟 Features

- **📝 Error Capture**: Store programming errors with rich context (stack traces, environment, tags)
- **🔍 Semantic Search**: Find similar issues using ML embeddings (sentence-transformers)
- **💡 Solution Management**: Link solutions to issues with effectiveness tracking
- **📊 Analytics Dashboard**: Visualize error patterns, trends, and resolution rates
- **🔒 Multi-user Support**: Supabase authentication with Row Level Security
- **🎨 Minimal UI**: Clean, modern interface with background animations

---

## 🏗️ Architecture

```
IssueSense/
├── backend/          # FastAPI server
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # Business logic
│   │   └── utils/    # Utilities
│   └── requirements.txt
│
├── frontend/         # Streamlit UI
│   ├── pages/        # App pages
│   ├── .streamlit/   # Config
│   ├── app.py        # Main app
│   └── requirements.txt
│
└── database/         # SQL schema
    └── schema.sql
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Supabase account (for database + auth)
- Gemini API key (optional, for AI suggestions)

### 1. Database Setup

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project
3. Go to SQL Editor
4. Run the schema from `database/schema.sql`

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy from project root .env)
# Edit with your Supabase credentials

# Run server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies (use same venv or create new one)
pip install -r requirements.txt

# Configure environment
echo "API_URL=http://localhost:8000" > .env
echo "SUPABASE_URL=your_supabase_url" >> .env
echo "SUPABASE_ANON_KEY=your_anon_key" >> .env

# Run Streamlit
streamlit run app.py
```

Frontend will be available at: http://localhost:8501

---

## 📖 Usage

### Create an Account

1. Open frontend in browser
2. Click "Sign Up" tab
3. Enter email and password
4. Verify email (check inbox)
5. Sign in

### Capture an Error

1. Navigate to **📝 Issues** → **Create New**
2. Fill in error details:
   - Error Type (e.g., TypeError)
   - Error Message
   - Stack Trace (optional)
   - Language, Framework, Tags
3. Click **Create Issue**
4. System automatically:
   - Generates ML embedding
   - Finds similar past issues
   - Suggests related solutions

### Search for Similar Errors

1. Navigate to **🔍 Search**
2. Enter natural language query (e.g., "cannot read property undefined")
3. Adjust similarity threshold (0.7 = 70% similar)
4. View ranked results with similarity scores

### Add Solutions

1. Open an issue
2. Click **Add Solution**
3. Provide:
   - Title
   - Description
   - Code fix
   - Step-by-step instructions
4. Other users can provide feedback (helpful/not helpful)
5. Effectiveness score auto-calculates

### View Analytics

Navigate to **📊 Analytics** to see:
- Error trends over time
- Severity distribution
- Language breakdown
- Top error types
- Resolution rate

---

## 🔧 Configuration

### Environment Variables

#### Backend (`.env` in project root)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# ML Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_CACHE_DIR=./model_cache

# LLM (Optional)
GEMINI_API_KEY=your_gemini_key

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:8501

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

#### Frontend (`frontend/.env`)

```env
API_URL=http://localhost:8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

---

## 🧠 How It Works

### ML Pipeline

1. **Embedding Generation**:
   - Combines error_type + error_message + stack_trace + tags
   - Uses sentence-transformers (MiniLM-L6-v2)
   - Produces 384-dimensional vector

2. **Similarity Search**:
   - Uses pgvector cosine distance
   - Returns issues above threshold (default 0.7)
   - Ranked by similarity score

3. **Deduplication** (future):
   - High similarity (>0.9) flags potential duplicates
   - Increments occurrence count

### Security

- **Authentication**: Supabase Auth with JWT tokens
- **RLS Policies**: Row-level security ensures users only see their own data
- **Input Validation**: Pydantic models validate all API inputs
- **Rate Limiting**: Prevent API abuse (60 requests/minute)

---

## 📊 Database Schema

Key tables:
- `issues`: Error records with embeddings
- `solutions`: Linked solutions with effectiveness scores
- `solution_feedback`: User feedback on solutions
- `teams`: Team workspaces (future)
- `team_members`: Team membership (future)

See `database/schema.sql` for complete schema.

---

## 🛠️ Development



### API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI

### Code Structure

- **Backend**:
  - `services/`: Business logic (IssueService, MLService, etc.)
  - `api/v1/`: API routes
  - `models/`: Pydantic schemas
  - `utils/`: Helper functions

- **Frontend**:
  - `app.py`: Main entry + auth
  - `pages/`: Streamlit pages
  - `api_client.py`: Backend API wrapper

---

## 🚢 Deployment

### Recommended Stack

- **Frontend**: Streamlit Cloud / Heroku
- **Backend**: Railway / Render / Fly.io
- **Database**: Supabase (managed PostgreSQL + pgvector)

### Docker Deployment

For production deployment using Docker, use the production compose file:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Environment Variables

Make sure to set all environment variables in your deployment platform or `.env` file.

---

## 🔮 Roadmap

### Phase 2 features
- [ ] LLM-powered solution suggestions
- [ ] Automatic error deduplication
- [ ] Stack trace parsing for file/line extraction
- [ ] Team workspaces
- [ ] GitHub Issues integration

### Phase 3 features
- [ ] Browser extension for error capture
- [ ] IDE plugins (VSCode, IntelliJ)
- [ ] Slack notifications
- [ ] Advanced analytics

---

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 💬 Support

For issues or questions:
- Create an issue on GitHub

---

**Built with ❤️ using FastAPI, Streamlit, Supabase, and sentence-transformers**
