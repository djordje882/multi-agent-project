<template>
  <div>
    <div class="content-header">
      <h2>Feuille de Temps</h2>
      <div class="timesheet-controls">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Rechercher un employé..." 
          class="search-input"
        >
        <select v-model="selectedConstructionSite">
          <option value="">Tous les Sites de Construction</option>
          <option v-for="site in uniqueConstructionSites" :key="site" :value="site">
            {{ site }}
          </option>
        </select>
        <select v-model="selectedMonth" @change="onDateChange">
          <option v-for="month in 12" :key="month" :value="month">
            {{ getMonthName(month) }}
          </option>
        </select>
        <select v-model="selectedYear" @change="onDateChange">
          <option v-for="year in getYearOptions()" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        <button @click="generatePDF" class="btn pdf-btn">Générer PDF</button>
      </div>
    </div>

    <div class="table-container timesheet-container" 
         ref="timesheetContainer"
         @mousedown="startDrag" 
         @wheel="handleWheel">
      <table class="timesheet-table">
        <thead>
          <tr>
            <th>Employé</th>
            <th v-for="dayInfo in monthDays" :key="dayInfo.date" :class="{ weekend: dayInfo.isWeekend }">
              <div>{{ dayInfo.date }}</div>
              <div class="day-name">{{ dayInfo.dayName }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="employee in filteredTimesheetEmployees" :key="employee.id">
            <td class="employee-info">
              <div class="employee-name">{{ employee.name }} {{ employee.last_name }}</div>
              <div class="employee-role">{{ employee.role }}</div>
            </td>
            <td v-for="dayInfo in monthDays" :key="dayInfo.date" :class="['timesheet-cell', { weekend: dayInfo.isWeekend }]">
              <template v-for="cellData in [timesheetCellData(employee, dayInfo)]" :key="'cell-data'">
                <select class="status-select" :title="cellData.title" :disabled="cellData.isDisabled" :value="cellData.status" @change="setTimeEntry(employee.id, dayInfo.date, 'status', $event.target.value)">
                  <option value="">Régulier</option>
                  <option value="weekend">Fin de Semaine</option>
                  <option value="holiday">Vacances</option>
                  <option value="workholiday">Travail pour les Vacances</option>
                  <option value="sick">Malade</option>
                  <option value="justified">Absence Justifiée</option>
                </select>
                <div v-if="cellData.status === 'holiday'" class="fixed-hours">8 heures</div>
                <div v-else-if="cellData.status === 'justified'" class="fixed-hours">
                  Justifié
                  <label class="justified-check">
                    <input type="checkbox" :checked="cellData.verified" @change="setTimeEntry(employee.id, dayInfo.date, 'verified', $event.target.checked)" :disabled="cellData.isDisabled">
                    ✓
                  </label>
                </div>
                <div v-else-if="cellData.status === 'sick'" class="fixed-hours">
                  Malade
                  <label class="justified-check">
                    <input type="checkbox" :checked="cellData.verified" @change="setTimeEntry(employee.id, dayInfo.date, 'verified', $event.target.checked)" :disabled="cellData.isDisabled">
                    ✓
                  </label>
                </div>
                <template v-else>
                  <input type="time" class="time-input" :disabled="cellData.isDisabled" :value="cellData.inTime" @input="setTimeEntry(employee.id, dayInfo.date, 'in', $event.target.value)" @dblclick="clearTimeEntry(employee.id, dayInfo.date, 'in')">
                  <input type="time" class="time-input" :disabled="cellData.isDisabled" :value="cellData.outTime" @input="setTimeEntry(employee.id, dayInfo.date, 'out', $event.target.value)" @dblclick="clearTimeEntry(employee.id, dayInfo.date, 'out')">
                  <input type="number" class="bonus-input" :disabled="cellData.isDisabled" :value="cellData.bonus" @input="setTimeEntry(employee.id, dayInfo.date, 'bonus', $event.target.value)" @dblclick="clearTimeEntry(employee.id, dayInfo.date, 'bonus')" :placeholder="getCurrencySymbol()" min="0" step="0.01">
                </template>
              </template>
            </td>
          </tr>
          <tr v-if="filteredTimesheetEmployees.length === 0">
            <td :colspan="monthDays.length + 1" class="no-data">
              {{ timesheetEmployees.length === 0 ? 'Aucun employé actif trouvé' : 'Aucun employé trouvé pour le site sélectionné' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useTranslations } from '../composables/useTranslations'
import axios from 'axios'

const API_BASE = '/api'

export default {
  name: 'TimesheetView',
  setup(_, { emit }) {
    const showMessage = inject('showMessage')
    const withLoading = inject('withLoading')
    const { getCurrencySymbol } = useTranslations()
    
    const selectedYear = ref(new Date().getFullYear())
    const selectedMonth = ref(new Date().getMonth() + 1)
    const selectedConstructionSite = ref('')
    const searchTerm = ref('')
    const timesheetEmployees = ref([])
    const monthDays = ref([])
    const timesheetData = ref({})
    const timesheetContainer = ref(null)
    const isDragging = ref(false)
    const startX = ref(0)
    const startY = ref(0)

    const uniqueConstructionSites = computed(() => {
      const sites = [...new Set(timesheetEmployees.value.map(emp => emp.construction_site).filter(Boolean))]
      return sites.sort()
    })

    const filteredTimesheetEmployees = computed(() => {
      let filtered = timesheetEmployees.value
      
      // Filter by construction site
      if (selectedConstructionSite.value) {
        filtered = filtered.filter(emp => emp.construction_site === selectedConstructionSite.value)
      }
      
      // Filter by search term
      if (searchTerm.value) {
        const searchLower = searchTerm.value.toLowerCase()
        filtered = filtered.filter(emp => 
          (emp.name || '').toLowerCase().includes(searchLower) ||
          (emp.last_name || '').toLowerCase().includes(searchLower)
        )
      }
      
      return filtered
    })

    const getStatusDisplay = (status, isWeekend) => {
      const map = { weekend: 'Fin de Semaine', holiday: 'Vacances', workholiday: 'Travail Vacances', sick: 'Malade', justified: 'Justifié' }
      return status ? map[status] || status : (isWeekend ? 'Fin de Semaine' : 'Régulier')
    }

    const timesheetCellData = (employee, dayInfo) => {
      const status = getTimeEntry(employee.id, dayInfo.date, 'status')
      const isDisabled = isInputDisabled(employee, dayInfo.date)
      return {
        status: status || (dayInfo.isWeekend ? 'weekend' : ''),
        title: getStatusDisplay(status, dayInfo.isWeekend),
        isDisabled,
        inTime: getTimeEntry(employee.id, dayInfo.date, 'in'),
        outTime: getTimeEntry(employee.id, dayInfo.date, 'out'),
        bonus: getTimeEntry(employee.id, dayInfo.date, 'bonus'),
        verified: getTimeEntry(employee.id, dayInfo.date, 'verified')
      }
    }

    const getMonthName = (month) => {
      const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
      return months[month - 1]
    }

    const getYearOptions = () => {
      const currentYear = new Date().getFullYear()
      return Array.from({length: 5}, (_, i) => currentYear - 2 + i)
    }

    const generateMonthDays = () => {
      const daysInMonth = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
      const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
      
      monthDays.value = Array.from({length: daysInMonth}, (_, i) => {
        const date = i + 1
        const dayOfWeek = new Date(selectedYear.value, selectedMonth.value - 1, date).getDay()
        return {
          date,
          dayName: dayNames[dayOfWeek],
          isWeekend: dayOfWeek === 0 || dayOfWeek === 6
        }
      })
    }

    const loadEmployees = async () => {
      await withLoading(async () => {
        try {
          const response = await axios.get(`${API_BASE}/employees`)
          const currentDate = new Date(selectedYear.value, selectedMonth.value - 1, 1)
          
          timesheetEmployees.value = response.data.filter(emp => {
            if (emp.status === 'active') return true
            if (emp.status === 'inactive' && emp.fire_date) {
              const fireDate = new Date(emp.fire_date)
              return currentDate <= fireDate
            }
            return false
          })
        } catch (error) {
          showMessage('Erreur lors du chargement des employés: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    }

    const loadTimesheet = async () => {
      generateMonthDays()
      clearTimesheetData()
      await loadEmployees()
    }

    const clearTimesheetData = () => {
      timesheetData.value = {}
      loadTimesheetData()
    }

    const saveTimesheetData = () => {
      const storageKey = `timesheet-${selectedYear.value}-${selectedMonth.value}`
      localStorage.setItem(storageKey, JSON.stringify(timesheetData.value))
    }

    const loadTimesheetData = () => {
      const storageKey = `timesheet-${selectedYear.value}-${selectedMonth.value}`
      const saved = localStorage.getItem(storageKey)
      timesheetData.value = saved ? JSON.parse(saved) : {}
    }

    const getTimeEntry = (employeeId, day, type) => {
      const key = `${employeeId}-${day}-${type}`
      if (type === 'verified') {
        return timesheetData.value[key] === true
      }
      return timesheetData.value[key] || ''
    }

    const setTimeEntry = (employeeId, day, type, value) => {
      const key = `${employeeId}-${day}-${type}`
      timesheetData.value[key] = value
      saveTimesheetData()
    }

    const clearTimeEntry = (employeeId, day, type) => {
      const key = `${employeeId}-${day}-${type}`
      timesheetData.value[key] = ''
      saveTimesheetData()
    }

    const isInputDisabled = (employee, day) => {
      const currentDay = new Date(selectedYear.value, selectedMonth.value - 1, day)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      // Disable future dates
      if (currentDay > today) return true
      
      // Disable after fire date
      if (employee.status === 'inactive' && employee.fire_date) {
        const fireDate = new Date(employee.fire_date)
        return currentDay > fireDate
      }
      
      return false
    }

    const generatePDF = () => {
      if (filteredTimesheetEmployees.value.length === 0) {
        showMessage('Aucun employé pour générer le PDF', 'error')
        return
      }
      
      const pdfData = {
        employees: filteredTimesheetEmployees.value,
        monthDays: monthDays.value,
        timesheetData: timesheetData.value,
        selectedYear: selectedYear.value,
        selectedMonth: selectedMonth.value,
        selectedConstructionSite: selectedConstructionSite.value
      }
      
      emit('generate-pdf', pdfData)
    }

    const startDrag = (e) => {
      const container = timesheetContainer.value
      if (!container) return
      
      isDragging.value = true
      startX.value = e.pageX + container.scrollLeft
      startY.value = e.pageY + container.scrollTop
      
      const handleMouseMove = (e) => {
        if (!isDragging.value) return
        e.preventDefault()
        container.scrollLeft = startX.value - e.pageX
        container.scrollTop = startY.value - e.pageY
      }
      
      const handleMouseUp = () => {
        isDragging.value = false
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
        container.style.cursor = 'default'
      }
      
      container.style.cursor = 'grabbing'
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    const handleWheel = (e) => {
      if (!e.shiftKey) return
      
      e.preventDefault()
      const container = timesheetContainer.value
      if (!container) return
      
      container.scrollLeft += e.deltaY
    }

    const onDateChange = () => {
      loadTimesheet()
    }

    onMounted(() => {
      generateMonthDays()
      clearTimesheetData()
      loadEmployees()
    })

    return {
      selectedYear,
      selectedMonth,
      selectedConstructionSite,
      searchTerm,
      timesheetEmployees,
      monthDays,
      timesheetData,
      timesheetContainer,
      uniqueConstructionSites,
      filteredTimesheetEmployees,
      timesheetCellData,
      getStatusDisplay,
      getMonthName,
      getYearOptions,
      loadTimesheet,
      onDateChange,
      setTimeEntry,
      getTimeEntry,
      clearTimeEntry,
      generatePDF,
      startDrag,
      handleWheel,
      getCurrencySymbol
    }
  }
}
</script>

<style scoped>
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.content-header h2 {
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

.timesheet-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}


.search-input {
  padding: var(--space-sm) var(--space-md);
  border: none !important;
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: var(--text-sm);
  outline: none !important;
}

.search-input:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.timesheet-controls select {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-sm);
  border-radius: var(--radius);
}

.status-select {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 3px 4px;
  font-size: 11px;
  border-radius: 3px;
  width: 100px;
  min-width: 100px;
  max-width: 100px;
}

.timesheet-controls select:focus,
.status-select:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.btn {
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
}

.pdf-btn {
  background: var(--error);
}

.pdf-btn:hover {
  background: var(--error);
}

/* Timesheet Container - Interactive Scroll */
.timesheet-container {
  overflow: auto;
  position: relative;
  cursor: grab;
  user-select: none;
}

.timesheet-container::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.timesheet-container::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: var(--radius);
}

.timesheet-container::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: var(--radius);
}

.timesheet-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Timesheet Table */
.timesheet-table {
  width: max-content;
  min-width: 140rem;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.timesheet-table th {
  padding: var(--space-sm) var(--space-md);
  height: 3rem;
  text-align: center;
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  position: sticky;
  top: 0;
  width: 4rem;
  min-width: 4rem;
  max-width: 4rem;
  white-space: nowrap;
}

.timesheet-table th:first-child {
  text-align: left;
  width: 12rem;
  min-width: 12rem;
  max-width: 12rem;
  position: sticky;
  left: 0;
  background: var(--bg-primary);
  z-index: 10;
  border-right: 1px solid var(--border);
  box-shadow: 2px 0 4px -2px rgba(0, 0, 0, 0.1);
}

.timesheet-table td:first-child {
  position: sticky;
  left: 0;
  background: var(--bg-primary);
  z-index: 9;
  border-right: 1px solid var(--border);
  box-shadow: 2px 0 4px -2px rgba(0, 0, 0, 0.1);
  padding: var(--space-sm) var(--space-md);
}

.employee-name {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-sm);
  margin-bottom: 2px;
}

.employee-role {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-normal);
}

.timesheet-table tbody tr:nth-child(even) td:first-child {
  background: var(--bg-primary);
}

.timesheet-table th.weekend {
  background: rgba(239, 68, 68, 0.2);
  color: var(--error);
}

.timesheet-table tbody tr:nth-child(even) {
  background: transparent;
}

.timesheet-table tbody tr:nth-child(even) .timesheet-cell.weekend {
  background: rgba(239, 68, 68, 0.1);
}

.day-name {
  font-size: 11px;
  font-weight: var(--font-normal);
  color: var(--text-secondary);
  margin-top: var(--space-sm);
}

.timesheet-cell {
  padding: var(--space-sm) var(--space-sm);
  text-align: center;
  border-bottom: 1px solid var(--border);
  width: 8rem;
  min-width: 8rem;
  max-width: 8rem;
  vertical-align: middle;
  height: 3rem;
}

.timesheet-cell.weekend {
  background: rgba(239, 68, 68, 0.1);
}

.timesheet-cell:first-child {
  text-align: left;
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.time-input {
  width: 110px;
  min-width: 110px;
  border: none !important;
  border-radius: 3px;
  padding: 4px 6px;
  font-size: 12px;
  margin: 1px 0;
  text-align: center;
  background: var(--bg-secondary);
  color: var(--text-primary);
  outline: none !important;
}

.time-input:focus {
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.bonus-input {
  width: 100%;
  border: none !important;
  border-radius: 3px;
  padding: 2px 4px;
  font-size: 9px;
  margin: 1px 0;
  text-align: center;
  background: rgba(245, 158, 11, 0.1);
  color: var(--text-primary);
  -webkit-appearance: none;
  -moz-appearance: textfield;
  outline: none !important;
}

.bonus-input::-webkit-outer-spin-button,
.bonus-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.bonus-input:focus {
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.3);
}

.time-input:disabled,
.bonus-input:disabled {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: not-allowed;
}


.fixed-hours {
  font-size: 10px;
  color: var(--text-secondary);
  text-align: center;
  padding: var(--space-sm);
  font-weight: var(--font-semibold);
  height: 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.justified-check {
  display: flex;
  align-items: center;
  font-size: 8px;
  margin-top: 2px;
  color: var(--success);
}

.justified-check input[type="checkbox"] {
  width: 10px;
  height: 10px;
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: var(--space-lg);
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: stretch;
  }

  .timesheet-controls {
    justify-content: center;
  }
  
  .timesheet-table th {
    padding: var(--space-sm);
    font-size: 10px;
  }
  
  .timesheet-table th:first-child {
    width: 8rem;
    min-width: 8rem;
    max-width: 8rem;
  }
  
  .timesheet-cell {
    width: 6rem;
    min-width: 6rem;
    max-width: 6rem;
  }
}
</style>