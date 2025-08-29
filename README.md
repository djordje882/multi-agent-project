# Payroll Time Tracker

Minimal payroll time tracking system with FastAPI + Vue 3.

## Quick Start

1. **Start Database**
   ```bash
   docker-compose up -d
   ```

2. **Start Backend** 
   ```bash
   cd backend
   uv run python main.py
   ```

3. **Start Frontend**
   ```bash
   cd frontend  
   pnpm dev
   ```

## Usage

- **Punch In/Out**: Track work hours
- **Sick/Vacation**: Record time off (8-hour blocks)
- **Payroll**: Calculate 15-day period pay with rates:
  - Regular: 1x rate (max 8hrs/day)
  - Overtime: 1.15x rate (>8hrs/day)
  - Weekend: 1.5x rate (Sat/Sun)
  - Holiday: 2x rate (Sundays)
  - Sick: 0.65x rate (8hrs)
  - Vacation: 1x rate (8hrs)

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Tech Stack

- **Backend**: FastAPI 0.116.1 + asyncpg + Pendulum + PostgreSQL
- **Frontend**: Vue 3.5.18 + Vite 7.1.1 + axios
- **Database**: PostgreSQL 16 (Docker)

Built with surgical precision and zero bloat.