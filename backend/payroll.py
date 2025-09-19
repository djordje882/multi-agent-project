import pendulum
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from database import get_time_entries_for_period, get_current_hourly_rate

@dataclass
class PayrollCalculation:
    regular_hours: Decimal
    overtime_hours: Decimal
    weekend_hours: Decimal
    holiday_hours: Decimal
    sick_hours: Decimal
    vacation_hours: Decimal
    total_hours: Decimal
    gross_pay: Decimal
    hourly_rate: Decimal
    period_start: pendulum.DateTime
    period_end: pendulum.DateTime

class PayrollCalculator:
    """Business logic for payroll calculations using Pendulum for precise datetime handling"""
    
    @staticmethod
    def is_weekend(date: pendulum.Date) -> bool:
        """Check if date is weekend (Saturday=5, Sunday=6)"""
        return date.weekday() in [5, 6]
    
    @staticmethod
    def is_holiday(date: pendulum.Date) -> bool:
        """Check if date is Sunday (holiday with 2x rate)"""
        return date.weekday() == 6
    
    @staticmethod
    def calculate_daily_hours(entries: list[dict], current_time: pendulum.DateTime = None) -> Decimal:
        """Calculate work hours for a single day from punch entries"""
        if current_time is None:
            current_time = pendulum.now('UTC')
            
        total_seconds = Decimal('0')
        in_time = None
        
        for entry in entries:
            if entry['entry_type'] == 'in':
                in_time = entry['punch_time']
            elif entry['entry_type'] == 'out' and in_time:
                duration = entry['punch_time'] - in_time
                total_seconds += Decimal(str(duration.total_seconds()))
                in_time = None
        
        # If still clocked in, calculate until current_time
        if in_time:
            duration = current_time - in_time
            total_seconds += Decimal(str(duration.total_seconds()))
        
        return total_seconds / Decimal('3600')  # Convert to hours
    
    @staticmethod
    def get_15_day_period_bounds(reference_date: pendulum.Date = None) -> tuple[pendulum.DateTime, pendulum.DateTime]:
        """Get 15-day period boundaries (1st-15th, 16th-end of month)"""
        if reference_date is None:
            reference_date = pendulum.now('UTC').date()
        
        if reference_date.day <= 15:
            start_date = pendulum.datetime(reference_date.year, reference_date.month, 1, tz='UTC')
            end_date = pendulum.datetime(reference_date.year, reference_date.month, 15, 23, 59, 59, tz='UTC')
        else:
            start_date = pendulum.datetime(reference_date.year, reference_date.month, 16, tz='UTC')
            last_day = reference_date.end_of('month').day
            end_date = pendulum.datetime(reference_date.year, reference_date.month, last_day, 23, 59, 59, tz='UTC')
        
        return (start_date, end_date)
    
    @classmethod
    def _group_entries_by_date(cls, entries: list[dict]) -> dict[str, list]:
        """Group time entries by date"""
        daily_entries: dict[str, list] = {}
        for entry in entries:
            date_key = entry['punch_time'].date().isoformat()
            if date_key not in daily_entries:
                daily_entries[date_key] = []
            daily_entries[date_key].append(entry)
        return daily_entries
    
    @classmethod
    def _calculate_gross_pay(cls, regular_hours: Decimal, overtime_hours: Decimal, 
                           weekend_hours: Decimal, holiday_hours: Decimal, 
                           sick_hours: Decimal, vacation_hours: Decimal, 
                           hourly_rate: Decimal) -> Decimal:
        """Calculate gross pay from hours breakdown"""
        return (
            regular_hours * hourly_rate +
            overtime_hours * hourly_rate * Decimal('1.15') +
            weekend_hours * hourly_rate * Decimal('1.5') +
            holiday_hours * hourly_rate * Decimal('2.0') +
            sick_hours * hourly_rate * Decimal('1.0') +
            vacation_hours * hourly_rate
        )
    
    @classmethod
    async def calculate_period_pay(cls, 
                                 start_date: pendulum.DateTime = None, 
                                 end_date: pendulum.DateTime = None) -> PayrollCalculation:
        """Calculate pay for a specific period (defaults to current 15-day period)"""
        
        if start_date is None or end_date is None:
            start_date, end_date = cls.get_15_day_period_bounds()
        
        # Get all time entries for the period
        entries = await get_time_entries_for_period(start_date, end_date)
        hourly_rate = await get_current_hourly_rate()
        
        # Group entries by date
        daily_entries = cls._group_entries_by_date(entries)
        
        # Initialize totals
        regular_hours = Decimal('0')
        overtime_hours = Decimal('0')
        weekend_hours = Decimal('0')
        holiday_hours = Decimal('0')
        sick_hours = Decimal('0')
        vacation_hours = Decimal('0')
        
        # Process each day
        for date_str, day_entries in daily_entries.items():
            work_date = pendulum.parse(date_str).date()
            
            # Handle sick/vacation entries (8-hour blocks)
            sick_entries = [e for e in day_entries if e['entry_type'] == 'sick']
            vacation_entries = [e for e in day_entries if e['entry_type'] == 'vacation']
            
            if sick_entries:
                sick_hours += Decimal('8')
                continue
            
            if vacation_entries:
                vacation_hours += Decimal('8')
                continue
            
            # Calculate actual work hours from punch in/out
            punch_entries = [e for e in day_entries if e['entry_type'] in ['in', 'out']]
            if not punch_entries:
                continue
                
            daily_work_hours = cls.calculate_daily_hours(punch_entries)
            
            # Apply rate multipliers based on day type
            if cls.is_holiday(work_date):
                # Sunday = 2x rate
                holiday_hours += daily_work_hours
            elif cls.is_weekend(work_date):
                # Saturday = 1.5x rate
                weekend_hours += daily_work_hours
            else:
                # Regular weekday - split between regular and overtime
                if daily_work_hours <= Decimal('8'):
                    regular_hours += daily_work_hours
                else:
                    regular_hours += Decimal('8')
                    overtime_hours += daily_work_hours - Decimal('8')
        
        # Calculate total hours and gross pay
        total_hours = regular_hours + overtime_hours + weekend_hours + holiday_hours + sick_hours + vacation_hours
        gross_pay = cls._calculate_gross_pay(regular_hours, overtime_hours, weekend_hours, 
                                           holiday_hours, sick_hours, vacation_hours, hourly_rate)
        
        return PayrollCalculation(
            regular_hours=regular_hours,
            overtime_hours=overtime_hours,
            weekend_hours=weekend_hours,
            holiday_hours=holiday_hours,
            sick_hours=sick_hours,
            vacation_hours=vacation_hours,
            total_hours=total_hours,
            gross_pay=gross_pay,
            hourly_rate=hourly_rate,
            period_start=start_date,
            period_end=end_date
        )
    
    @classmethod
    async def get_today_hours(cls, current_time: pendulum.DateTime = None) -> dict:
        """Get today's work hours and status"""
        if current_time is None:
            current_time = pendulum.now('UTC')
            
        today = current_time.date()
        start_of_day = pendulum.datetime(today.year, today.month, today.day, tz='UTC')
        end_of_day = start_of_day.end_of('day')
        
        entries = await get_time_entries_for_period(start_of_day, end_of_day)
        
        # Check current status (last entry determines if clocked in/out)
        is_clocked_in = False
        clock_in_time = None
        
        if entries:
            last_entry = entries[-1]
            if last_entry['entry_type'] == 'in':
                is_clocked_in = True
                clock_in_time = last_entry['punch_time'].format('HH:mm')
        
        # Calculate total hours for today
        punch_entries = [e for e in entries if e['entry_type'] in ['in', 'out']]
        total_hours = cls.calculate_daily_hours(punch_entries, current_time)
        
        return {
            'total_hours': float(total_hours),
            'is_clocked_in': is_clocked_in,
            'clock_in_time': clock_in_time,
            'entry_count': len(entries)
        }