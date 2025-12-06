# 🚀 Agentic HR Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**A comprehensive AI-powered Human Resource Management System with automated candidate evaluation, interview scheduling, document management, and GDPR compliance.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Demo Guide](#-demo-guide) • [API Reference](#-api-reference)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Demo Guide](#-demo-guide)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Security & Compliance](#-security--compliance)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 Overview

The **Agentic HR Assistant** is a modern, full-stack HR management application designed to streamline the entire recruitment pipeline. From job posting to candidate onboarding, this system automates repetitive tasks while maintaining human oversight for critical decisions.

### Key Highlights

- 🤖 **AI-Powered Evaluation**: Automated resume parsing and candidate scoring
- 📅 **Smart Scheduling**: Interview slot management with panel assignment
- 📄 **Document Management**: Secure upload, verification, and storage of candidate documents
- 🔒 **GDPR Compliant**: Built-in data protection and consent management
- 📊 **Real-time Dashboard**: Interactive analytics and metrics visualization
- 🎨 **Modern UI**: Responsive design with Tailwind CSS

---

## ✨ Features

### 1. Job Management
- Create, edit, and manage job postings
- Define job requirements, skills, and qualifications
- Set salary ranges and job locations
- Track job status (draft, active, closed)

### 2. Candidate Management
- Add and manage candidate profiles
- Store contact information, skills, and experience
- Track candidate status through hiring pipeline
- View candidate history and interactions

### 3. Application Tracking
- Link candidates to job applications
- AI-powered resume scoring against job requirements
- Application status workflow (new → screening → interview → offer → hired)
- Notes and feedback tracking

### 4. Interview Panel Management
- Create interview panels with multiple members
- Define panel expertise and interview focus areas
- Assign panels to specific job roles
- Track panel availability and workload

### 5. Interview Scheduling
- Create and manage interview time slots
- Schedule interviews with automatic panel assignment
- Support for multiple interview rounds
- Calendar integration ready

### 6. Document Management
- **Multi-document upload** for candidates:
  - Resume/CV
  - Identity Proof (Passport, Aadhar, etc.)
  - Education Certificates & Marksheets
  - Experience Letters & Relieving Letters
  - Salary Slips & Offer Letters
  - Certifications & Portfolios
- Document verification workflow
- Access level controls (HR Only, Panel View, All Interviewers)
- Secure file storage with integrity verification

### 7. Real-time Dashboard
- Active jobs, candidates, and applications count
- Interview pipeline visualization
- Recent activity feed
- Quick action buttons

---

## 🛠 Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core programming language |
| **FastAPI** | High-performance async web framework |
| **Uvicorn** | ASGI server for running FastAPI |
| **SQLAlchemy 2.0** | ORM for database operations |
| **Pydantic** | Data validation and settings management |
| **Alembic** | Database migrations |

### Database

| Technology | Purpose |
|------------|---------|
| **SQLite** | Default lightweight database (for development/demo) |
| **PostgreSQL** | Production database option |
| **asyncpg** | Async PostgreSQL driver |

### Authentication & Security

| Technology | Purpose |
|------------|---------|
| **python-jose** | JWT token generation and validation |
| **passlib** | Password hashing with bcrypt |
| **cryptography** | Data encryption for GDPR compliance |

### File Handling

| Technology | Purpose |
|------------|---------|
| **aiofiles** | Async file operations |
| **PyPDF2** | PDF parsing for resumes |
| **python-docx** | Word document parsing |
| **python-multipart** | File upload handling |

### Frontend

| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure |
| **Tailwind CSS** | Utility-first styling |
| **JavaScript (ES6+)** | Interactive functionality |
| **Font Awesome** | Icons |
| **Chart.js** | Analytics visualizations |

### AI/ML (Optional)

| Technology | Purpose |
|------------|---------|
| **Anthropic Claude API** | Resume analysis and scoring |
| **Ollama** | Local LLM alternative |
| **Transformers** | Local NLP models |

### Development Tools

| Technology | Purpose |
|------------|---------|
| **pytest** | Unit and integration testing |
| **black** | Code formatting |
| **isort** | Import sorting |
| **flake8** | Code linting |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Dashboard  │  │  Login Page │  │  API Clients│              │
│  │  (HTML/JS)  │  │  (HTML/JS)  │  │  (External) │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    REST API Endpoints                    │    │
│  │  /api/v1/demo/candidates  │  /api/v1/demo/jobs          │    │
│  │  /api/v1/demo/applications│  /api/v1/demo/panels        │    │
│  │  /api/v1/demo/interviews  │  /api/v1/demo/documents     │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Middleware                            │    │
│  │  CORS │ Request Logging │ Authentication │ Rate Limiting│    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │ DocumentService│  │ ClaudeService │  │ GDPRService   │        │
│  │ - Upload      │  │ - AI Scoring  │  │ - Encryption  │        │
│  │ - Download    │  │ - Resume Parse│  │ - Consent     │        │
│  │ - Verify      │  │ - Questions   │  │ - Audit Log   │        │
│  └───────────────┘  └───────────────┘  └───────────────┘        │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │   SQLAlchemy  │  │  File Storage │  │  Session      │        │
│  │   ORM Models  │  │  ./uploads/   │  │  Management   │        │
│  └───────┬───────┘  └───────────────┘  └───────────────┘        │
│          │                                                       │
│          ▼                                                       │
│  ┌───────────────────────────────────────────────────┐          │
│  │              SQLite / PostgreSQL                   │          │
│  │  Tables: candidates, jobs, applications,          │          │
│  │          interview_panels, interview_slots,       │          │
│  │          interviews, candidate_documents          │          │
│  └───────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **pip** (comes with Python)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agentic-hr-assistant.git
cd agentic-hr-assistant
```

#### 2. Create Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for demo)
```

#### 5. Create Required Directories

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Path "./uploads" -Force
New-Item -ItemType Directory -Path "./storage" -Force
```

**macOS/Linux:**
```bash
mkdir -p uploads storage
```

#### 6. Initialize Database (Optional - Auto-creates on first run)

```bash
python init_db.py
```

---

## ⚙ Configuration

### Environment Variables (.env)

```env
# Application Settings
APP_NAME=HR Assistant
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Database (SQLite for demo)
DATABASE_URL=sqlite+aiosqlite:///./hr_assistant.db

# For PostgreSQL (production):
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hr_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=15728640  # 15MB
UPLOAD_DIR=./uploads

# AI Service (Optional)
ANTHROPIC_API_KEY=your-api-key-here

# CORS
ALLOWED_ORIGINS=["http://localhost:8000", "http://127.0.0.1:8000"]
```

---

## 🚀 Running the Application

### Development Mode

**Windows (PowerShell):**
```powershell
cd "c:\path\to\agentic-hr-assistant"
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

**With Auto-reload:**
```powershell
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

**macOS/Linux:**
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Access the Application

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/dashboard | Main HR Dashboard |
| http://127.0.0.1:8000/login | Login Page |
| http://127.0.0.1:8000/docs | API Documentation (Swagger UI) |
| http://127.0.0.1:8000/redoc | API Documentation (ReDoc) |

---

## 🎬 Demo Guide

### For Presenters: Step-by-Step Demo Script

#### Pre-Demo Setup (5 minutes before)

1. **Start the Server:**
   ```powershell
   cd "c:\Users\LENOVO\OneDrive\Documents\Python\Agentic HR Assistant"
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
   ```

2. **Verify Server is Running:**
   - Open browser to: http://127.0.0.1:8000/dashboard
   - You should see the HR Dashboard with stats cards

3. **Check Database:**
   - Ensure `hr_assistant.db` exists in the project folder
   - Tables will auto-create on first run

---

### Demo Flow (Recommended Order)

#### 1. Dashboard Overview (2 min)
- Show the main dashboard with statistics
- Highlight: Active Jobs, Total Candidates, Active Panels, Pending Applications
- Point out the modern UI design

#### 2. Job Management (3 min)
- Click **"Manage Jobs"** card
- Click **"+ Add Job"** button
- Create a sample job:
  ```
  Title: Senior Python Developer
  Department: Engineering
  Location: Bangalore, India
  Employment Type: Full-time
  Experience: 3-5 years
  Salary: ₹15,00,000 - ₹25,00,000
  Description: Looking for experienced Python developer...
  Requirements: Python, FastAPI, PostgreSQL, Docker
  ```
- Show the job appears in the list
- Demonstrate **View** and **Edit** functionality

#### 3. Candidate Management (3 min)
- Click **"Manage Candidates"** card
- Click **"+ Add Candidate"** button
- Create a sample candidate:
  ```
  Name: John Doe
  Email: john.doe@example.com
  Phone: +91 98765 43210
  Skills: Python, FastAPI, React, PostgreSQL
  Experience: 4 years
  Education: B.Tech Computer Science
  ```
- Show the candidate card with action buttons

#### 4. Document Upload Feature (5 min) ⭐
- Click **"Documents"** button on a candidate card
- Show the **"Upload Document"** button (green)
- Upload multiple documents:
  
  **Document 1 - Resume:**
  ```
  Type: Resume/CV
  Title: John Doe Resume 2024
  File: [Select a PDF]
  Access: All Interviewers
  ```
  
  **Document 2 - Identity Proof:**
  ```
  Type: Identity Proof
  Subtype: Passport
  Title: Passport Copy
  Document Number: A1234567
  Issuing Authority: Govt. of India
  ```
  
  **Document 3 - Education:**
  ```
  Type: Education Certificate
  Title: B.Tech Degree
  Institution: IIT Delhi
  Year: 2020
  Grade: 8.5 CGPA
  ```

- Show document filters (by type, by status)
- Demonstrate document verification workflow

#### 5. Interview Panel Management (3 min)
- Click **"Interview Panels"** tab
- Click **"+ Create Panel"** button
- Create a panel:
  ```
  Name: Technical Interview Panel
  Type: Technical
  Members: John Smith (Lead), Jane Doe (Member)
  Expertise: Python, System Design, Algorithms
  ```

#### 6. Interview Scheduling (3 min)
- Click **"Interview Slots"** tab
- Click **"+ Add Slot"** button
- Create interview slots:
  ```
  Panel: Technical Interview Panel
  Date: [Tomorrow's date]
  Start: 10:00 AM
  End: 11:00 AM
  ```
- Show how to schedule an interview with a candidate

#### 7. Application Flow (2 min)
- Show how candidates are linked to jobs
- Demonstrate status change workflow
- Show AI scoring (if enabled)

---

### Key Talking Points

1. **Modern Architecture:**
   - "Built with FastAPI - one of the fastest Python frameworks"
   - "Async operations for high performance"
   - "Clean separation of concerns"

2. **Document Management:**
   - "Supports 17+ document types for complete candidate profiles"
   - "Access control ensures only authorized personnel view sensitive docs"
   - "Document verification workflow for compliance"

3. **Interview Management:**
   - "Complete interview lifecycle management"
   - "Panel-based interviews with expertise matching"
   - "Slot management prevents double-booking"

4. **Security & Compliance:**
   - "GDPR-ready with consent management"
   - "Secure file storage with integrity checks"
   - "Audit logging for all operations"

5. **Extensibility:**
   - "Easy to integrate AI services for resume scoring"
   - "API-first design for third-party integrations"
   - "Modular services architecture"

---

## 📚 API Reference

### Base URL
```
http://127.0.0.1:8000/api/v1/demo
```

### Endpoints

#### Candidates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/candidates` | List all candidates |
| POST | `/candidates` | Create new candidate |
| GET | `/candidates/{id}` | Get candidate details |
| PUT | `/candidates/{id}` | Update candidate |
| DELETE | `/candidates/{id}` | Delete candidate |

#### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all jobs |
| POST | `/jobs` | Create new job |
| GET | `/jobs/{id}` | Get job details |
| PUT | `/jobs/{id}` | Update job |
| DELETE | `/jobs/{id}` | Delete job |

#### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications` | List applications |
| POST | `/applications` | Create application |
| PUT | `/applications/{id}/status` | Update status |

#### Interview Panels
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/panels` | List all panels |
| POST | `/panels` | Create panel |
| GET | `/panels/{id}` | Get panel details |
| PUT | `/panels/{id}` | Update panel |

#### Interview Slots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/slots` | List slots |
| POST | `/slots` | Create slot |
| POST | `/slots/bulk` | Create bulk slots |

#### Interviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interviews` | List interviews |
| POST | `/interviews` | Schedule interview |
| PUT | `/interviews/{id}/feedback` | Submit feedback |

#### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/candidates/{id}/documents` | List candidate docs |
| POST | `/candidates/{id}/documents` | Upload document |
| GET | `/documents/{id}` | Get document details |
| GET | `/documents/{id}/download` | Download document |
| PUT | `/documents/{id}/verify` | Verify document |
| DELETE | `/documents/{id}` | Delete document |

### Full API Documentation

Visit http://127.0.0.1:8000/docs for interactive Swagger documentation.

---

## 🗄 Database Schema

### Core Tables

```sql
-- Candidates
candidates (
    id UUID PRIMARY KEY,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    skills TEXT,
    experience_years INTEGER,
    education TEXT,
    status VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Jobs
jobs (
    id UUID PRIMARY KEY,
    title VARCHAR,
    department VARCHAR,
    location VARCHAR,
    employment_type VARCHAR,
    experience_required VARCHAR,
    salary_range VARCHAR,
    description TEXT,
    requirements TEXT,
    status VARCHAR,
    created_at TIMESTAMP
)

-- Applications
applications (
    id UUID PRIMARY KEY,
    candidate_id UUID REFERENCES candidates,
    job_id UUID REFERENCES jobs,
    status VARCHAR,
    ai_score FLOAT,
    notes TEXT,
    created_at TIMESTAMP
)

-- Interview Panels
interview_panels (
    id UUID PRIMARY KEY,
    name VARCHAR,
    panel_type VARCHAR,
    members JSON,
    expertise TEXT,
    is_active BOOLEAN
)

-- Interview Slots
interview_slots (
    id UUID PRIMARY KEY,
    panel_id UUID REFERENCES interview_panels,
    date DATE,
    start_time TIME,
    end_time TIME,
    status VARCHAR
)

-- Interviews
interviews (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES applications,
    slot_id UUID REFERENCES interview_slots,
    panel_id UUID REFERENCES interview_panels,
    round_number INTEGER,
    status VARCHAR,
    feedback TEXT
)

-- Candidate Documents
candidate_documents (
    id UUID PRIMARY KEY,
    candidate_id UUID REFERENCES candidates,
    document_type VARCHAR,
    document_subtype VARCHAR,
    title VARCHAR,
    file_path VARCHAR,
    file_hash VARCHAR,
    verification_status VARCHAR,
    access_level VARCHAR,
    uploaded_at TIMESTAMP
)
```

---

## 🔒 Security & Compliance

### Authentication
- JWT-based token authentication
- Password hashing with bcrypt
- Session management

### Data Protection
- Field-level encryption for sensitive data
- Secure file storage with hash verification
- Access control on documents

### GDPR Compliance
- Consent management system
- Right to erasure (data deletion)
- Data export functionality
- Audit logging

### Best Practices
- Input validation with Pydantic
- SQL injection prevention via ORM
- CORS configuration
- Rate limiting ready

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Server Won't Start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill any existing Python processes
Get-Process python* | Stop-Process -Force
```

#### 2. Database Errors
```powershell
# Delete and recreate database
Remove-Item hr_assistant.db -Force
python init_db.py
```

#### 3. File Upload Fails
- Ensure `uploads` directory exists
- Check file size (max 15MB)
- Verify allowed file types

#### 4. Modal Display Issues
- Hard refresh: `Ctrl + Shift + R`
- Clear browser cache
- Check browser console for JS errors

#### 5. API Returns 500 Error
- Check server logs in terminal
- Verify database connection
- Check `.env` configuration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👏 Acknowledgements

- FastAPI framework by Sebastián Ramírez
- Tailwind CSS for styling
- Font Awesome for icons
- The open-source community

---

<div align="center">

**Built with ❤️ for modern HR teams**

[⬆ Back to Top](#-agentic-hr-assistant)

</div>