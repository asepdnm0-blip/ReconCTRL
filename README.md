# ReconCTRL Monorepo

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-Educational-red)

>  **Agentic reconnaissance platform** — scan target, stream hasil real-time, export laporan PDF.

---

## Project Structure

```
reconctrl/
├── frontend/                     # React 18 + Vite + TailwindCSS
├── backend/                      # FastAPI + Python 3.11 + Poetry
├── worker/                       # Celery worker (shares backend codebase)
├── docker/                       # Dockerfiles per service
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── worker.Dockerfile
├── docker-compose.yml            # Docker orchestration
├── .env.example                  # Template environment variables
└── README.md                     # Monorepo documentation
```
# ReconCTRL

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-Educational-red)

## Screenshot

<!-- Ganti dengan screenshot dashboard kamu -->
![ReconCTRL Dashboard](docs/screenshot.png)

---

## Fitur

- **7 Recon Modules** — Port Scan (nmap + NVD CVE), HTTP Headers, Subdomain Enum, OSINT, Directory Enum, OWASP Checks, AI Summary
- **Real-time Streaming** — hasil scan muncul live via Server-Sent Events (SSE)
- **Export** — download laporan sebagai JSON atau PDF
- **JWT Auth** — login, register, refresh token
- **Task Queue** — Celery + Redis untuk distributed scanning
- **Docker** — semua service jalan dalam container

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS |
| Backend | FastAPI, Python 3.11, SQLAlchemy async |
| Database | PostgreSQL 15 |
| Cache & Queue | Redis 7, Celery |
| Recon Engine | nmap, httpx, dnspython, python-whois |
| Container | Docker Compose (OrbStack) |
| Real-time | Server-Sent Events |

---

## Arsitektur

Browser (React + SSE)
│
▼
FastAPI Backend ──► Celery Worker
│                    │
▼                    ▼
PostgreSQL           Redis Pub/Sub
│
▼
SSE Stream → Browser

---

## Cara Menjalankan

### Prasyarat
- OrbStack atau Docker Desktop
- Node.js 20
- Python 3.11

### 1. Clone repo
```bash
git clone https://github.com/USERNAME/ReconCTRL.git
cd ReconCTRL
```

### 2. Setup environment
```bash
cp .env.example .env
```

### 3. Jalankan semua container
```bash
docker compose up -d
```

### 4. Jalankan frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Buka browser
http://localhost:5173

Login: `admin` / `admin123`

---

## Modul Recon

| Modul | Deskripsi |
|-------|-----------|
| `port_scan` | nmap -sV -sC + NVD CVE enrichment |
| `header` | Security headers via httpx |
| `subdomain` | crt.sh + DNS resolution |
| `osint` | WHOIS + IP geolocation |
| `dir_enum` | Common path discovery |
| `owasp` | OWASP Top 10 header checks |
| `ai_summary` | Executive report via Claude API |

---

## Environment Variables

```env
POSTGRES_DB=reconctrl
POSTGRES_USER=recon
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql+asyncpg://recon:password@postgres:5432/reconctrl
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your_secret_key
CLAUDE_API_KEY=sk-ant-xxxx
ENVIRONMENT=development
```

---

## ⚠️ Disclaimer

> ReconCTRL dibuat untuk tujuan **educational dan authorized penetration testing** saja.
> Jangan gunakan untuk scanning sistem yang bukan milikmu atau tanpa izin eksplisit.

---

## Lisensi

Educational use only.
