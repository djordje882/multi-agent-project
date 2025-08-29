<template>
  <div>
    <div class="pdf-container">
      <div class="pdf-page" :class="getScaleClass()">
        <!-- Unified Payroll Template -->
        <div v-for="(employee, index) in filteredTimesheetEmployees" :key="employee.id" :class="{
          'payroll-employee': true,
          'current-employee': index === currentEmployeeIndex,
          'page-break': index > 0
        }">
          <div class="payroll-details">
            <div class="detail-row">
              <label>Site de Construction:</label>
              <span>{{ employee.construction_site }}</span>
            </div>
            <div class="detail-row">
              <label>Nom:</label>
              <span>{{ employee.name }} {{ employee.last_name }}</span>
            </div>
            <div class="detail-row">
              <label>Rôle:</label>
              <span>{{ employee.role }}</span>
            </div>
            <div class="detail-row">
              <label>Date de Paiement Initial:</label>
              <span>{{ getFirstDayOfMonth() }}</span>
            </div>
            <div class="detail-row">
              <label>Date de Paiement Final:</label>
              <span>{{ getLastDayOfMonth() }}</span>
            </div>

            <table class="hours-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Normales</th>
                  <th>Extra</th>
                  <th>Weekend</th>
                  <th>Vacances Travaillées</th>
                  <th>Vacances</th>
                  <th>Absence Justifiée</th>
                  <th>Maladie</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="dayInfo in getPayrollDays()" :key="dayInfo.date">
                  <td>{{ dayInfo.dayName }} {{ formatDate(dayInfo) }}</td>
                  <td v-for="hourType in hourTypes" :key="hourType">
                    {{ getHoursByType(dayInfo, hourType, index) }}
                  </td>
                </tr>
                <tr class="total-row">
                  <td><strong>Total</strong></td>
                  <td v-for="hourType in hourTypes" :key="hourType">
                    <strong>{{ getTotalHours(hourType, index) }}</strong>
                  </td>
                </tr>
                <tr class="salary-row">
                  <td><strong>Salaire par heure</strong></td>
                  <td v-for="hourType in hourTypes" :key="hourType">
                    <strong>{{ currencySymbol }} {{ getSalaryPerHour(hourType, index) }}</strong>
                  </td>
                </tr>
                <tr class="bonus-row">
                  <td><strong>Prime</strong></td>
                  <td colspan="6"></td>
                  <td><strong>{{ currencySymbol }} {{ getTotalBonus(index) }}</strong></td>
                </tr>
                <tr>
                  <td colspan="7"><strong>Allocation de voyage:</strong></td>
                  <td><strong>{{ currencySymbol }} {{ getTravelAllowance(index) }}</strong></td>
                </tr>
                <tr class="total-payments-row">
                  <td><strong>Paiements totaux</strong></td>
                  <td v-for="hourType in hourTypes" :key="hourType">
                    <strong>{{ currencySymbol }} {{ getTotalPayment(hourType, index) }}</strong>
                  </td>
                </tr>
                <tr class="for-payment-row">
                  <td><strong>À Payer:</strong></td>
                  <td colspan="6"></td>
                  <td><strong>{{ currencySymbol }} {{ getGrandTotal(index) }}</strong></td>
                </tr>
              </tbody>
            </table>

            <div class="signature-section">
              <div class="signature-item">
                <div class="signature-line"></div>
                <div class="signature-label">Signature de l'employé</div>
              </div>
              <div class="signature-item">
                <div class="signature-line"></div>
                <div class="signature-label">Signature de l'employeur</div>
              </div>
            </div>
          </div>
        </div>
        
        <button @click="prevEmployee" :disabled="currentEmployeeIndex === 0" class="nav-arrow left">‹</button>
        <button @click="nextEmployee" :disabled="currentEmployeeIndex === filteredTimesheetEmployees.length - 1" class="nav-arrow right">›</button>
      </div>
    </div>
    
    <div class="pdf-counter">
      {{ currentEmployeeIndex + 1 }} / {{ filteredTimesheetEmployees.length }}
    </div>
    
    <div class="pdf-controls">
      <div class="date-range-selector">
        <input type="date" v-model="fromDate" class="date-input">
        <span>à</span>
        <input type="date" v-model="toDate" class="date-input">
      </div>
      <button @click="printPayroll" class="btn print-btn">Imprimer</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, inject } from 'vue'
import { useTranslations } from '../composables/useTranslations'

export default {
  name: 'PDFView',
  props: {
    pdfData: Object
  },
  setup(props) {
    const { getCurrencySymbol } = useTranslations()
    const loading = inject('loading')
    const showMessage = inject('showMessage')
    const withLoading = inject('withLoading')
    
    const currentEmployeeIndex = ref(0)
    const fromDate = ref('')
    const toDate = ref('')
    const actualTimesheetData = ref({})
    
    const hourTypes = [
      'regular',
      'overtime', 
      'weekend',
      'holidayWorked',
      'holiday',
      'justified',
      'sick'
    ]
    const payrollEmployeeData = computed(() => {
      return {
        print: filteredTimesheetEmployees.value.map((employee, index) => ({
          employee,
          index
        }))
      }
    })
    const filteredTimesheetEmployees = computed(() => {
      const employees = props.pdfData?.employees || []
      if (!fromDate.value || !toDate.value) return employees
      
      return employees.filter(employee => {
        // Check if employee worked at least 1 day in selected period
        return getPayrollDays().some(day => {
          const inTime = getTimeEntry(employee.id, day.date, 'in', day.month, day.year)
          const outTime = getTimeEntry(employee.id, day.date, 'out', day.month, day.year)
          const status = getTimeEntry(employee.id, day.date, 'status', day.month, day.year)
          const verified = getTimeEntry(employee.id, day.date, 'verified', day.month, day.year)
          const bonus = getTimeEntry(employee.id, day.date, 'bonus', day.month, day.year)
          
          // Has work if: has time entries, or verified status, or bonus
          return (inTime && outTime) || 
                 (status === 'holiday') ||
                 (status === 'justified' && verified) ||
                 (status === 'sick' && verified) ||
                 (status === 'workholiday' && inTime && outTime) ||
                 bonus
        })
      })
    })
    const monthDays = computed(() => props.pdfData?.monthDays || [])
    const timesheetData = computed(() => props.pdfData?.timesheetData || {})
    const selectedYear = computed(() => props.pdfData?.selectedYear || new Date().getFullYear())
    const selectedMonth = computed(() => props.pdfData?.selectedMonth || new Date().getMonth() + 1)

    const currencySymbol = computed(() => getCurrencySymbol())

    const getFirstDayOfMonth = () => {
      return fromDate.value ? new Date(fromDate.value).toLocaleDateString('fr-FR') : new Date(selectedYear.value, selectedMonth.value - 1, 1).toLocaleDateString('fr-FR')
    }

    const getLastDayOfMonth = () => {
      return toDate.value ? new Date(toDate.value).toLocaleDateString('fr-FR') : new Date(selectedYear.value, selectedMonth.value, 0).toLocaleDateString('fr-FR')
    }

    const getPayrollDays = () => {
      if (!fromDate.value || !toDate.value) return monthDays.value
      
      const fromDateObj = new Date(fromDate.value)
      const toDateObj = new Date(toDate.value)
      const payrollDays = []
      
      // Generate days for the date range
      for (let d = new Date(fromDateObj); d <= toDateObj; d.setDate(d.getDate() + 1)) {
        const dayOfWeek = d.getDay()
        const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
        payrollDays.push({
          date: d.getDate(),
          month: d.getMonth() + 1,
          year: d.getFullYear(),
          dayName: dayNames[dayOfWeek],
          isWeekend: dayOfWeek === 0 || dayOfWeek === 6
        })
      }
      
      return payrollDays
    }

    const getOptimizedPayrollDays = (employeeIndex) => {
      const allDays = getPayrollDays()
      const employee = filteredTimesheetEmployees.value[employeeIndex]
      if (!employee) return allDays

      // For 15+ days, filter out days with no activity to save space
      if (allDays.length >= 15) {
        return allDays.filter(dayInfo => {
          const { date, month, year } = dayInfo
          const inTime = getTimeEntry(employee.id, date, 'in', month, year)
          const outTime = getTimeEntry(employee.id, date, 'out', month, year)
          const status = getTimeEntry(employee.id, date, 'status', month, year)
          const verified = getTimeEntry(employee.id, date, 'verified', month, year)
          const bonus = getTimeEntry(employee.id, date, 'bonus', month, year)
          
          // Include day if has any activity
          return (inTime && outTime) || 
                 (status === 'holiday') ||
                 (status === 'justified' && verified) ||
                 (status === 'sick' && verified) ||
                 (status === 'workholiday' && inTime && outTime) ||
                 bonus
        })
      }
      
      return allDays
    }

    const getScaleClass = () => {
      const dayCount = getPayrollDays().length
      if (dayCount >= 25) return 'scale-tiny'
      if (dayCount >= 20) return 'scale-small'
      if (dayCount >= 15) return 'scale-compact'
      return ''
    }

    const formatDate = (dayInfo) => {
      const month = dayInfo.month || selectedMonth.value
      return `${String(dayInfo.date || dayInfo).padStart(2, '0')}/${String(month).padStart(2, '0')}`
    }

    const loadTimesheetDataForRange = () => {
      if (!fromDate.value || !toDate.value) {
        actualTimesheetData.value = timesheetData.value
        return
      }
      
      const fromDateObj = new Date(fromDate.value)
      const toDateObj = new Date(toDate.value)
      const monthlyData = {}
      
      // Load data for each month in the range, keep separate by month
      for (let year = fromDateObj.getFullYear(); year <= toDateObj.getFullYear(); year++) {
        const startMonth = year === fromDateObj.getFullYear() ? fromDateObj.getMonth() + 1 : 1
        const endMonth = year === toDateObj.getFullYear() ? toDateObj.getMonth() + 1 : 12
        
        for (let month = startMonth; month <= endMonth; month++) {
          const storageKey = `timesheet-${year}-${month}`
          const saved = localStorage.getItem(storageKey)
          if (saved) {
            monthlyData[`${year}-${month}`] = JSON.parse(saved)
          }
        }
      }
      
      actualTimesheetData.value = monthlyData
    }

    const getTimeEntry = (employeeId, day, type, month, year) => {
      if (month && year) {
        const monthKey = `${year}-${month}`
        const dayKey = `${employeeId}-${day}-${type}`
        return actualTimesheetData.value[monthKey]?.[dayKey] || ''
      }
      
      // Fallback for original single-month data
      const key = `${employeeId}-${day}-${type}`
      return timesheetData.value[key] || ''
    }

    const calculateHours = (inTime, outTime) => {
      if (!inTime || !outTime) return 0
      const [inHours, inMinutes] = inTime.split(':').map(Number)
      const [outHours, outMinutes] = outTime.split(':').map(Number)
      const inTotalMinutes = inHours * 60 + inMinutes
      const outTotalMinutes = outHours * 60 + outMinutes
      return Math.max(0, (outTotalMinutes - inTotalMinutes) / 60)
    }

    const getHoursByType = (dayInfo, type, employeeIndex) => {
      const employee = filteredTimesheetEmployees.value[employeeIndex]
      if (!employee) return '0'
      
      const { date, isWeekend, month, year } = dayInfo
      const status = getTimeEntry(employee.id, date, 'status', month, year)
      const inTime = getTimeEntry(employee.id, date, 'in', month, year)
      const outTime = getTimeEntry(employee.id, date, 'out', month, year)
      const totalHours = calculateHours(inTime, outTime)
      const verified = getTimeEntry(employee.id, date, 'verified', month, year)
      
      // Only count explicit user entries, not default UI states
      if (status === 'holiday' && type === 'holiday') return '8'
      if (status === 'justified' && type === 'justified' && verified) return '8'
      if (status === 'sick' && type === 'sick' && verified) return '8'
      if (status === 'workholiday' && type === 'holidayWorked' && totalHours > 0) return totalHours.toFixed(1)
      
      // Weekend work only if actual time entries exist
      if (isWeekend && type === 'weekend' && totalHours > 0) return totalHours.toFixed(1)
      
      // Regular work only if time entries exist
      if (!isWeekend && totalHours > 0) {
        if (type === 'regular') return totalHours > 8 ? '8' : totalHours.toFixed(1)
        if (type === 'overtime') return totalHours > 8 ? (totalHours - 8).toFixed(1) : '0'
      }
      
      return '0'
    }

    const getTotalHours = (type, employeeIndex) => {
      let total = 0
      getPayrollDays().forEach(day => {
        const hours = parseFloat(getHoursByType(day, type, employeeIndex))
        total += hours
      })
      return total.toFixed(1)
    }

    const getSalaryPerHour = (type, employeeIndex) => {
      const employee = filteredTimesheetEmployees.value[employeeIndex]
      if (!employee) return '0.00'
      
      const baseRate = parseFloat(employee.hourly_rate || 0)
      if (type === 'overtime') return (baseRate * 1.5).toFixed(2)
      if (type === 'weekend') return (baseRate * 2).toFixed(2)
      return baseRate.toFixed(2)
    }

    const getTotalBonus = (employeeIndex) => {
      const employee = filteredTimesheetEmployees.value[employeeIndex]
      if (!employee) return '0.00'
      
      let total = 0
      getPayrollDays().forEach(day => {
        const bonus = parseFloat(getTimeEntry(employee.id, day.date, 'bonus', day.month, day.year) || 0)
        total += bonus
      })
      return total.toFixed(2)
    }

    const getTravelAllowance = (employeeIndex) => {
      if (!fromDate.value || !toDate.value) return '0.00'
      
      const fromDateObj = new Date(fromDate.value)
      const toDateObj = new Date(toDate.value)
      
      // Check if any day in range is last day of its month
      for (let d = new Date(fromDateObj); d <= toDateObj; d.setDate(d.getDate() + 1)) {
        const lastDayOfMonth = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate()
        if (d.getDate() === lastDayOfMonth) {
          const employee = filteredTimesheetEmployees.value[employeeIndex]
          if (!employee) return '0.00'
          return employee.role.toLowerCase().includes('aider') ? '70000.00' : '100000.00'
        }
      }
      
      return '0.00'
    }

    const getTotalPayment = (type, employeeIndex) => {
      const hours = parseFloat(getTotalHours(type, employeeIndex))
      const rate = parseFloat(getSalaryPerHour(type, employeeIndex))
      return (hours * rate).toFixed(2)
    }

    const roundPayment = (value) => {
      const r = Math.round(value) % 1000
      return Math.round(value) - r + (r <= 333 ? 0 : r <= 666 ? 500 : 1000)
    }

    const getGrandTotal = (employeeIndex) => {
      const regular = parseFloat(getTotalPayment('regular', employeeIndex))
      const overtime = parseFloat(getTotalPayment('overtime', employeeIndex))
      const weekend = parseFloat(getTotalPayment('weekend', employeeIndex))
      const holiday = parseFloat(getTotalPayment('holiday', employeeIndex))
      const holidayWorked = parseFloat(getTotalPayment('holidayWorked', employeeIndex))
      const justified = parseFloat(getTotalPayment('justified', employeeIndex))
      const sick = parseFloat(getTotalPayment('sick', employeeIndex))
      const bonus = parseFloat(getTotalBonus(employeeIndex))
      const travel = parseFloat(getTravelAllowance(employeeIndex))
      
      const total = regular + overtime + weekend + holiday + holidayWorked + justified + sick + bonus + travel
      return roundPayment(total).toFixed(2)
    }

    const prevEmployee = () => {
      if (currentEmployeeIndex.value > 0) {
        currentEmployeeIndex.value--
      }
    }

    const nextEmployee = () => {
      if (currentEmployeeIndex.value < filteredTimesheetEmployees.value.length - 1) {
        currentEmployeeIndex.value++
      }
    }

    watch(() => props.pdfData, () => {
      currentEmployeeIndex.value = 0
      // Set default date range to full month
      if (selectedYear.value && selectedMonth.value) {
        const year = selectedYear.value
        const month = selectedMonth.value
        fromDate.value = `${year}-${String(month).padStart(2, '0')}-01`
        const lastDay = new Date(year, month, 0).getDate()
        toDate.value = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
      }
      loadTimesheetDataForRange()
    }, { immediate: true })

    watch([fromDate, toDate], () => {
      loadTimesheetDataForRange()
    })

    const printPayroll = () => {
      window.print()
    }

    return {
      currentEmployeeIndex,
      fromDate,
      toDate,
      payrollEmployeeData,
      filteredTimesheetEmployees,
      monthDays,
      timesheetData,
      selectedYear,
      selectedMonth,
      hourTypes,
      currencySymbol,
      getFirstDayOfMonth,
      getLastDayOfMonth,
      getPayrollDays,
      getOptimizedPayrollDays,
      getScaleClass,
      formatDate,
      loadTimesheetDataForRange,
      getHoursByType,
      getTotalHours,
      getSalaryPerHour,
      getTotalBonus,
      getTravelAllowance,
      getTotalPayment,
      roundPayment,
      getGrandTotal,
      prevEmployee,
      nextEmployee,
      printPayroll
    }
  }
}
</script>

<style scoped>
/* PDF Generation Page */
.pdf-container {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.pdf-page {
  position: relative;
  max-width: 800px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--space-lg);
}

.nav-arrow {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 30px;
  background: transparent;
  color: var(--accent);
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-arrow.left {
  left: 0;
}

.nav-arrow.right {
  right: 0;
}

.nav-arrow:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.1);
  color: var(--accent-hover);
}

.nav-arrow:disabled {
  background: transparent;
  color: var(--text-secondary);
  cursor: not-allowed;
}

.pdf-counter {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.pdf-controls {
  text-align: center;
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 12px;
  align-items: center;
}


.date-range-selector {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.date-range-selector span {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.date-input {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-sm);
  border-radius: var(--radius);
  border: none;
}

.date-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.btn {
  padding: var(--space-sm) var(--space-lg);
  border: none;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  color: white;
}

.print-btn {
  background: var(--success);
}

.print-btn:hover {
  background: var(--success);
}

.payroll-details h3 {
  margin-bottom: 24px;
  color: var(--text-primary);
  text-align: center;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.detail-row label {
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
}

.detail-row span {
  color: var(--text-primary);
}

.hours-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 32px;
  font-size: 10px;
  table-layout: fixed;
}

.hours-table th {
  width: 12.5%;
}

.hours-table th,
.hours-table td {
  padding: 4px 6px;
  min-height: 38px;
  border-bottom: 1px solid var(--border);
  word-wrap: break-word;
  vertical-align: top;
}

.hours-table th {
  background: var(--bg-secondary);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  font-size: 11px;
  text-align: left;
}

.hours-table th:first-child,
.hours-table td:first-child {
  text-align: left;
}

.hours-table th:nth-child(n+2),
.hours-table td:nth-child(n+2) {
  text-align: right;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
}

.hours-table tbody tr:nth-child(even) {
  background: var(--bg-secondary);
}

.total-row {
  border-top: 2px solid var(--text-secondary);
}

.total-row td,
.salary-row td,
.bonus-row td,
.total-payments-row td,
.for-payment-row td {
  background: var(--bg-secondary);
}

.bonus-row td {
  color: var(--warning);
  font-weight: var(--font-semibold);
}

.signature-section {
  display: flex;
  justify-content: space-between;
  margin-top: 48px;
}

.signature-item {
  width: 200px;
}

.signature-line {
  border-bottom: 1px solid var(--text-primary);
  height: 1px;
  margin-bottom: 8px;
}

.signature-label {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.payroll-employee {
  display: none;
}

.payroll-employee.current-employee {
  display: block;
}

.page-break {
  page-break-before: always;
}

/* Print Styles */
@page {
  margin: 15mm 20mm;
  size: A4;
}

@media print {
  .payroll-employee {
    display: block !important;
  }
  
  body * {
    visibility: hidden;
  }
  
  .pdf-page, .pdf-page * {
    visibility: visible;
  }
  
  .pdf-page {
    position: static;
    width: 100%;
    margin: 0;
    padding: 0;
    box-shadow: none;
    border-radius: 0;
    font-size: 11px;
  }
  
  .pdf-page .detail-row {
    padding: 6px 0;
  }
  
  .pdf-page .hours-table {
    margin-top: 16px;
    font-size: 9px;
  }
  
  .pdf-page .hours-table th,
  .pdf-page .hours-table td {
    padding: 3px 4px;
    height: 28px;
  }
  
  .pdf-page .signature-section {
    margin-top: 24px;
  }
  
  .nav-arrow, .pdf-counter, .pdf-controls {
    display: none !important;
  }

  /* Dynamic scaling for large date ranges */
  .pdf-page.scale-compact .hours-table {
    font-size: 8px;
  }
  
  .pdf-page.scale-compact .hours-table th,
  .pdf-page.scale-compact .hours-table td {
    padding: 2px 3px;
    height: 22px;
  }

  .pdf-page.scale-small .hours-table {
    font-size: 7px;
  }
  
  .pdf-page.scale-small .hours-table th,
  .pdf-page.scale-small .hours-table td {
    padding: 1px 2px;
    height: 18px;
  }

  .pdf-page.scale-tiny .hours-table {
    font-size: 6px;
  }
  
  .pdf-page.scale-tiny .hours-table th,
  .pdf-page.scale-tiny .hours-table td {
    padding: 1px 1px;
    height: 15px;
  }
}
</style>