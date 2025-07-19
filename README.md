# 🤖 Automated Property Research Assistant

Een volledig geautomatiseerd systeem dat nieuwe properties detecteert, marktdata verzamelt, AI-analyse uitvoert en professionele rapporten genereert.

## 🚀 Features

- **Automatische Property Detectie** - Monitor Google Sheets voor nieuwe entries
- **Multi-Source Data Collection** - CBS, demografische data, vergelijkbare verkopen
- **AI-Powered Analysis** - OpenAI integration voor marktinzichten
- **Automated Reporting** - Professionele rapporten met actionable insights
- **Multi-Channel Distribution** - Email, Slack, en Sheet updates

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python
- **Automation**: Make.com (visual workflow automation)
- **AI**: OpenAI GPT-4 API
- **Database**: Google Sheets
- **Deployment**: Render.com / Google Cloud Run
- **Monitoring**: Streamlit Dashboard

## 📁 Project Structure

```
property-research-assistant/
├── api/                    # FastAPI backend
├── dashboard/             # Streamlit analytics dashboard
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```