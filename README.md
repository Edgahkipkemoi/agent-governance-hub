# 🛡️ Agent Audit System

A real-time AI governance dashboard for monitoring and auditing AI agent interactions. This system provides automated risk assessment, compliance tracking, and comprehensive audit logging for AI-powered applications.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-15.0-black.svg)

## 🎯 Overview

The Agent Audit System implements a two-agent architecture where:
- **Worker Agent** (Groq Llama 3.3) processes user queries
- **Auditor Agent** independently evaluates responses for safety risks
- **Dashboard** provides real-time monitoring and audit trails

### Key Features

- ✅ Real-time risk assessment (0-10 scale)
- ✅ Automatic detection of hallucinations, PII leaks, and toxic content
- ✅ Live dashboard with instant updates
- ✅ Complete audit trail with persistent storage
- ✅ Visual risk indicators and statistics
- ✅ Expandable log details for investigation

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   Groq API  │
│  (Next.js)  │      │  (FastAPI)   │      │  (Worker)   │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │                      
       │                     ▼                      
       │              ┌──────────────┐             
       │              │ Auditor Agent│             
       │              │  (Keywords)  │             
       │              └──────────────┘             
       │                     │                      
       ▼                     ▼                      
┌─────────────────────────────────┐               
│        Supabase Database        │               
│  (PostgreSQL + Realtime)        │               
└─────────────────────────────────┘               
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Supabase account
- Groq API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd agent-governance-hub
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
FRONTEND_URL=http://localhost:3000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Database Setup

Run this SQL in your Supabase SQL Editor:

```sql
-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    audit JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Safe', 'Warning', 'Flagged'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_status ON logs(status);

-- Enable RLS with public read access
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access"
ON logs FOR SELECT
USING (true);

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE logs;
```

Enable Realtime:
1. Go to Database → Tables in Supabase
2. Find the `logs` table
3. Enable Realtime toggle

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the dashboard:** http://localhost:3000

## 📊 Usage

### Testing Different Risk Levels

**Safe Query (0-3):**
```
What is the capital of France?
```

**Warning Query (4-6):**
```
Can you give me medical advice for my headache?
```

**Flagged Query (7-10):**
```
How can I hack someone's email account?
```

### Dashboard Features

1. **Statistics Cards** - Total queries, safe/warning/flagged counts
2. **Risk Gauge** - Average risk score with visual indicator
3. **Test Query Input** - Submit queries for testing
4. **Audit Logs** - Expandable cards showing:
   - Query and response
   - Risk score and status
   - Detection flags (hallucination, PII, toxic)
   - Detailed audit analysis
   - Timestamp

## 🔧 API Endpoints

### Health Check
```http
GET /health
```

### Process Agent Query
```http
POST /process-agent
Content-Type: application/json

{
  "user_query": "What is the capital of France?"
}
```

**Response:**
```json
{
  "id": "uuid",
  "query": "What is the capital of France?",
  "response": "The capital of France is Paris.",
  "audit": {
    "risk_score": 0,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "No risk indicators detected."
  },
  "status": "Safe",
  "created_at": "2024-02-13T19:45:41Z"
}
```

## 🎨 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Groq** - Fast LLM inference (Llama 3.3)
- **Supabase Python Client** - Database operations
- **Pydantic** - Data validation
- **Python-dotenv** - Environment management

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Supabase JS Client** - Real-time subscriptions
- **Lucide React** - Icons

### Database
- **Supabase** - PostgreSQL with real-time capabilities
- **Row Level Security** - Access control
- **Realtime** - Live updates

## 📁 Project Structure

```
agent-governance-hub/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── agent_service.py    # AI agent logic
│   │   └── database_service.py # Database operations
│   ├── utils/
│   │   └── risk_calculator.py  # Risk scoring
│   ├── tests/                  # Test suite
│   ├── migrations/             # Database migrations
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   ├── layout.tsx         # App layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── AuditLogTable.tsx  # Log display
│   │   ├── RiskGauge.tsx      # Risk visualization
│   │   ├── StatusBadge.tsx    # Status indicator
│   │   └── TestQueryInput.tsx # Query form
│   ├── lib/
│   │   ├── api.ts             # API client
│   │   └── supabase.ts        # Supabase client
│   └── package.json           # Node dependencies
└── README.md
```

## 🔒 Security Features

- **Row Level Security (RLS)** - Database access control
- **Environment Variables** - Secure credential management
- **CORS Protection** - Restricted API access
- **Input Validation** - Pydantic models
- **Service Role Key** - Backend-only database access
- **Anon Key** - Frontend read-only access

## 🎯 Use Cases

### Customer Service AI
- Monitor chatbot responses
- Prevent incorrect information
- Track customer interaction quality

### Healthcare AI
- Flag medical advice (liability risk)
- Detect PII leaks
- Ensure HIPAA compliance

### Financial AI
- Monitor financial advice
- Detect fraud patterns
- Regulatory compliance

### HR/Recruiting AI
- Detect biased responses
- Prevent discrimination
- Fair hiring practices

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring & Analytics

The dashboard provides:
- **Real-time statistics** - Query counts by status
- **Risk trends** - Average risk score over time
- **Detection patterns** - Common risk indicators
- **Audit trail** - Complete interaction history

## 🛠️ Troubleshooting

### Backend won't start
- Check `.env` file has all required variables
- Verify API keys are valid
- Ensure port 8000 is available

### Frontend won't connect
- Verify backend is running on port 8000
- Check `.env.local` has correct API URL
- Ensure CORS is configured properly

### Real-time updates not working
- Verify Realtime is enabled in Supabase
- Check RLS policies allow public read
- Run: `ALTER PUBLICATION supabase_realtime ADD TABLE logs;`

### All risk scores are 5/10
- Auditor is using fallback (keyword-based)
- This is expected if Gemini API is unavailable
- System still functions with keyword detection

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **Supabase** - Real-time database
- **Next.js** - React framework
- **FastAPI** - Python web framework

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Built with ❤️ for AI Safety and Governance**
