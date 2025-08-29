from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Optional
import pendulum
import asyncpg
from functools import wraps

import database as db
from payroll import PayrollCalculator

class PunchRequest(BaseModel):
    entry_type: str = Field(..., pattern="^(in|out|sick|vacation)$")
    timestamp: Optional[str] = None

class RateUpdateRequest(BaseModel):
    hourly_rate: float = Field(..., gt=0)

class EmployeeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role_id: int = Field(..., gt=0)
    hourly_rate: float = Field(..., gt=0)
    construction_site_id: int = Field(..., gt=0)

class EmployeeFireRequest(BaseModel):
    fire_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')

class ConstructionSiteRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)

class RoleRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class PunchResponse(BaseModel):
    success: bool
    message: str
    entry_id: int
    timestamp: str

class TodayHoursResponse(BaseModel):
    total_hours: float
    is_clocked_in: bool
    clock_in_time: Optional[str] = None
    entry_count: int

class PayrollResponse(BaseModel):
    regular_hours: float
    overtime_hours: float
    weekend_hours: float
    holiday_hours: float
    sick_hours: float
    vacation_hours: float
    total_hours: float
    gross_pay: float
    hourly_rate: float
    period_start: str
    period_end: str

# FastAPI 0.116.1 lifespan pattern
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.db_manager.create_pool()
    await db.init_database()
    await db.init_default_data()
    
    yield
    # Shutdown
    await db.db_manager.close_pool()

app = FastAPI(
    title="Payroll Time Tracker",
    description="Minimal payroll time tracking API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def prepare_employee_data(employee: EmployeeRequest) -> dict:
    """Convert EmployeeRequest to dict with proper Decimal conversion"""
    data = employee.dict()
    data["hourly_rate"] = Decimal(str(employee.hourly_rate))
    return data

def handle_errors(error_prefix: str):
    """Decorator to handle common exception patterns"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"{error_prefix}: {str(e)}")
        return wrapper
    return decorator

@app.post("/api/punch", response_model=PunchResponse)
async def punch_clock(request: PunchRequest):
    """Punch in/out or record sick/vacation time"""
    try:
        # Parse timestamp or use current time
        if request.timestamp:
            punch_time = pendulum.parse(request.timestamp)
        else:
            punch_time = pendulum.now('UTC')
        
        # Insert time entry
        entry_id = await db.insert_time_entry(punch_time, request.entry_type)
        
        return PunchResponse(
            success=True,
            message=f"{request.entry_type.title()} recorded successfully",
            entry_id=entry_id,
            timestamp=punch_time.to_iso8601_string()
        )
    
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

@app.get("/api/hours/today", response_model=TodayHoursResponse)
async def get_today_hours():
    """Get today's work hours and current punch status"""
    try:
        hours_data = await PayrollCalculator.get_today_hours()
        
        return TodayHoursResponse(
            total_hours=hours_data['total_hours'],
            is_clocked_in=hours_data['is_clocked_in'],
            clock_in_time=hours_data['clock_in_time'],
            entry_count=hours_data['entry_count']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hours: {str(e)}")

@app.get("/api/payroll/calculate", response_model=PayrollResponse)
async def calculate_payroll(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Calculate payroll for current 15-day period or specified date range"""
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = pendulum.parse(start_date).start_of('day')
        if end_date:
            end_dt = pendulum.parse(end_date).end_of('day')
        
        # Calculate payroll
        calculation = await PayrollCalculator.calculate_period_pay(start_dt, end_dt)
        
        return PayrollResponse(
            regular_hours=float(calculation.regular_hours),
            overtime_hours=float(calculation.overtime_hours),
            weekend_hours=float(calculation.weekend_hours),
            holiday_hours=float(calculation.holiday_hours),
            sick_hours=float(calculation.sick_hours),
            vacation_hours=float(calculation.vacation_hours),
            total_hours=float(calculation.total_hours),
            gross_pay=float(calculation.gross_pay),
            hourly_rate=float(calculation.hourly_rate),
            period_start=calculation.period_start.to_iso8601_string(),
            period_end=calculation.period_end.to_iso8601_string()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.put("/api/settings/rate")
async def update_rate(request: RateUpdateRequest):
    try:
        rate = Decimal(str(request.hourly_rate))
        success = await db.update_hourly_rate(rate)
        
        if success:
            return {"success": True, "new_rate": float(rate)}
        else:
            raise HTTPException(status_code=500, detail="Failed to update rate")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rate: {str(e)}")

@app.get("/api/settings/rate")
async def get_current_rate():
    try:
        rate = await db.get_current_hourly_rate()
        return {"hourly_rate": float(rate)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rate: {str(e)}")

@app.get("/api/calendar")
async def get_calendar_data(
    year: int = None,
    month: int = None
):
    """Get calendar data with time entries for a specific month"""
    try:
        # Default to current month if not specified
        if year is None or month is None:
            now = pendulum.now('UTC')
            year = now.year
            month = now.month
        
        # Get month boundaries
        start_of_month = pendulum.datetime(year, month, 1, tz='UTC')
        end_of_month = start_of_month.end_of('month')
        
        # Get all entries for the month
        entries = await db.get_time_entries_for_period(start_of_month, end_of_month)
        
        # Group entries by date
        calendar_data = {}
        for entry in entries:
            date_key = entry['punch_time'].date().isoformat()
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            
            calendar_data[date_key].append({
                'id': entry['id'],
                'time': entry['punch_time'].format('HH:mm'),
                'type': entry['entry_type']
            })
        
        return {
            "year": year,
            "month": month,
            "entries": calendar_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar error: {str(e)}")

# Employee management endpoints
@app.get("/api/employees")
@handle_errors("Error retrieving employees")
async def get_employees():
    return await db.get_all_employees()

@app.post("/api/employees")
@handle_errors("Error creating employee")
async def create_employee(employee: EmployeeRequest):
    data = prepare_employee_data(employee)
    employee_id = await db.create_employee(**data)
    return {"success": True, "employee_id": employee_id, "message": "Employee created successfully"}

@app.put("/api/employees/{employee_id}")
@handle_errors("Error updating employee")
async def update_employee(employee_id: int, employee: EmployeeRequest):
    data = prepare_employee_data(employee)
    success = await db.update_employee(employee_id, **data)
    if success:
        return {"success": True, "message": "Employee updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@app.delete("/api/employees/{employee_id}")
@handle_errors("Error deleting employee")
async def delete_employee(employee_id: int):
    success = await db.delete_employee(employee_id)
    if success:
        return {"success": True, "message": "Employee deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@app.put("/api/employees/{employee_id}/fire")
async def fire_employee(employee_id: int, fire_request: EmployeeFireRequest):
    try:
        success = await db.fire_employee(employee_id, fire_request.fire_date)
        if success:
            return {"success": True, "message": "Employee updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating employee: {str(e)}")

@app.put("/api/employees/{employee_id}/hire")
async def hire_employee(employee_id: int):
    try:
        success = await db.hire_employee(employee_id)
        if success:
            return {"success": True, "message": "Employee updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating employee: {str(e)}")

# Construction Sites endpoints
@app.get("/api/construction-sites")
@handle_errors("Error retrieving construction sites")
async def get_construction_sites():
    return await db.get_all_construction_sites()

@app.post("/api/construction-sites")
@handle_errors("Error creating construction site")
async def create_construction_site(site: ConstructionSiteRequest):
    construction_site_id = await db.create_construction_site(**site.dict())
    return {"success": True, "construction_site_id": construction_site_id, "message": "Construction site created successfully"}

@app.put("/api/construction-sites/{site_id}")
async def update_construction_site(site_id: int, site: ConstructionSiteRequest):
    try:
        success = await db.update_construction_site(site_id, **site.dict())
        if success:
            return {"success": True, "message": "Construction site updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Construction site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating construction site: {str(e)}")

@app.delete("/api/construction-sites/{site_id}")
async def delete_construction_site(site_id: int):
    try:
        success = await db.delete_construction_site(site_id)
        if success:
            return {"success": True, "message": "Construction site deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Construction site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting construction site: {str(e)}")

# Roles API endpoints
@app.get("/api/roles")
@handle_errors("Error retrieving roles")
async def get_roles():
    return await db.get_all_roles()

@app.post("/api/roles")
async def create_role(role: RoleRequest):
    try:
        role_id = await db.create_role(**role.dict())
        return {"success": True, "role_id": role_id, "message": "Role created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating role: {str(e)}")

@app.put("/api/roles/{role_id}")
async def update_role(role_id: int, role: RoleRequest):
    try:
        success = await db.update_role(role_id, **role.dict())
        if success:
            return {"success": True, "message": "Role updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Role not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")

@app.delete("/api/roles/{role_id}")
async def delete_role(role_id: int):
    try:
        success = await db.delete_role(role_id)
        if success:
            return {"success": True, "message": "Role deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Role not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": pendulum.now('UTC').to_iso8601_string()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )