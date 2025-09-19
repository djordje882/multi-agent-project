# Employee Payroll Time Tracker

A complete payroll and time tracking system for small businesses. Track employee hours, manage sick leave and vacation time, and automatically calculate payroll with different pay rates for regular hours, overtime, weekends, and holidays.

## 📋 What Does This Application Do?

This application helps you:
- **Track employee work hours** - Employees can punch in/out to record their work time
- **Manage construction sites and roles** - Organize employees by job sites and positions
- **Record time off** - Track sick leave and vacation days
- **Calculate payroll automatically** - Get accurate pay calculations with different rates for:
  - Regular hours (100% pay rate)
  - Overtime hours (115% pay rate - for work over 8 hours per day)
  - Weekend work (150% pay rate - Saturdays and Sundays)
  - Holiday work (200% pay rate - Sundays)
  - Sick leave (100% pay rate - full pay for justified absences)
  - Vacation time (100% pay rate)
- **Generate timesheet reports** - View and export employee time records
- **Multi-language support** - Available in French and English

Perfect for construction companies, small businesses, or any organization that needs accurate time tracking and payroll calculation.

## 🔧 Before You Start - Required Software

You need to install these programs on your computer **before** setting up the application:

### 1. Git (for downloading the application)
- **Windows**: Download from https://git-scm.com/download/win
- **Mac**: Download from https://git-scm.com/download/mac  
- **Linux**: Run `sudo apt install git` (Ubuntu) or `sudo yum install git` (CentOS)

### 2. Docker Desktop (for running the application)
- **Windows**: Download from https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- **Mac**: Download from https://desktop.docker.com/mac/main/amd64/Docker.dmg
- **Linux**: Follow instructions at https://docs.docker.com/desktop/install/linux-install/

**Important**: After installing Docker Desktop, make sure it's running (you should see the Docker whale icon in your system tray).

### 3. PowerShell (Windows only)
- Windows 10/11 already has PowerShell installed
- For older Windows versions, download from https://github.com/PowerShell/PowerShell

## 📥 Getting the Application from GitHub

### Step 1: Open Terminal/Command Prompt
- **Windows**: Press `Windows key + R`, type `powershell`, press Enter
- **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 2: Choose a location for the application
Navigate to where you want to store the application (e.g., your Desktop):

```bash
# For Windows
cd Desktop

# For Mac/Linux  
cd ~/Desktop
```

### Step 3: Download the application
Copy and paste this command exactly:

```bash
git clone https://github.com/djordje882/multi-agent-project.git
```

This will create a folder called `multi-agent-project` with all the application files.

### Step 4: Enter the application folder
```bash
cd multi-agent-project
```

## 🚀 Setting Up the Application

You have two options for starting the application:

### Option 1: Fast Startup (Recommended)
This automatically sets up everything for you.

**Windows users:**
```powershell
.\setup.ps1
```

**Mac/Linux users:**
```bash
chmod +x setup.ps1
./setup.ps1
```

**What this does:**
- Creates a secure database with default settings
- Starts all application services
- Sets up sample roles for construction workers
- Takes about 2-3 minutes to complete

### Option 2: Manual Setup (For Advanced Users)
If you prefer to control each step:

```bash
docker-compose up -d --build
```

**What this does:**
- Builds the application from source code
- Starts the database, backend API, and frontend interface
- Takes about 5-10 minutes depending on your internet speed

## 🌐 Accessing the Application

Once setup is complete, open your web browser and go to:

**Main Application:** http://localhost:3002

**API Documentation:** http://localhost:8002/docs (for developers)

**Note**: The first time you load the application, there might be a brief delay (5-10 seconds) while the database initializes. This is normal.

## 📚 How to Use the Application

### 1. Managing Roles
- Go to the "Roles" section
- Add job positions like "Mason", "Site Manager", "Carpenter", etc.
- These roles will be used when creating employees

### 2. Managing Construction Sites  
- Go to the "Sites" section
- Add your work locations with names and addresses
- Examples: "Downtown Office Building", "Highway Bridge Project"

### 3. Managing Employees
- Go to the "Employees" section
- Click "Add Employee" 
- Fill in: Name, Last Name, Role, Construction Site, Hourly Rate
- The hourly rate should be in your local currency (e.g., 25.00 for $25/hour)

### 4. Time Tracking
- Go to the "Timesheet" section
- Select an employee and date range
- Record time entries:
  - **Punch In/Out**: For regular work hours
  - **Sick**: For sick leave (counts as 8 hours at full pay)
  - **Vacation**: For vacation time (counts as 8 hours at full pay)

### 5. Generating Payroll
- Go to the "Timesheet" section
- Select employee and pay period dates
- Click "Generate PDF" to create a payroll report
- The system automatically calculates pay based on time worked and rates

## 💰 Understanding Payroll Calculations

The application uses these pay rate multipliers:

| Time Type | Pay Rate | Example (if hourly rate is $20) |
|-----------|----------|----------------------------------|
| Regular Hours (1-8 hours/day) | 100% | $20.00/hour |
| Overtime (over 8 hours/day) | 115% | $23.00/hour |
| Weekend Work (Saturday/Sunday) | 150% | $30.00/hour |
| Holiday Work (Sundays) | 200% | $40.00/hour |
| Sick Leave | 100% | $20.00/hour (8 hours) |
| Vacation | 100% | $20.00/hour (8 hours) |

**Example Calculation:**
If an employee works:
- 8 regular hours: 8 × $20 = $160
- 2 overtime hours: 2 × $23 = $46
- **Total**: $206 for the day

## 🔧 Troubleshooting Common Issues

### "Cannot connect to Docker" error
**Solution**: Make sure Docker Desktop is running. Look for the Docker whale icon in your system tray. If it's not there, start Docker Desktop from your applications.

### "Port already in use" error  
**Solution**: Stop the application and restart:
```bash
docker-compose down
docker-compose up -d
```

### Application won't load in browser
**Solutions**:
1. Wait 30 seconds after startup for initialization to complete
2. Try refreshing the page (Ctrl+F5 or Cmd+Shift+R)
3. Check that you're using the correct URL: http://localhost:3002
4. Make sure no other applications are using ports 3002, 8002, or 5437

### "Permission denied" error on Mac/Linux
**Solution**: Make the setup script executable:
```bash
chmod +x setup.ps1
```

### Database connection errors
**Solution**: Reset the database:
```bash
docker-compose down -v
docker-compose up -d --build
```

### Application is slow or unresponsive
**Solutions**:
1. Make sure you have at least 4GB of free RAM
2. Close other applications to free up memory
3. Restart Docker Desktop
4. Restart the application: `docker-compose restart`

## 🛠️ For Developers

### Technology Stack
- **Backend**: FastAPI 0.116.1 + asyncpg + Pendulum + PostgreSQL 16
- **Frontend**: Vue 3.5.18 + Vite 7.1.1 + Axios + Pinia
- **Database**: PostgreSQL 16 with asyncpg connection pooling
- **Deployment**: Docker + Docker Compose

### Project Structure
```
multi-agent-project/
├── backend/           # FastAPI application
│   ├── main.py       # API endpoints and FastAPI app
│   ├── database.py   # Database operations and schema
│   ├── payroll.py    # Payroll calculation logic
│   └── Dockerfile    # Backend container config
├── frontend/         # Vue.js application  
│   ├── src/         # Vue components and logic
│   ├── dist/        # Built frontend assets
│   └── Dockerfile   # Frontend container config
├── docker-compose.yml # Multi-container orchestration
├── setup.ps1        # Automated setup script
└── README.md        # This file
```

### Development Commands
```bash
# Start in development mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d --build

# Rebuild single service
docker-compose build backend
docker-compose up -d backend
```

### API Endpoints
- `GET /api/employees` - List all employees
- `POST /api/employees` - Create new employee
- `GET /api/roles` - List all roles
- `GET /api/construction-sites` - List all sites
- `POST /api/punch` - Record time entry
- `GET /api/payroll/calculate` - Calculate payroll for period
- `GET /api/calendar` - Get calendar data for month

### Environment Variables
Create a `.env` file for custom database settings:
```
POSTGRES_DB=payroll
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

## 📞 Getting Help

### Before Asking for Help
1. Check the troubleshooting section above
2. Make sure Docker Desktop is running
3. Try restarting the application: `docker-compose restart`
4. Check if you can access http://localhost:3002

### Reporting Issues
If you encounter a problem:

1. **Create an issue** at: https://github.com/djordje882/multi-agent-project/issues
2. **Include this information**:
   - Your operating system (Windows 10, macOS Big Sur, Ubuntu 20.04, etc.)
   - Error messages (copy and paste the exact text)
   - What you were trying to do when the error occurred
   - Steps to reproduce the problem

### Quick Self-Help Commands
```bash
# Check if Docker is running
docker version

# Check if application containers are running  
docker ps

# View application logs
docker-compose logs

# Complete reset (destroys all data)
docker-compose down -v
docker-compose up -d --build
```

## 🔄 Updating the Application

To get the latest version:

```bash
# Stop the application
docker-compose down

# Get latest code
git pull origin master

# Rebuild and restart
docker-compose up -d --build
```

**Note**: Updates may reset your data. Make sure to backup important information before updating.

## 📄 License

This project is provided as-is for educational and business use. See the repository for full license details.

---

**Built with surgical precision and zero bloat** - A modern, reliable payroll solution for small businesses.