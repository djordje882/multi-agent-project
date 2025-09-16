# Payroll Time Tracker

Minimal payroll time tracking system with FastAPI + Vue 3.

## Quick Start

1. **Auto Setup (Recommended)**
   ```powershell
   .\setup.ps1
   ```

2. **Manual Setup**
   ```bash
   docker-compose up -d --build
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

- Frontend: http://localhost:3002
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs

## Tech Stack

- **Backend**: FastAPI 0.116.1 + asyncpg + Pendulum + PostgreSQL
- **Frontend**: Vue 3.5.18 + Vite 7.1.1 + axios
- **Database**: PostgreSQL 16 (Docker)

Built with surgical precision and zero bloat.