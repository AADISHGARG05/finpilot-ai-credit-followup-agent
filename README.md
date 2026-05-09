# ⚡ FinPilot AI — Credit Follow-Up Email Agent

> Enterprise AI-powered receivables automation platform using Groq LLMs, Streamlit, and SQLite for intelligent invoice escalation, payment reminder generation, audit logging, and financial analytics.

---

# 📌 Overview

FinPilot AI is an end-to-end AI-powered finance automation platform designed to streamline invoice follow-ups and collections workflows.

The system intelligently:
- processes overdue invoices
- classifies escalation stages
- generates professional AI-driven payment reminder emails
- maintains audit logs
- visualizes collection analytics through an enterprise-grade dashboard

This project simulates a real-world accounts receivable automation system used in fintech and enterprise finance operations.

---

# 🚀 Key Features

## ✅ AI-Powered Email Generation
- Uses **Groq-hosted Llama 3.3 70B**
- Generates personalized payment reminder emails
- Escalation-aware tone adaptation
- Professional business communication

---

## ✅ Intelligent Escalation Engine

Automatically classifies invoices into escalation stages:

| Days Overdue | Stage | Tone |
|---|---|---|
| 1–7 | Stage 1 | Warm & Friendly |
| 8–14 | Stage 2 | Polite but Firm |
| 15–21 | Stage 3 | Formal & Serious |
| 22–30 | Stage 4 | Stern & Urgent |
| 30+ | Escalation | Legal Review |

---

## ✅ Enterprise Dashboard
Built using Streamlit with:
- Dark fintech-style UI
- Interactive analytics
- CSV upload pipeline
- Live invoice processing
- AI email preview
- Audit log viewer
- Dynamic charts

---

## ✅ SQLite Audit Logging
Maintains:
- generated email history
- escalation logs
- timestamps
- invoice tracking
- compliance-style audit records

---

## ✅ Real-Time Analytics
Interactive analytics powered by Plotly:
- escalation distribution
- overdue trends
- outstanding amounts
- tone distribution
- receivables overview

---

# 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │   Invoice CSV    │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ Invoice Processor    │
                 │ • Overdue Detection  │
                 │ • Stage Assignment   │
                 │ • Tone Mapping       │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │ Groq LLM Engine      │
                 │ Llama 3.3 70B        │
                 │ AI Email Generation  │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │ SQLite Audit DB      │
                 │ Email Logging        │
                 │ Compliance Tracking  │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │ Streamlit Dashboard  │
                 │ Analytics + UI       │
                 └──────────────────────┘
```

---

# 🛠️ Tech Stack

## Frontend
- Streamlit

## Backend
- Python

## AI / LLM
- Groq API
- Llama 3.3 70B Versatile

## Database
- SQLite

## Visualization
- Plotly

## Core Libraries
- Pandas
- LangChain
- Pydantic
- SQLAlchemy

---

# 📂 Project Structure

```text
finance-email-agent/
│
├── app/
│   ├── agents/
│   │   └── prompt_templates.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── security.py
│   │
│   ├── database/
│   │   └── db.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── invoice_processor.py
│   │   └── llm_service.py
│   │
│   └── ui/
│       └── dashboard.py
│
├── data/
│   └── invoices.csv
│
├── screenshots/
│
├── requirements.txt
├── run.py
├── .env.example
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/finpilot-ai-credit-followup-agent.git

cd finpilot-ai-credit-followup-agent
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

---

# ▶️ Running the Project

## Run Backend Pipeline

```bash
python run.py
```

---

## Run Streamlit Dashboard

```bash
streamlit run app/ui/dashboard.py
```

---

# 📊 Dashboard Features

## Upload & Process CSV
- drag-and-drop CSV upload
- invoice validation
- automatic processing

---

## AI Email Generation
- one-click AI email creation
- escalation-aware communication
- professional formatting

---

## Analytics Dashboard
- stage distribution
- overdue analysis
- outstanding balance overview
- tone analytics

---

## Audit Logging
- SQLite-backed logs
- generated email history
- compliance tracking

---

# 📧 Sample AI Email Output

## Stage 1 — Friendly Reminder

```text
Subject: Friendly Reminder — Invoice INV-1001 Pending

Dear Rajesh Kapoor,

We hope you're doing well.

This is a gentle reminder regarding Invoice INV-1001
for ₹45,000, which became due on May 5, 2026.

We would appreciate it if you could process the payment
at your earliest convenience.

Payment Link:
https://pay.company.com/inv1001

Warm regards,
FinPilot AI Finance Team
```

---

## Escalation Stage — Legal Review

```text
Subject: Urgent Payment Escalation Notice — INV-1005

Dear Vikram Singh,

This is a formal notification regarding the overdue
payment for Invoice INV-1005 amounting to ₹90,000.

The invoice has remained unpaid beyond the agreed
payment period and now requires immediate attention.

Failure to resolve the outstanding amount may result
in further escalation procedures.

Payment Link:
https://pay.company.com/inv1005

Regards,
FinPilot AI Finance Team
```

---

# 🔒 Security & Reliability

Implemented safeguards include:
- input sanitization
- structured JSON validation
- defensive rendering
- SQLite persistence
- exception handling
- thread-safe database access

---

# 📈 Future Improvements

Potential future enhancements:
- SMTP email delivery
- multi-user authentication
- PostgreSQL migration
- Docker deployment
- cloud hosting
- payment API integration
- LangGraph orchestration
- autonomous finance agents

---

# 🎯 Learning Outcomes

This project demonstrates:
- LLM integration
- prompt engineering
- AI workflow orchestration
- enterprise dashboard design
- backend/frontend integration
- database logging systems
- production-style architecture

---

# 👨‍💻 Author

## Aadish Garg

AI / ML Engineer | Data Science Enthusiast

- LinkedIn: https://www.linkedin.com/in/aadish-garg-ab2a59288/
- GitHub: https://github.com/AADISHGARG05

---

# ⭐ Acknowledgements

- Groq
- Streamlit
- LangChain
- Plotly
- Open-source AI community

---

# 📜 License

This project is intended for educational, internship, and portfolio purposes.
