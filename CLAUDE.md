# Claude Operating System

## Core Principles
- **THINK HARD. DO NOT BLOAT CODE. Keep code minimalistic** - Primary directive for all development
- Be direct and concise (≤4 lines unless detail requested)
- No unnecessary explanations or summaries unless asked
- Focus exactly on what was requested, nothing more
- Proactive TodoWrite usage for complex multi-step tasks

## Technical Stack & Patterns

### Architecture
- **Frontend**: Vue 3.5.18 Composition API + Axios + pnpm
- **Backend**: FastAPI 0.116.1 + Pydantic + AsyncPG + uv
- **Database**: PostgreSQL with proper foreign keys
- **Currency**: XAF (FCFA) only - no switching, settings removed
- **Multi-agent approach** with specialized agents for complex tasks

### Business Logic Patterns
```javascript
// Payment rounding: 0-333=0, 334-666=500, 667-999=1000
const roundPayment = (value) => {
  const r = Math.round(value) % 1000
  return Math.round(value) - r + (r <= 333 ? 0 : r <= 666 ? 500 : 1000)
}

// Travel allowance: Only if date range includes any month-end
const getTravelAllowance = (employeeIndex) => {
  for (let d = new Date(fromDate); d <= new Date(toDate); d.setDate(d.getDate() + 1)) {
    const lastDayOfMonth = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate()
    if (d.getDate() === lastDayOfMonth) {
      return employee.role.toLowerCase().includes('aider') ? '70000.00' : '100000.00'
    }
  }
  return '0.00'
}

// Rate conversion: Daily salary ÷ 8 = hourly rate
const hourlyRate = dailySalary / 8

// Cross-month date handling - CRITICAL for PDF accuracy
const getPayrollDays = () => {
  const payrollDays = []
  for (let d = new Date(fromDate); d <= new Date(toDate); d.setDate(d.getDate() + 1)) {
    payrollDays.push({
      date: d.getDate(),
      month: d.getMonth() + 1,  // MUST include month context
      year: d.getFullYear(),    // MUST include year context
      dayName: dayNames[d.getDay()],
      isWeekend: d.getDay() === 0 || d.getDay() === 6
    })
  }
  return payrollDays
}

// Month-aware localStorage access for cross-month ranges
const getTimeEntry = (employeeId, day, type, month, year) => {
  const monthKey = `${year}-${month}`
  const dayKey = `${employeeId}-${day}-${type}`
  return monthlyData[monthKey]?.[dayKey] || ''
}
```

### Database Patterns
```sql
-- Always use foreign key relationships
ALTER TABLE employees ADD CONSTRAINT fk_construction_site 
FOREIGN KEY (construction_site_id) REFERENCES construction_sites(id);

-- Handle deletions with cascading updates
UPDATE employees SET construction_site_id = NULL WHERE construction_site_id = $1;
DELETE FROM construction_sites WHERE id = $1;
```

### CSS Variable System (Anti-Bloat)
```css
:root {
  /* Essential Colors (10 variables) */
  --bg-primary: #1A1A2E;
  --bg-secondary: #2C2C4E;
  --accent: #8B5CF6;
  --accent-hover: #7C3AED;
  --text-primary: #E0E0E0;
  --text-secondary: #A0A0A0;
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --border: rgba(224, 224, 224, 0.1);
  
  /* Essential Spacing (3 variables) */
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  
  /* Essential Typography (3 variables) */
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  
  /* Essential Font Weights (3 variables) */
  --font-normal: 400;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Essential Radius (2 variables) */
  --radius: 0.5rem;
  --radius-lg: 0.75rem;
  
  /* Essential Shadow (1 variable) */
  --shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
```
**Principle**: Never exceed 25 CSS variables. Group by purpose, eliminate variations.

### Vue Patterns
```javascript
// CRUD Component Pattern (eliminates 150+ lines)
<CrudView :config="crudConfig" />

const crudConfig = {
  endpoint: 'employees', entityName: 'Employé',
  formDefaults: { name: '', email: '' },
  tableColumns: [{ key: 'name', label: 'Nom' }],
  searchFields: ['name', 'email'],
  messages: { createSuccess: 'Créé avec succès' },
  customActions: { fire: fireEmployee }
}

// Provide/inject over prop drilling
provide('loading', loading)
provide('showMessage', showMessage)
const loading = inject('loading')

// Data-driven loops over hardcoded repetition
<td v-for="hourType in hourTypes" :key="hourType">
  {{ getHoursByType(hourType, index) }}
</td>

// Generic CRUD composable
export function useCrud(config, props) {
  const data = ref([])
  const showModal = ref(false)
  // ... reusable CRUD logic
  return { data, showModal, loadData, saveEntity }
}

// Reactivity patterns - CRITICAL for dynamic data
// Use computed() for reactive data that changes
const extraData = computed(() => ({ roles, sites }))  // Not ref()
// Template access: extraData.value.roles or extraData.roles depending on context

// Search functionality - minimal and reusable
const searchTerm = ref('')
const filteredData = computed(() => {
  const searchLower = searchTerm.value.toLowerCase()
  return data.value.filter(item => 
    searchFields.some(field => 
      (item[field] || '').toLowerCase().includes(searchLower)
    )
  )
})

// Hamburger menu - mobile-first approach
.nav-menu { 
  display: none; /* Hidden by default */
  position: absolute; 
  background: var(--bg-secondary);
}
.nav-menu.active { display: flex; flex-direction: column; }
// Remove desktop media queries for consistent behavior
```

### FastAPI Patterns
```python
# Pydantic models with validation
class EntityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
# CRUD endpoints
@app.get("/api/entities")
async def get_entities():
    return await get_all_entities()

@app.post("/api/entities") 
async def create_entity(entity: EntityCreateRequest):
    entity_id = await create_entity(entity.name)
    return {"success": True, "entity_id": entity_id}

# Error handling decorator - MUST use @wraps for FastAPI compatibility
from functools import wraps
def handle_errors(error_prefix: str):
    def decorator(func):
        @wraps(func)  # CRITICAL: Preserves function signatures for FastAPI DI
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"{error_prefix}: {str(e)}")
        return wrapper
    return decorator
```

## UI/UX Guidelines

### Typography
- **Font**: Inter (weights 300-700)
- **Hierarchy**: Use font weights to create clear visual hierarchy
- **Colors**: Primary text (#E0E0E0), Secondary text (#A0A0A0)

### Interactive Elements
- **Hover states**: Use `--primary-700` for hover
- **Buttons**: Purple accent (`--primary-accent`) with white text
- **Forms**: CSS variables for consistent styling
- **Dropdowns**: Remove browser styling with `appearance: none`

### Data Display
- **Tables**: Sticky first columns for large datasets
- **Text truncation**: `max-width` + `overflow: hidden` + `text-overflow: ellipsis` + `title` attribute for hover
- **Button sizing**: Minimal padding (4px 8px), small font (10px), reduced gap (4px) to fit table cells
- **Currency display**: Always `white-space: nowrap` to prevent wrapping
- **PDF tables**: Uniform column widths (`width: 12.5%`), abbreviated headers to prevent 3-row wrapping
- **Scrolling**: Custom drag + Shift+wheel for timesheet tables
- **Modals**: Overlay pattern for CRUD operations
- **Search/Sort**: Consistent controls across all list views

## Development Workflow

### Tool Usage Priority
1. **TodoWrite first**: Before any complex task (triggers: multiple steps, user lists, planning needed)
2. **Specialized agents** for domain expertise (codebase analysis, security, performance)
3. **Tool batching**: Multiple Read/Grep/Bash calls in single response
4. **MultiEdit** for coordinated file changes
5. **Evidence-based**: Always include file:line references when discussing code

### Analysis Methodology
1. **3-Pass Analysis Protocol**: For accuracy and completeness
   - **Pass 1**: Structural analysis (architecture, patterns, organization)
   - **Pass 2**: Implementation analysis (logic, algorithms, data flow)
   - **Pass 3**: Quality analysis (SOLID, duplication, optimization opportunities)
2. **100% Evidence-Based**: Every claim must have specific file:line references
3. **Quantified Results**: Document line counts, reduction percentages, specific metrics

### Debugging Protocol
1. **Systematic Error Location**:
   - Pass 1: Analyze logic flow and data generation
   - Pass 2: Check data lookup and storage patterns
   - Pass 3: Verify complete flow from input to output
2. **100% Certainty Before Fixes**: Never guess - locate exact error source
3. **Evidence-First Approach**: Must identify specific file:line where error occurs
4. **Cross-Context Validation**: For date ranges, verify month/year context preservation
5. **Data Integrity Verification**: Ensure PDF matches timesheet exactly - no phantom data

### Code Organization
```
project/
├── backend/
│   ├── main.py          # FastAPI app + routes
│   ├── database.py      # CRUD operations
│   └── models.py        # Pydantic models
└── frontend/src/
    └── App.vue          # Single-file Vue component
```

### Error Handling
- Always try/catch with specific error messages
- Show user-friendly messages via toast system
- Log technical details for debugging

### Data Validation
- Frontend: Required fields + maxlength
- Backend: Pydantic validation with Field constraints
- Database: NOT NULL + CHECK constraints

## Multi-Language Support

### Pattern
```javascript
// Separate translation objects for complex data
const roleTranslations = {
  en: { 'Maçon': 'Mason', 'Chef de chantier': 'Site Manager' },
  fr: { 'Maçon': 'Maçon', 'Chef de chantier': 'Chef de chantier' }
}

translateRole(roleName) {
  return roleTranslations[this.currentLanguage][roleName] || roleName
}
```

## Performance Patterns

### Database
- Use indexes on frequently queried columns
- LEFT JOIN for optional relationships
- Batch inserts for initial data

### Frontend  
- Computed properties for filtered/sorted data
- Lazy loading for large datasets
- CSS variables for theme switching performance

### Browser Compatibility
- `option:hover` styling not supported - accept browser defaults
- Use `-webkit-appearance: none` to remove input spinners
- CSS Grid for layout, Flexbox for components

## Command Patterns

### Common Commands
```bash
# Development (pnpm + uv)
pnpm run dev                                    # Frontend
uv run python -m uvicorn main:app --reload     # Backend

# Docker containers
docker ps                                       # Check running containers
# Look for: salary_tracker_frontend:3002, salary_tracker_api:8002, salary_tracker_db:5437

# Testing  
npm run test
pytest

# Database
psql -d database_name
```

### Data Import Patterns
```python
# Bulk worker creation with rate conversion
workers = [("LAST", "FIRST", "ROLE", daily_salary), ...]
for last_name, first_name, role_name, daily_salary in workers:
    hourly_rate = daily_salary / 8  # Always convert daily to hourly
    # Map roles, create employees via API
```

### Git Workflow
- Commit with descriptive messages
- Include "Generated with Claude Code" attribution
- Never push unless explicitly requested

## Change Management & Risk Mitigation

### Bloat Detection Protocol
1. **5-Pass Analysis Method**: Comprehensive bloat identification
   - **Pass 1**: Template bloat (duplicate code, repetitive structures)
   - **Pass 2**: JavaScript bloat (over-abstraction, unused complexity)
   - **Pass 3**: Data structure bloat (redundant state, prop drilling)
   - **Pass 4**: CSS bloat (excessive variables, unused styles)
   - **Pass 5**: Architecture bloat (unnecessary layers, over-engineering)
   - Document reduction percentages and line counts
   - Never change without 100% certainty of compatibility

2. **Incremental Change Strategy**
   - **NEVER** change frontend AND backend simultaneously
   - Maintain API compatibility during transitions
   - Test each layer independently before proceeding
   - Always preserve rollback capability

3. **Compatibility Requirements**
   - Keep old endpoints while adding new ones
   - Ensure backward compatibility for all changes
   - Verify container/environment compatibility
   - Test build systems before structural changes

### Failure Recovery
- **Immediate rollback** capability required for all optimizations
- Preserve original files as `-old` backups
- Quick restoration process when changes break functionality
- No blame, just rapid problem-solving focus

## Operational Guidelines

### User Interaction Patterns
- **Ultra-concise responses**: ≤4 lines unless detail explicitly requested
- **Zero fluff policy**: No preambles, explanations, or summaries unless asked
- **Proactive TodoWrite**: Any task with 3+ steps gets todo tracking
- **"THINK HARD" directive**: Deep analysis before any code changes - emphasized repeatedly
- **Tool use interruptions**: User will reject tool use mid-execution if wrong approach
- **Immediate compliance**: When user says "NO" or interrupts, STOP completely and wait for direction
- **Solution rejection**: User may reject first 2-3 solutions until optimal found - expect iterations
- **3-question rule**: Ask clarifying questions before complex tasks to avoid wrong direction
- **Risk-first mindset**: "MUST not break frontend/backend/database" is paramount
- **One thing at a time**: Never change multiple layers simultaneously
- **Context awareness**: Recognize when approaching context limits, prioritize essential information
- **Iterative refinement**: Expect multiple analysis rounds until user satisfaction achieved
- **100% certainty requirement**: Never make changes without complete understanding and evidence
- **Multi-pass analysis protocol**: Use systematic 3-pass approach for complex debugging
- **Evidence-first debugging**: Locate exact error with file:line precision before fixing

### Problem-Solving Approach
1. **Systematic analysis** over quick fixes
2. **Tool batching** for efficiency
3. **Specialized agents** for complex tasks
4. **Evidence-based decisions** with specific line numbers/examples
5. **Minimize output tokens** while maintaining quality

### Code Quality Standards
- **Minimalism over cleverness** - simple solutions preferred
- **Working code over perfect code** - functionality first
- **Consistency over innovation** - follow existing patterns
- **Compatibility over optimization** - don't break working systems

## Operational Methodology

### Change Execution Protocol
1. **Read first**: Always examine existing code before any modifications
2. **TodoWrite for planning**: Multi-step tasks require explicit tracking
3. **Single-layer changes**: Frontend OR backend OR database - never multiple
4. **Test immediately**: Verify each change before proceeding
5. **Stop on uncertainty**: Ask for direction rather than assume

### Communication Protocol  
- **Answer only what's asked**: No additional context unless requested
- **Use file:line references**: `src/App.vue:175` for specific code locations
- **Mark todos as completed**: Update progress immediately after each task
- **Batch tool calls**: Multiple Read/Grep operations in single response

### Risk Mitigation Rules
- **Compatibility first**: Never break working functionality  
- **Incremental changes**: Small, verifiable steps over large refactors
- **Evidence-based decisions**: Specific line counts and file analysis
- **Rollback ready**: Preserve ability to undo any optimization

### Critical Technical Requirements
- **FastAPI decorators**: MUST use `@wraps(func)` to preserve function signatures for dependency injection
- **Vue reactivity**: Use `computed()` for dynamic data that changes over time
- **Database integrity**: Always handle foreign key constraints with UPDATE + DELETE pattern
- **Function signature preservation**: Essential for framework compatibility (FastAPI, Vue composition API)
- **Error context**: Maintain specific error messages while avoiding information leakage

This operating system prioritizes **minimalistic, working solutions** with **systematic risk management**, **ultra-concise communication**, and **rigorous technical accuracy**.