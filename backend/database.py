import asyncpg
import pendulum
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from decimal import Decimal
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5437/payroll")

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def create_pool(self):
        """Create asyncpg connection pool with idiomatic settings"""
        self.pool = await asyncpg.create_pool(
            dsn=self.database_url,
            min_size=5,
            max_size=20,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0,
            command_timeout=60,
            server_settings={
                'timezone': 'UTC'
            }
        )
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection with proper lifecycle management"""
        async with self.pool.acquire() as conn:
            try:
                yield conn
            except Exception:
                raise

db_manager = DatabaseManager(DATABASE_URL)

# Generic CRUD helpers for simple cases
async def _simple_get_all(table: str) -> list:
    async with db_manager.get_connection() as conn:
        records = await conn.fetch(f"SELECT * FROM {table} ORDER BY name")
        return [dict(record) for record in records]

async def _simple_create(table: str, **data) -> int:
    async with db_manager.get_connection() as conn:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(data)))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        return await conn.fetchval(query, *data.values())

async def _simple_update(table: str, entity_id: int, **data) -> bool:
    async with db_manager.get_connection() as conn:
        set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
        query = f"UPDATE {table} SET {set_clause}, updated_at = NOW() WHERE id = $1"
        result = await conn.execute(query, entity_id, *data.values())
        return result == "UPDATE 1"

async def _simple_delete(table: str, entity_id: int) -> bool:
    async with db_manager.get_connection() as conn:
        result = await conn.execute(f"DELETE FROM {table} WHERE id = $1", entity_id)
        return result == "DELETE 1"

async def init_database():
    """Initialize database schema with clean, final state"""
    async with db_manager.get_connection() as conn:
        async with conn.transaction():
            # Create all tables in correct dependency order
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS construction_sites (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    address VARCHAR(500) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    role_id INTEGER REFERENCES roles(id),
                    construction_site_id INTEGER REFERENCES construction_sites(id),
                    hourly_rate DECIMAL(10,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
                    fire_date DATE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS time_entries (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
                    punch_time TIMESTAMPTZ NOT NULL,
                    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('in', 'out', 'sick', 'vacation')),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 15.00,
                    timezone VARCHAR(50) DEFAULT 'UTC',
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_entries_punch_time ON time_entries(punch_time)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_entries_employee ON time_entries(employee_id)
            """)
            
            # Insert default settings
            await conn.execute("""
                INSERT INTO user_settings (hourly_rate) 
                VALUES (15.00) 
                ON CONFLICT (id) DO NOTHING
            """)

async def init_default_data():
    sites = [
        ("DGDI-Libreville", "Libreville, Gabon"),
        ("DGDI-Oyem", "Oyem, Gabon"), 
        ("DGDI-Meyo Kye", "Meyo Kye, Gabon"),
        ("BDT-Libreville", "Libreville, Gabon"),
        ("Cobac-Libreville", "Libreville, Gabon")
    ]
    
    existing_sites = await get_all_construction_sites()
    existing_names = {site['name'] for site in existing_sites}
    
    for name, address in sites:
        if name not in existing_names:
            await create_construction_site(name, address)
    
    roles = [
        "Guichetier", "Gardien", "Chauffeur", "Magasinier", "Coursier",
        "Chef de chantier", "Chef d'équipe-Maçon", "Chef d'équipe-Charpentier", 
        "Chef d'équipe-Ferrailleur", "Maçon", "Aide Maçon", "Charpentier",
        "Aide Charpentier", "Ferrailleur", "Aide Ferrailleur", "Betonier", "Aide"
    ]
    
    existing_roles = await get_all_roles()
    existing_role_names = {role['name'] for role in existing_roles}
    
    for role_name in roles:
        if role_name not in existing_role_names:
            await create_role(role_name)

async def get_time_entries_for_period(start_date: pendulum.DateTime, end_date: pendulum.DateTime) -> list:
    """Get time entries for date range with proper timezone handling"""
    async with db_manager.get_connection() as conn:
        records = await conn.fetch("""
            SELECT id, punch_time, entry_type, created_at
            FROM time_entries
            WHERE punch_time >= $1 AND punch_time <= $2
            ORDER BY punch_time
        """, start_date, end_date)
        
        return [
            {
                'id': record['id'],
                'punch_time': pendulum.instance(record['punch_time']),
                'entry_type': record['entry_type'],
                'created_at': pendulum.instance(record['created_at'])
            }
            for record in records
        ]

async def insert_time_entry(punch_time: pendulum.DateTime, entry_type: str) -> int:
    """Insert new time entry"""
    async with db_manager.get_connection() as conn:
        entry_id = await conn.fetchval("""
            INSERT INTO time_entries (punch_time, entry_type)
            VALUES ($1, $2)
            RETURNING id
        """, punch_time, entry_type)
        return entry_id

async def get_current_hourly_rate() -> Decimal:
    """Get current hourly rate"""
    async with db_manager.get_connection() as conn:
        rate = await conn.fetchval("""
            SELECT hourly_rate FROM user_settings WHERE id = 1
        """)
        return Decimal(str(rate)) if rate else Decimal('15.00')

async def update_hourly_rate(new_rate: Decimal) -> bool:
    """Update hourly rate"""
    async with db_manager.get_connection() as conn:
        result = await conn.execute("""
            UPDATE user_settings 
            SET hourly_rate = $1, updated_at = NOW()
            WHERE id = 1
        """, new_rate)
        return result == "UPDATE 1"

# Employee CRUD operations
async def get_all_employees() -> list:
    """Get all employees"""
    async with db_manager.get_connection() as conn:
        records = await conn.fetch("""
            SELECT e.id, e.name, e.last_name, e.role_id,
                   COALESCE(r.name, '') as role,
                   e.construction_site_id, 
                   COALESCE(cs.name, '') as construction_site,
                   e.hourly_rate, e.status, e.fire_date, e.created_at, e.updated_at
            FROM employees e
            LEFT JOIN construction_sites cs ON e.construction_site_id = cs.id
            LEFT JOIN roles r ON e.role_id = r.id
            ORDER BY e.name, e.last_name
        """)
        return [dict(record) for record in records]

async def create_employee(name: str, last_name: str, role_id: int, hourly_rate: Decimal, construction_site_id: int) -> int:
    """Create new employee"""
    async with db_manager.get_connection() as conn:
        employee_id = await conn.fetchval("""
            INSERT INTO employees (name, last_name, role_id, hourly_rate, construction_site_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, name, last_name, role_id, hourly_rate, construction_site_id)
        return employee_id

async def update_employee(employee_id: int, name: str, last_name: str, role_id: int, hourly_rate: Decimal, construction_site_id: int) -> bool:
    """Update employee"""
    async with db_manager.get_connection() as conn:
        result = await conn.execute("""
            UPDATE employees 
            SET name = $1, last_name = $2, role_id = $3, hourly_rate = $4, construction_site_id = $5, updated_at = NOW()
            WHERE id = $6
        """, name, last_name, role_id, hourly_rate, construction_site_id, employee_id)
        return result == "UPDATE 1"

async def delete_employee(employee_id: int) -> bool:
    return await _simple_delete("employees", employee_id)

async def fire_employee(employee_id: int, fire_date: str) -> bool:
    """Fire employee (set status to inactive with fire date)"""
    async with db_manager.get_connection() as conn:
        date_obj = datetime.strptime(fire_date, '%Y-%m-%d').date()
        result = await conn.execute("""
            UPDATE employees 
            SET status = 'inactive', fire_date = $2, updated_at = NOW()
            WHERE id = $1
        """, employee_id, date_obj)
        return result == "UPDATE 1"

async def hire_employee(employee_id: int) -> bool:
    """Hire employee (set status to active and clear fire date)"""
    async with db_manager.get_connection() as conn:
        result = await conn.execute("""
            UPDATE employees 
            SET status = 'active', fire_date = NULL, updated_at = NOW()
            WHERE id = $1
        """, employee_id)
        return result == "UPDATE 1"

# Construction Sites CRUD operations
async def get_all_construction_sites() -> list:
    return await _simple_get_all("construction_sites")

async def create_construction_site(name: str, address: str) -> int:
    return await _simple_create("construction_sites", name=name, address=address)

async def update_construction_site(site_id: int, name: str, address: str) -> bool:
    return await _simple_update("construction_sites", site_id, name=name, address=address)

async def delete_construction_site(site_id: int) -> bool:
    """Delete construction site"""
    async with db_manager.get_connection() as conn:
        async with conn.transaction():
            # First, update employees to remove reference to this site
            await conn.execute("""
                UPDATE employees SET construction_site_id = NULL 
                WHERE construction_site_id = $1
            """, site_id)
            
            # Then delete the construction site
            result = await conn.execute("""
                DELETE FROM construction_sites WHERE id = $1
            """, site_id)
            return result == "DELETE 1"

# Roles CRUD operations
async def get_all_roles() -> list:
    return await _simple_get_all("roles")

async def create_role(name: str) -> int:
    return await _simple_create("roles", name=name)

async def update_role(role_id: int, name: str) -> bool:
    return await _simple_update("roles", role_id, name=name)

async def delete_role(role_id: int) -> bool:
    """Delete role"""
    async with db_manager.get_connection() as conn:
        async with conn.transaction():
            # First, update employees to remove reference to this role
            await conn.execute("""
                UPDATE employees SET role_id = NULL 
                WHERE role_id = $1
            """, role_id)
            
            # Then delete the role
            result = await conn.execute("""
                DELETE FROM roles WHERE id = $1
            """, role_id)
            return result == "DELETE 1"