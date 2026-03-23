
# 🛡️ AVAS — AI-Powered Infrastructure Inspection Intelligence Platform

> Detect defects, score risk, and prioritize maintenance — automatically.  

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.99.0-green?style=for-the-badge&logo=fastapi)]()
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-3178C6?style=for-the-badge&logo=typescript)]()
[![Docker](https://img.shields.io/badge/Docker-24.0.2-2496ED?style=for-the-badge&logo=docker)]()
[![MIT License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()

---

## 🌟 Overview

**AVAS** is an enterprise-grade platform that leverages AI and computer vision to **automatically detect infrastructure defects, assess risk, and prioritize maintenance**.  

**Highlights**:  

- 🏗️ AI-powered defect detection (YOLOv8)  
- 📊 Rule-based and ML-enhanced risk scoring  
- 📈 Analytics dashboard & historical tracking  
- 🔐 Secure JWT-based authentication  
- 🚀 Fully containerized & production-ready  

---

## 🏛️ Architecture

```

┌─────────────────────────────────────────────────────────┐
│                      AVAS Platform                       │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Frontend    │   Backend    │  AI Service  │  Storage   │
│  React/Vite  │  FastAPI     │  YOLOv8 +    │  MinIO     │
│  Tailwind    │  PostgreSQL  │  Risk Model  │  (S3-compat│
│  Port :3000  │  Port :8000  │  Port :8001  │  Port :9000│
└──────────────┴──────────────┴──────────────┴────────────┘

````

**Stack:** React | TailwindCSS | TypeScript | FastAPI | PostgreSQL | YOLOv8 | MinIO | Docker  

---

## ⚡ Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/avas.git
cd avas

# Quickstart with auto-generated secrets
bash infrastructure/scripts/quickstart.sh

# Open in browser
open http://localhost:3000
````

---

## 📊 Key Features

| Feature                | Description                                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| 🖼️ Defect Detection   | YOLOv8 detects cracks, corrosion, spalling, delamination, erosion, broken/missing components, discoloration |
| ⚡ Risk Scoring         | Rule-based composite score (0–100) combining severity, type, confidence, and defect count                   |
| 🏗️ Asset Management   | Track infrastructure assets with inspection history & risk prioritization                                   |
| 📈 Dashboard Analytics | Visualize inspection results, risk trends, and top-risk assets                                              |
| 🔒 Security            | JWT authentication & role-based access control                                                              |
| 📦 Containerized       | Fully Dockerized with AI microservice and MinIO storage                                                     |

---

## 📋 API Endpoints

### Auth

| Method | Endpoint                | Description          |
| ------ | ----------------------- | -------------------- |
| POST   | `/api/v1/auth/register` | Register user        |
| POST   | `/api/v1/auth/login`    | Login (JWT tokens)   |
| POST   | `/api/v1/auth/refresh`  | Refresh access token |

### Inspections

| Method | Endpoint                           | Description            |
| ------ | ---------------------------------- | ---------------------- |
| POST   | `/api/v1/inspections`              | Create inspection      |
| POST   | `/api/v1/inspections/{id}/upload`  | Upload images          |
| POST   | `/api/v1/inspections/{id}/analyze` | Run AI analysis        |
| GET    | `/api/v1/inspections`              | List inspections       |
| GET    | `/api/v1/inspections/{id}`         | Get inspection details |

### Assets

| Method | Endpoint              | Description         |
| ------ | --------------------- | ------------------- |
| POST   | `/api/v1/assets`      | Create asset        |
| GET    | `/api/v1/assets`      | List assets by risk |
| GET    | `/api/v1/assets/{id}` | Get asset info      |
| DELETE | `/api/v1/assets/{id}` | Delete asset        |

### Analytics

| Method | Endpoint                         | Description        |
| ------ | -------------------------------- | ------------------ |
| GET    | `/api/v1/analytics/dashboard`    | Dashboard stats    |
| GET    | `/api/v1/analytics/risk-summary` | Asset risk ranking |

---

## 🤖 AI Models

### YOLOv8 Defect Detection

Detects **8 defect types**:
`crack`, `corrosion`, `erosion`, `delamination`, `spalling`, `broken_component`, `missing_component`, `discoloration`

> Fine-tune the default YOLOv8n model for production on your inspection dataset.

### Risk Scoring (0–100)

| Score  | Meaning   |
| ------ | --------- |
| 0–40   | ✅ GO      |
| 40–70  | ⚠️ REVIEW |
| 70–100 | 🚫 NO-GO  |

---

## ⚙️ Environment Variables

| Variable               | Description                             |
| ---------------------- | --------------------------------------- |
| `APP_SECRET_KEY`       | Application secret                      |
| `JWT_SECRET_KEY`       | JWT signing key                         |
| `DATABASE_URL`         | PostgreSQL connection                   |
| `REDIS_URL`            | Redis connection                        |
| `MINIO_ENDPOINT`       | Object storage endpoint                 |
| `AI_SERVICE_URL`       | AI microservice URL                     |
| `AI_INFERENCE_TIMEOUT` | Max AI inference seconds (default: 120) |

---

## 💻 Development

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm install
npm run dev

# Full stack
docker compose up --build
```

---

## 🚀 Production Checklist

* [ ] Replace YOLOv8n with fine-tuned defect model
* [ ] Set `.env` variables (`APP_ENV=production`, `APP_DEBUG=false`)
* [ ] Configure SSL in `infrastructure/nginx/ssl/`
* [ ] Enable GPU support if available
* [ ] Setup database backups (PostgreSQL)
* [ ] Configure S3-compatible storage

---

## 📄 License

MIT — Built by **AVAS Team**

<div align="center">
Built with ❤️ by **AVAS Team** | <a href="https://github.com/your-org/avas">GitHub Repository</a>
</div>
```


Do you want me to do that next?
