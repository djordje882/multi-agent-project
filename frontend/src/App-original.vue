<template>
  <div id="app">
    <!-- Header Navigation -->
    <header class="header">
      <div class="header-container">
        <div class="nav-brand">
          <h1>Gestion des Employés</h1>
        </div>
        <nav class="nav-menu" :class="{ 'active': menuOpen }">
          <a href="#" @click="showView('employees')" class="nav-link" :class="{ active: currentView === 'employees' }">Employés</a>
          <a href="#" @click="showView('sites')" class="nav-link" :class="{ active: currentView === 'sites' }">Sites</a>
          <a href="#" @click="showView('roles')" class="nav-link" :class="{ active: currentView === 'roles' }">Rôles</a>
          <a href="#" @click="showView('timesheet')" class="nav-link" :class="{ active: currentView === 'timesheet' }">Feuille de Temps</a>
          <a href="#" @click="showView('settings')" class="nav-link" :class="{ active: currentView === 'settings' }">Paramètres</a>
        </nav>
        <button class="hamburger" @click="toggleMenu" :class="{ 'active': menuOpen }">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Employee View -->
      <div v-if="currentView === 'employees'">
        <div class="content-header">
          <h2>Liste des Employés</h2>
          <div class="employee-controls">
            <input v-model="searchTerm" type="text" placeholder="Rechercher des employés..." class="search-input">
            <select v-model="sortBy" class="sort-select">
              <option value="name">Trier par Nom</option>
              <option value="construction_site">Trier par Site</option>
              <option value="hourly_rate">Trier par Taux</option>
              <option value="status">Trier par Statut</option>
            </select>
            <button @click="showAddEmployeeModal" class="btn add-btn">+ Ajouter Employé</button>
          </div>
        </div>

        <div class="table-container">
          <table class="employee-table">
            <thead>
              <tr>
                <th v-for="column in tableColumns" :key="column.key">{{ column.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentFilteredData" :key="item.id">
                <td v-for="column in tableColumns" :key="column.key" :class="column.class">
                  <template v-if="column.key === 'actions'">
                    <button @click="editCurrentItem(item)" class="action-btn edit-btn">Modifier</button>
                    <template v-if="currentView === 'employees'">
                      <button v-if="item.status === 'active'" @click="fireEmployee(item.id)" class="action-btn fire-btn">Licencier</button>
                      <button v-if="item.status === 'inactive'" @click="hireEmployee(item.id)" class="action-btn hire-btn">Embaucher</button>
                    </template>
                    <button @click="deleteCurrentItem(item.id)" class="action-btn delete-btn">Supprimer</button>
                  </template>
                  <template v-else-if="column.key === 'status'">
                    <span :class="['status-badge', item.status]">
                      {{ item.status }}
                    </span>
                  </template>
                  <template v-else-if="column.key === 'hourly_rate'">
                    {{ getCurrencySymbol() }} {{ item.hourly_rate }}
                  </template>
                  <template v-else>
                    {{ getColumnValue(item, column.key) }}
                  </template>
                </td>
              </tr>
              <tr v-if="currentFilteredData.length === 0">
                <td :colspan="tableColumns.length" class="no-data">{{ noDataMessage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Construction Sites View -->
      <div v-if="currentView === 'sites'">
        <div class="content-header">
          <h2>Sites de Construction</h2>
          <div class="site-controls">
            <input v-model="siteSearchTerm" type="text" placeholder="Rechercher des sites..." class="search-input">
            <select v-model="siteSortBy" class="sort-select">
              <option value="name">Trier par Nom</option>
              <option value="address">Trier par Adresse</option>
            </select>
            <button @click="showAddSiteModal" class="btn add-btn">+ Ajouter Site</button>
          </div>
        </div>

        <div class="table-container">
          <table class="employee-table">
            <thead>
              <tr>
                <th v-for="column in tableColumns" :key="column.key">{{ column.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentFilteredData" :key="item.id">
                <td v-for="column in tableColumns" :key="column.key" :class="column.class">
                  <template v-if="column.key === 'actions'">
                    <button @click="editCurrentItem(item)" class="action-btn edit-btn">Modifier</button>
                    <template v-if="currentView === 'employees'">
                      <button v-if="item.status === 'active'" @click="fireEmployee(item.id)" class="action-btn fire-btn">Licencier</button>
                      <button v-if="item.status === 'inactive'" @click="hireEmployee(item.id)" class="action-btn hire-btn">Embaucher</button>
                    </template>
                    <button @click="deleteCurrentItem(item.id)" class="action-btn delete-btn">Supprimer</button>
                  </template>
                  <template v-else-if="column.key === 'status'">
                    <span :class="['status-badge', item.status]">
                      {{ item.status }}
                    </span>
                  </template>
                  <template v-else-if="column.key === 'hourly_rate'">
                    {{ getCurrencySymbol() }} {{ item.hourly_rate }}
                  </template>
                  <template v-else>
                    {{ getColumnValue(item, column.key) }}
                  </template>
                </td>
              </tr>
              <tr v-if="currentFilteredData.length === 0">
                <td :colspan="tableColumns.length" class="no-data">{{ noDataMessage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Roles View -->
      <div v-if="currentView === 'roles'">
        <div class="content-header">
          <h2>Rôles</h2>
          <div class="site-controls">
            <input v-model="roleSearchTerm" type="text" placeholder="Rechercher des rôles..." class="search-input">
            <select v-model="roleSortBy" class="sort-select">
              <option value="name">Trier par Nom</option>
            </select>
            <button @click="showAddRoleModal" class="btn add-btn">+ Ajouter Rôle</button>
          </div>
        </div>

        <div class="table-container">
          <table class="employee-table">
            <thead>
              <tr>
                <th v-for="column in tableColumns" :key="column.key">{{ column.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentFilteredData" :key="item.id">
                <td v-for="column in tableColumns" :key="column.key" :class="column.class">
                  <template v-if="column.key === 'actions'">
                    <button @click="editCurrentItem(item)" class="action-btn edit-btn">Modifier</button>
                    <template v-if="currentView === 'employees'">
                      <button v-if="item.status === 'active'" @click="fireEmployee(item.id)" class="action-btn fire-btn">Licencier</button>
                      <button v-if="item.status === 'inactive'" @click="hireEmployee(item.id)" class="action-btn hire-btn">Embaucher</button>
                    </template>
                    <button @click="deleteCurrentItem(item.id)" class="action-btn delete-btn">Supprimer</button>
                  </template>
                  <template v-else-if="column.key === 'status'">
                    <span :class="['status-badge', item.status]">
                      {{ item.status }}
                    </span>
                  </template>
                  <template v-else-if="column.key === 'hourly_rate'">
                    {{ getCurrencySymbol() }} {{ item.hourly_rate }}
                  </template>
                  <template v-else>
                    {{ getColumnValue(item, column.key) }}
                  </template>
                </td>
              </tr>
              <tr v-if="currentFilteredData.length === 0">
                <td :colspan="tableColumns.length" class="no-data">{{ noDataMessage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Timesheet View -->
      <div v-if="currentView === 'timesheet'">
        <div class="content-header">
          <h2>Feuille de Temps</h2>
          <div class="timesheet-controls">
            <select v-model="selectedConstructionSite">
              <option value="">Tous les Sites de Construction</option>
              <option v-for="site in uniqueConstructionSites" :key="site" :value="site">
                {{ site }}
              </option>
            </select>
            <select v-model="selectedMonth" @change="loadTimesheet">
              <option v-for="month in 12" :key="month" :value="month">
                {{ getMonthName(month) }}
              </option>
            </select>
            <select v-model="selectedYear" @change="loadTimesheet">
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
                <th>Employee</th>
                <th v-for="dayInfo in monthDays" :key="dayInfo.date" :class="{ weekend: dayInfo.isWeekend }">
                  <div>{{ dayInfo.date }}</div>
                  <div class="day-name">{{ dayInfo.dayName }}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="employee in filteredTimesheetEmployees" :key="employee.id">
                <td class="name-cell">
                  <div class="employee-name">{{ employee.name }} {{ employee.last_name }}</div>
                  <div class="employee-role">{{ employee.role }}</div>
                </td>
                <td v-for="dayInfo in monthDays" :key="dayInfo.date" :class="['timesheet-cell', { weekend: dayInfo.isWeekend }]">
                  <template v-for="cellData in [timesheetCellData(employee, dayInfo)]" :key="'cell-data'">
                    <select class="status-select" :title="cellData.title" :disabled="cellData.isDisabled" :value="cellData.status" @change="setTimeEntry(employee.id, dayInfo.date, 'status', $event.target.value)">
                      <option value="">Normal</option>
                      <option value="weekend">Fin de Semaine</option>
                      <option value="holiday">Vacances</option>
                      <option value="workholiday">Travail pour les Vacances</option>
                      <option value="sick">Malade</option>
                      <option value="justified">Absence Justifiée</option>
                    </select>
                    <div v-if="cellData.status === 'holiday'" class="fixed-hours">8 heures</div>
                    <div v-else-if="cellData.status === 'justified' || cellData.status === 'sick'" class="fixed-hours">
                      8 heures
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
                <td :colspan="monthDays.length + 1" class="no-data">{{ timesheetEmployees.length === 0 ? 'Aucun employé actif trouvé' : 'Aucun employé trouvé pour le site sélectionné' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Settings View -->
      <div v-if="currentView === 'settings'">
        <div class="settings-container">
          <div class="setting-item">
            <label>Devise:</label>
            <select v-model="currentCurrency" @change="changeCurrency(currentCurrency)" class="setting-select">
              <option v-for="currency in currencies" :key="currency.code" :value="currency.code">
                {{ currency.code }} - {{ currency.name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- PDF Generation Page -->
      <div v-if="currentView === 'pdf'">
        <div class="pdf-container">
          <div class="pdf-page">
            <!-- Unified Payroll Template -->
            <div v-for="employeeData in payrollEmployeeData.print" :key="employeeData.employee.id" :class="{
              'payroll-employee': true,
              'current-employee': employeeData.index === currentEmployeeIndex,
              'page-break': employeeData.index > 0
            }">
              <div class="payroll-details">
                <div class="detail-row">
                  <label>Site de Construction:</label>
                  <span>{{ employeeData.employee.construction_site }}</span>
                </div>
                <div class="detail-row">
                  <label>Nom:</label>
                  <span>{{ employeeData.employee.name }} {{ employeeData.employee.last_name }}</span>
                </div>
                <div class="detail-row">
                  <label>Rôle:</label>
                  <span>{{ employeeData.employee.role }}</span>
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
                      <th>Jour / Date</th>
                      <th>Heures Normales</th>
                      <th>Heures Supplémentaires</th>
                      <th>Heures de Fin de Semaine</th>
                      <th>Heures de Vacances Travaillées</th>
                      <th>Heures de Vacances</th>
                      <th>Absence Justifiée</th>
                      <th>Heures de Maladie</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="dayInfo in getPayrollDays()" :key="dayInfo.date">
                      <td>{{ dayInfo.dayName }} {{ formatDate(dayInfo.date) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'regular', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'overtime', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'weekend', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'holidayWorked', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'holiday', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'justified', employeeData.index) }}</td>
                      <td>{{ getHoursByType(dayInfo.date, dayInfo.isWeekend, 'sick', employeeData.index) }}</td>
                    </tr>
                    <tr class="total-row">
                      <td><strong>Total</strong></td>
                      <td><strong>{{ getTotalHours('regular', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('overtime', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('weekend', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('holidayWorked', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('holiday', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('justified', employeeData.index) }}</strong></td>
                      <td><strong>{{ getTotalHours('sick', employeeData.index) }}</strong></td>
                    </tr>
                    <tr class="salary-row">
                      <td><strong>Salaire par heure</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('regular', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('overtime', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('weekend', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('holidayWorked', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('holiday', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('justified', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getSalaryPerHour('sick', employeeData.index) }}</strong></td>
                    </tr>
                    <tr class="bonus-row">
                      <td><strong>Prime</strong></td>
                      <td colspan="6"></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalBonus(employeeData.index) }}</strong></td>
                    </tr>
                    <tr>
                      <td colspan="7"><strong>Allocation de voyage:</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTravelAllowance(employeeData.index) }}</strong></td>
                    </tr>
                    <tr class="total-payments-row">
                      <td><strong>Paiements totaux</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('regular', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('overtime', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('weekend', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('holidayWorked', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('holiday', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('justified', employeeData.index) }}</strong></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getTotalPayment('sick', employeeData.index) }}</strong></td>
                    </tr>
                    <tr class="for-payment-row">
                      <td><strong>À Payer:</strong></td>
                      <td colspan="6"></td>
                      <td><strong>{{ getCurrencySymbol() }} {{ getGrandTotal(employeeData.index) }}</strong></td>
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
          <div class="period-selector">
            <select v-model="payrollPeriod">
              <option value="full">Mois Complet</option>
              <option value="first15">15 Premiers Jours</option>
              <option value="last15">15 Derniers Jours</option>
            </select>
          </div>
          <button @click="printPayroll" class="btn print-btn">Imprimer</button>
        </div>
      </div>
    </main>

    <!-- Unified Modal -->
    <div v-if="showModal || showSiteModal || showRoleModal" class="modal-overlay" @click="closeCurrentModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button @click="closeCurrentModal" class="close-btn">×</button>
        </div>
        <form @submit.prevent="saveCurrentEntity" class="modal-form">
          <!-- Employee Fields -->
          <template v-if="showModal">
            <div class="form-group">
              <label>Nom:</label>
              <input v-model="employeeForm.name" type="text" required maxlength="100">
            </div>
            <div class="form-group">
              <label>Nom de Famille:</label>
              <input v-model="employeeForm.last_name" type="text" required maxlength="100">
            </div>
            <div class="form-group">
              <label>Rôle:</label>
              <select v-model="employeeForm.role_id" required>
                <option value="" disabled>Sélectionner un rôle</option>
                <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Site de Construction:</label>
              <select v-model="employeeForm.construction_site_id" required>
                <option value="" disabled>Sélectionner un site</option>
                <option v-for="site in sites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Taux Horaire:</label>
              <input v-model="employeeForm.hourly_rate" type="number" required step="0.25" min="0">
            </div>
          </template>
          
          <!-- Site Fields -->
          <template v-if="showSiteModal">
            <div class="form-group">
              <label>Nom:</label>
              <input v-model="siteForm.name" type="text" required maxlength="200">
            </div>
            <div class="form-group">
              <label>Adresse:</label>
              <textarea v-model="siteForm.address" required maxlength="500" rows="3"></textarea>
            </div>
          </template>
          
          <!-- Role Fields -->
          <template v-if="showRoleModal">
            <div class="form-group">
              <label>Nom:</label>
              <input v-model="roleForm.name" type="text" required maxlength="100">
            </div>
          </template>
          
          <div class="modal-actions">
            <button type="button" @click="closeCurrentModal" class="cancel-btn">Annuler</button>
            <button type="submit" :disabled="loading" class="save-btn">
              {{ saveButtonText }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Message Toast -->
    <div v-if="message" class="toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = '/api'




const currencies = [
  { code: 'XAF', name: 'CFA Franc' },
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'JPY', name: 'Japanese Yen' },
  { code: 'CNY', name: 'Chinese Yuan' },
  { code: 'INR', name: 'Indian Rupee' },
  { code: 'BRL', name: 'Brazilian Real' },
  { code: 'RUB', name: 'Russian Ruble' },
  { code: 'CAD', name: 'Canadian Dollar' },
  { code: 'AUD', name: 'Australian Dollar' },
  { code: 'KRW', name: 'South Korean Won' },
  { code: 'MXN', name: 'Mexican Peso' },
  { code: 'CHF', name: 'Swiss Franc' }
]


export default {
  name: 'App',
  data() {
    return {
      loading: false,
      message: '',
      messageType: 'success',
      menuOpen: false,
      showModal: false,
      editingEmployee: null,
      employees: [],
      searchTerm: '',
      sortBy: 'name',
      employeeForm: { name: '', last_name: '', role_id: '', construction_site_id: '', hourly_rate: '' },
      sites: [],
      roles: [],
      siteSearchTerm: '',
      siteSortBy: 'name',
      showSiteModal: false,
      editingSite: null,
      siteForm: { name: '', address: '' },
      showRoleModal: false,
      editingRole: null,
      roleForm: { name: '' },
      roleSearchTerm: '',
      roleSortBy: 'name',
      currentView: 'employees',
      selectedYear: new Date().getFullYear(),
      selectedMonth: new Date().getMonth() + 1,
      selectedConstructionSite: '',
      timesheetEmployees: [],
      monthDays: [],
      timesheetData: {},
      currentEmployeeIndex: 0,
      payrollPeriod: 'full',
      currentCurrency: localStorage.getItem('currency') || 'XAF',
      isDragging: false,
      startX: 0,
      startY: 0
    }
  },
  
  computed: {
    currencies() {
      return currencies
    },

    modalTitle() {
      if (this.showModal) {
        return this.editingEmployee ? 'Modifier Employé' : 'Ajouter Employé'
      }
      if (this.showSiteModal) {
        return this.editingSite ? 'Modifier Site de Construction' : 'Ajouter Site de Construction'
      }
      if (this.showRoleModal) {
        return this.editingRole ? 'Modifier Rôle' : 'Ajouter Rôle'
      }
      return ''
    },

    saveButtonText() {
      if (this.showModal) {
        return this.editingEmployee ? 'Mettre à Jour' : 'Créer'
      }
      if (this.showSiteModal) {
        return this.editingSite ? 'Mettre à Jour' : 'Créer'
      }
      if (this.showRoleModal) {
        return this.editingRole ? 'Mettre à Jour' : 'Créer'
      }
      return 'Créer'
    },

    tableColumns() {
      if (this.currentView === 'employees') {
        return [
          { key: 'name', label: 'Nom', class: 'name-cell' },
          { key: 'last_name', label: 'Nom de Famille', class: 'name-cell' },
          { key: 'role', label: 'Rôle', class: 'role-cell' },
          { key: 'construction_site', label: 'Site de Construction' },
          { key: 'hourly_rate', label: 'Taux Horaire', class: 'rate-cell' },
          { key: 'status', label: 'Statut' },
          { key: 'actions', label: 'Actions', class: 'actions-cell' }
        ]
      }
      if (this.currentView === 'sites') {
        return [
          { key: 'name', label: 'Nom', class: 'name-cell' },
          { key: 'address', label: 'Adresse' },
          { key: 'actions', label: 'Actions', class: 'actions-cell' }
        ]
      }
      if (this.currentView === 'roles') {
        return [
          { key: 'name', label: 'Nom', class: 'name-cell' },
          { key: 'actions', label: 'Actions', class: 'actions-cell' }
        ]
      }
      return []
    },

    currentFilteredData() {
      if (this.currentView === 'employees') return this.filteredEmployees
      if (this.currentView === 'sites') return this.filteredSites
      if (this.currentView === 'roles') return this.filteredRoles
      return []
    },

    noDataMessage() {
      if (this.currentView === 'employees') {
        return this.employees.length === 0 ? 'Aucun employé trouvé' : 'Aucun employé ne correspond à votre recherche'
      }
      if (this.currentView === 'sites') {
        return this.sites.length === 0 ? 'Aucun site trouvé' : 'Aucun site ne correspond à votre recherche'
      }
      if (this.currentView === 'roles') {
        return this.roles.length === 0 ? 'Aucun rôle trouvé' : 'Aucun rôle ne correspond à votre recherche'
      }
      return ''
    },

    filteredEmployees() {
      let filtered = this.employees.filter(emp => {
        if (!this.searchTerm) return true
        const term = this.searchTerm.toLowerCase()
        return emp.name.toLowerCase().includes(term) ||
               emp.last_name.toLowerCase().includes(term) ||
               (emp.role || '').toLowerCase().includes(term) ||
               (emp.construction_site || '').toLowerCase().includes(term)
      })
      
      if (this.sortBy === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name))
      if (this.sortBy === 'hourly_rate') filtered.sort((a, b) => b.hourly_rate - a.hourly_rate)
      if (this.sortBy === 'construction_site') filtered.sort((a, b) => (a.construction_site || '').localeCompare(b.construction_site || ''))
      if (this.sortBy === 'status') filtered.sort((a, b) => a.status.localeCompare(b.status))
      
      return filtered
    },

    filteredSites() {
      let filtered = this.sites.filter(site => {
        if (!this.siteSearchTerm) return true
        const term = this.siteSearchTerm.toLowerCase()
        return site.name.toLowerCase().includes(term) ||
               site.address.toLowerCase().includes(term)
      })
      
      if (this.siteSortBy === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name))
      if (this.siteSortBy === 'address') filtered.sort((a, b) => a.address.localeCompare(b.address))
      
      return filtered
    },

    filteredRoles() {
      let filtered = this.roles.filter(role => {
        if (!this.roleSearchTerm) return true
        return role.name.toLowerCase().includes(this.roleSearchTerm.toLowerCase())
      })
      
      if (this.roleSortBy === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name))
      
      return filtered
    },

    uniqueConstructionSites() {
      const sites = [...new Set(this.timesheetEmployees.map(emp => emp.construction_site).filter(site => site))]
      return sites.sort()
    },

    filteredTimesheetEmployees() {
      if (!this.selectedConstructionSite) {
        return this.timesheetEmployees
      }
      return this.timesheetEmployees.filter(emp => emp.construction_site === this.selectedConstructionSite)
    },

    payrollEmployeeData() {
      const screenData = this.filteredTimesheetEmployees[this.currentEmployeeIndex]
      return {
        screen: screenData ? [{ employee: screenData, index: this.currentEmployeeIndex }] : [],
        print: this.filteredTimesheetEmployees.map((employee, index) => ({ employee, index }))
      }
    },


    timesheetCellData() {
      return (employee, dayInfo) => {
        const status = this.getTimeEntry(employee.id, dayInfo.date, 'status')
        const isDisabled = this.isInputDisabled(employee, dayInfo.date)
        return {
          status: status || (dayInfo.isWeekend ? 'weekend' : ''),
          title: status || (dayInfo.isWeekend ? 'weekend' : 'regular'),
          isDisabled,
          inTime: this.getTimeEntry(employee.id, dayInfo.date, 'in'),
          outTime: this.getTimeEntry(employee.id, dayInfo.date, 'out'),
          bonus: this.getTimeEntry(employee.id, dayInfo.date, 'bonus'),
          verified: this.getTimeEntry(employee.id, dayInfo.date, 'verified')
        }
      }
    }
  },
  
  async mounted() {
    await this.loadEmployees()
    await this.loadSites()
    await this.loadRoles()
  },
  
  methods: {
    closeCurrentModal() {
      if (this.showModal) {
        this.closeEmployeeModal()
      } else if (this.showSiteModal) {
        this.closeSiteModal()
      } else if (this.showRoleModal) {
        this.closeRoleModal()
      }
    },

    saveCurrentEntity() {
      if (this.showModal) {
        this.saveEmployee()
      } else if (this.showSiteModal) {
        this.saveSite()
      } else if (this.showRoleModal) {
        this.saveRole()
      }
    },

    editCurrentItem(item) {
      if (this.currentView === 'employees') {
        this.editEmployee(item)
      } else if (this.currentView === 'sites') {
        this.editSite(item)
      } else if (this.currentView === 'roles') {
        this.editRole(item)
      }
    },

    deleteCurrentItem(id) {
      if (this.currentView === 'employees') {
        this.deleteEmployee(id)
      } else if (this.currentView === 'sites') {
        this.deleteSite(id)
      } else if (this.currentView === 'roles') {
        this.deleteRole(id)
      }
    },

    getColumnValue(item, key) {
      if (key === 'construction_site') {
        return item.construction_site || '-'
      }
      return item[key] || ''
    },

    getCurrencySymbol() {
      const symbols = {
        XAF: 'FCFA',
        USD: '$',
        EUR: '€',
        GBP: '£',
        JPY: '¥',
        CNY: '¥',
        INR: '₹',
        BRL: 'R$',
        RUB: '₽',
        CAD: 'C$',
        AUD: 'A$',
        KRW: '₩',
        MXN: '$',
        CHF: 'CHF'
      }
      return symbols[this.currentCurrency] || this.currentCurrency
    },

    changeCurrency(currency) {
      this.currentCurrency = currency
      localStorage.setItem('currency', currency)
    },

    async loadEmployees() {
      await this.withLoading(async () => {
        try {
          const response = await axios.get(`${API_BASE}/employees`)
          this.employees = response.data
        } catch (error) {
          this.showMessage('Erreur lors du chargement des employés: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },

    showView(view) {
      this.currentView = view
      this.menuOpen = false
      if (view === 'timesheet') {
        this.loadTimesheet()
      }
    },



    async fireEmployee(employeeId) {
      const fireDate = prompt('Enter fire date (YYYY-MM-DD):')
      if (!fireDate || !confirm('Êtes-vous sûr de vouloir licencier cet employé?')) {
        return
      }

      await this.withLoading(async () => {
        try {
          const response = await axios.put(`${API_BASE}/employees/${employeeId}/fire`, { fire_date: fireDate })
          this.showMessage(response.data.message, 'success')
          await this.loadEmployees()
        } catch (error) {
          this.showMessage('Error firing employee: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async hireEmployee(employeeId) {
      if (!confirm('Êtes-vous sûr de vouloir embaucher cet employé? Il sera marqué comme actif.')) {
        return
      }

      await this.withLoading(async () => {
        try {
          const response = await axios.put(`${API_BASE}/employees/${employeeId}/hire`)
          this.showMessage(response.data.message, 'success')
          await this.loadEmployees()
        } catch (error) {
          this.showMessage('Error hiring employee: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => this.clearMessage(), 3000)
    },
    
    clearMessage() {
      this.message = ''
    },

    // Generic async wrapper to eliminate loading state repetition
    async withLoading(asyncOperation) {
      this.loading = true
      try {
        return await asyncOperation()
      } finally {
        this.loading = false
      }
    },

    // Employee Methods
    showAddEmployeeModal() {
      this.editingEmployee = null
      this.employeeForm = { name: '', last_name: '', role_id: '', construction_site_id: '', hourly_rate: '' }
      this.showModal = true
    },

    editEmployee(employee) {
      this.editingEmployee = employee
      this.employeeForm = { ...employee }
      this.showModal = true
    },

    closeEmployeeModal() {
      this.showModal = false
      this.editingEmployee = null
      this.employeeForm = { name: '', last_name: '', role_id: '', construction_site_id: '', hourly_rate: '' }
    },

    async saveEmployee() {
      await this.withLoading(async () => {
        try {
          const payload = {
            ...this.employeeForm,
            role_id: parseInt(this.employeeForm.role_id),
            construction_site_id: parseInt(this.employeeForm.construction_site_id),
            hourly_rate: parseFloat(this.employeeForm.hourly_rate)
          }
          
          if (this.editingEmployee) {
            const response = await axios.put(`${API_BASE}/employees/${this.editingEmployee.id}`, payload)
            this.showMessage(response.data.message, 'success')
          } else {
            const response = await axios.post(`${API_BASE}/employees`, payload)
            this.showMessage(response.data.message, 'success')
          }
          
          this.closeEmployeeModal()
          await this.loadEmployees()
        } catch (error) {
          this.showMessage('Erreur lors de la sauvegarde de l\'employé: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async deleteEmployee(id) {
      if (!confirm('Êtes-vous sûr de vouloir supprimer cet employé? Cette action ne peut pas être annulée.')) {
        return
      }
      await this.withLoading(async () => {
        try {
          const response = await axios.delete(`${API_BASE}/employees/${id}`)
          this.showMessage(response.data.message, 'success')
          await this.loadEmployees()
        } catch (error) {
          this.showMessage('Erreur lors de la suppression de l\'employé: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    // Site Methods
    showAddSiteModal() {
      this.editingSite = null
      this.siteForm = { name: '', address: '' }
      this.showSiteModal = true
    },

    editSite(site) {
      this.editingSite = site
      this.siteForm = { ...site }
      this.showSiteModal = true
    },

    closeSiteModal() {
      this.showSiteModal = false
      this.editingSite = null
      this.siteForm = { name: '', address: '' }
    },

    async saveSite() {
      await this.withLoading(async () => {
        try {
          if (this.editingSite) {
            const response = await axios.put(`${API_BASE}/construction-sites/${this.editingSite.id}`, this.siteForm)
            this.showMessage(response.data.message, 'success')
          } else {
            const response = await axios.post(`${API_BASE}/construction-sites`, this.siteForm)
            this.showMessage(response.data.message, 'success')
          }
          
          this.closeSiteModal()
          await this.loadSites()
        } catch (error) {
          this.showMessage('Erreur lors de la sauvegarde du site: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async deleteSite(id) {
      if (!confirm('Êtes-vous sûr de vouloir supprimer ce site? Cette action ne peut pas être annulée.')) {
        return
      }
      await this.withLoading(async () => {
        try {
          const response = await axios.delete(`${API_BASE}/construction-sites/${id}`)
          this.showMessage(response.data.message, 'success')
          await this.loadSites()
        } catch (error) {
          this.showMessage('Erreur lors de la suppression du site: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    // Role Methods
    showAddRoleModal() {
      this.editingRole = null
      this.roleForm = { name: '' }
      this.showRoleModal = true
    },

    editRole(role) {
      this.editingRole = role
      this.roleForm = { ...role }
      this.showRoleModal = true
    },

    closeRoleModal() {
      this.showRoleModal = false
      this.editingRole = null
      this.roleForm = { name: '' }
    },

    async saveRole() {
      await this.withLoading(async () => {
        try {
          if (this.editingRole) {
            const response = await axios.put(`${API_BASE}/roles/${this.editingRole.id}`, this.roleForm)
            this.showMessage(response.data.message, 'success')
          } else {
            const response = await axios.post(`${API_BASE}/roles`, this.roleForm)
            this.showMessage(response.data.message, 'success')
          }
          
          this.closeRoleModal()
          await this.loadRoles()
        } catch (error) {
          this.showMessage('Erreur lors de la sauvegarde du rôle: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async deleteRole(id) {
      if (!confirm('Êtes-vous sûr de vouloir supprimer ce rôle? Cette action ne peut pas être annulée.')) {
        return
      }
      await this.withLoading(async () => {
        try {
          const response = await axios.delete(`${API_BASE}/roles/${id}`)
          this.showMessage(response.data.message, 'success')
          await this.loadRoles()
        } catch (error) {
          this.showMessage('Erreur lors de la suppression du rôle: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async loadTimesheet() {
      this.loading = true
      try {
        const response = await axios.get(`${API_BASE}/employees`)
        const currentDate = new Date(this.selectedYear, this.selectedMonth - 1, 1)
        
        this.timesheetEmployees = response.data.filter(emp => {
          if (emp.status === 'active') return true
          if (emp.status === 'inactive' && emp.fire_date) {
            const fireDate = new Date(emp.fire_date)
            return currentDate <= fireDate
          }
          return false
        })
        
        this.generateMonthDays()
        this.clearTimesheetData()
      } catch (error) {
        this.showMessage('Erreur lors du chargement de la feuille de temps: ' + (error.response?.data?.detail || error.message), 'error')
      } finally {
        this.loading = false
      }
    },

    generateMonthDays() {
      const daysInMonth = new Date(this.selectedYear, this.selectedMonth, 0).getDate()
      const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
      
      this.monthDays = Array.from({length: daysInMonth}, (_, i) => {
        const date = i + 1
        const dayOfWeek = new Date(this.selectedYear, this.selectedMonth - 1, date).getDay()
        return {
          date,
          dayName: dayNames[dayOfWeek],
          isWeekend: dayOfWeek === 0 || dayOfWeek === 6
        }
      })
    },

    getMonthName(month) {
      const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
      return months[month - 1]
    },

    getYearOptions() {
      const currentYear = new Date().getFullYear()
      return Array.from({length: 5}, (_, i) => currentYear - 2 + i)
    },

    generatePDF() {
      if (this.filteredTimesheetEmployees.length === 0) {
        this.showMessage('Aucun employé pour générer le PDF', 'error')
        return
      }
      this.currentEmployeeIndex = 0
      this.currentView = 'pdf'
    },

    prevEmployee() {
      if (this.currentEmployeeIndex > 0) {
        this.currentEmployeeIndex--
      }
    },

    nextEmployee() {
      if (this.currentEmployeeIndex < this.filteredTimesheetEmployees.length - 1) {
        this.currentEmployeeIndex++
      }
    },

    getFirstDayOfMonth() {
      if (this.payrollPeriod === 'last15') {
        return `${this.selectedYear}-${String(this.selectedMonth).padStart(2, '0')}-16`
      }
      return `${this.selectedYear}-${String(this.selectedMonth).padStart(2, '0')}-01`
    },

    getLastDayOfMonth() {
      if (this.payrollPeriod === 'first15') {
        return `${this.selectedYear}-${String(this.selectedMonth).padStart(2, '0')}-15`
      }
      const lastDay = new Date(this.selectedYear, this.selectedMonth, 0).getDate()
      return `${this.selectedYear}-${String(this.selectedMonth).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    },

    formatDate(day) {
      return `${this.selectedYear}-${String(this.selectedMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    },

    getHoursByType(day, isWeekend, type, employeeIndex = this.currentEmployeeIndex) {
      const employee = this.filteredTimesheetEmployees[employeeIndex]
      const inTime = this.getTimeEntry(employee.id, day, 'in')
      const outTime = this.getTimeEntry(employee.id, day, 'out')
      const status = this.getTimeEntry(employee.id, day, 'status')
      
      const totalHours = (inTime && outTime) ? this.calculateHours(inTime, outTime) : 0
      
      const verified = this.getTimeEntry(employee.id, day, 'verified')
      
      switch(type) {
        case 'regular': return (!isWeekend && status !== 'holiday' && status !== 'workholiday' && totalHours > 0) ? Math.min(totalHours, 8).toFixed(1) : '0'
        case 'overtime': return (!isWeekend && status !== 'holiday' && status !== 'workholiday' && totalHours > 8) ? (totalHours - 8).toFixed(1) : '0'
        case 'weekend': return (isWeekend && totalHours > 0) ? totalHours.toFixed(1) : '0'
        case 'holidayWorked': return (status === 'workholiday' && totalHours > 0) ? totalHours.toFixed(1) : '0'
        case 'holiday': return (status === 'holiday') ? '8.0' : '0'
        case 'justified': return (status === 'justified' && verified) ? '8.0' : '0'
        case 'sick': return (status === 'sick' && verified) ? '8.0' : '0'
        default: return '0'
      }
    },

    calculateHours(inTime, outTime) {
      const [inHour, inMin] = inTime.split(':').map(Number)
      const [outHour, outMin] = outTime.split(':').map(Number)
      const inMinutes = inHour * 60 + inMin
      const outMinutes = outHour * 60 + outMin
      return (outMinutes - inMinutes) / 60
    },

    getTotalHours(type, employeeIndex = this.currentEmployeeIndex) {
      let total = 0
      this.getPayrollDays().forEach(dayInfo => {
        const hours = parseFloat(this.getHoursByType(dayInfo.date, dayInfo.isWeekend, type, employeeIndex))
        total += hours
      })
      return total.toFixed(1)
    },

    getPayrollDays() {
      if (this.payrollPeriod === 'first15') {
        return this.monthDays.filter(day => day.date <= 15)
      } else if (this.payrollPeriod === 'last15') {
        return this.monthDays.filter(day => day.date > 15)
      }
      return this.monthDays
    },

    getSalaryPerHour(type, employeeIndex = this.currentEmployeeIndex) {
      const employee = this.filteredTimesheetEmployees[employeeIndex]
      const baseRate = parseFloat(employee.hourly_rate)
      
      switch(type) {
        case 'regular': return baseRate.toFixed(2)
        case 'overtime': return (baseRate * 1.15).toFixed(2)
        case 'weekend': return (baseRate * 1.5).toFixed(2)
        case 'holidayWorked': return (baseRate * 2).toFixed(2)
        case 'holiday': return baseRate.toFixed(2)
        case 'justified': return baseRate.toFixed(2)
        case 'sick': return baseRate.toFixed(2)
        default: return '0.00'
      }
    },

    getTotalPayment(type, employeeIndex = this.currentEmployeeIndex) {
      const totalHours = parseFloat(this.getTotalHours(type, employeeIndex))
      const salaryPerHour = parseFloat(this.getSalaryPerHour(type, employeeIndex))
      return (totalHours * salaryPerHour).toFixed(2)
    },

    getTotalBonus(employeeIndex = this.currentEmployeeIndex) {
      let totalBonus = 0
      this.getPayrollDays().forEach(dayInfo => {
        const dailyBonus = parseFloat(this.getTimeEntry(this.filteredTimesheetEmployees[employeeIndex].id, dayInfo.date, 'bonus') || 0)
        totalBonus += dailyBonus
      })
      return totalBonus.toFixed(2)
    },

    getTravelAllowance(employeeIndex = this.currentEmployeeIndex) {
      if (this.payrollPeriod === 'first15') return '0.00'
      
      const employee = this.filteredTimesheetEmployees[employeeIndex]
      if (!employee) return '0.00'
      
      const role = employee.role.toLowerCase()
      const amount = (role === 'aide' || role.startsWith('aide')) ? 70000 : 100000
      return amount.toFixed(2)
    },

    getGrandTotal(employeeIndex = this.currentEmployeeIndex) {
      const types = ['regular', 'overtime', 'weekend', 'holidayWorked', 'holiday', 'justified', 'sick']
      let total = 0
      types.forEach(type => {
        total += parseFloat(this.getTotalPayment(type, employeeIndex))
      })
      total += parseFloat(this.getTotalBonus(employeeIndex))
      total += parseFloat(this.getTravelAllowance(employeeIndex))
      return total.toFixed(2)
    },

    clearTimesheetData() {
      this.timesheetData = {}
      this.loadTimesheetData()
    },

    saveTimesheetData() {
      const storageKey = `timesheet-${this.selectedYear}-${this.selectedMonth}`
      localStorage.setItem(storageKey, JSON.stringify(this.timesheetData))
    },

    loadTimesheetData() {
      const storageKey = `timesheet-${this.selectedYear}-${this.selectedMonth}`
      const saved = localStorage.getItem(storageKey)
      this.timesheetData = saved ? JSON.parse(saved) : {}
    },

    getTimeEntry(employeeId, day, type) {
      const key = `${employeeId}-${day}-${type}`
      if (type === 'verified') {
        return this.timesheetData[key] === true
      }
      return this.timesheetData[key] || ''
    },

    setTimeEntry(employeeId, day, type, value) {
      const key = `${employeeId}-${day}-${type}`
      this.timesheetData[key] = value
      this.saveTimesheetData()
    },

    clearTimeEntry(employeeId, day, type) {
      const key = `${employeeId}-${day}-${type}`
      this.timesheetData[key] = ''
      this.saveTimesheetData()
    },

    isInputDisabled(employee, day) {
      const currentDay = new Date(this.selectedYear, this.selectedMonth - 1, day)
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
    },

    printPayroll() {
      window.print()
    },

    // Construction Sites methods
    async loadSites() {
      await this.withLoading(async () => {
        try {
          const response = await axios.get(`${API_BASE}/construction-sites`)
          this.sites = response.data
        } catch (error) {
          this.showMessage('Erreur lors du chargement des sites: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    },

    async loadRoles() {
      try {
        const response = await axios.get(`${API_BASE}/roles`)
        this.roles = response.data
      } catch (error) {
        console.error('Erreur lors du chargement des rôles:', error)
        this.showMessage('Erreur lors du chargement des rôles', 'error')
      }
    },



    startDrag(e) {
      const container = this.$refs.timesheetContainer
      if (!container) return
      
      this.isDragging = true
      this.startX = e.pageX + container.scrollLeft
      this.startY = e.pageY + container.scrollTop
      
      const handleMouseMove = (e) => {
        if (!this.isDragging) return
        e.preventDefault()
        container.scrollLeft = this.startX - e.pageX
        container.scrollTop = this.startY - e.pageY
      }
      
      const handleMouseUp = () => {
        this.isDragging = false
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
        container.style.cursor = 'default'
      }
      
      container.style.cursor = 'grabbing'
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    },

    handleWheel(e) {
      if (!e.shiftKey) return
      
      e.preventDefault()
      const container = this.$refs.timesheetContainer
      if (!container) return
      
      container.scrollLeft += e.deltaY
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* Essential Colors (8 variables) */
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

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Micro-interactions & Animations */

.modal {
}

.table-container {
}

.nav-menu.active {
}

/* Header Navigation */
.header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
  position: relative;
}

.nav-brand h1 {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.nav-menu {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--bg-secondary);
  flex-direction: column;
  padding: var(--space-lg) var(--space-lg);
  box-shadow: var(--shadow);
  border-radius: var(--radius-lg);
  min-width: 10rem;
  border: 1px solid var(--border);
}

.nav-menu.active {
  display: flex;
  gap: var(--space-sm);
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  padding: var(--space-sm) 0;
  border-radius: var(--radius);
}

.nav-link:hover {
  color: var(--accent);
}

.nav-link.active {
  color: var(--accent);
  font-weight: var(--font-semibold);
}

/* Main Content */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-lg) var(--space-lg);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  gap: var(--space-lg);
}

.content-header h2 {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

/* Settings Page */
.settings-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow);
  max-width: 800px;
  margin: 0 auto;
  margin-top: var(--space-lg);
}

.setting-item {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-lg) var(--space-lg);
  border-bottom: 1px solid var(--border);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item label {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-lg);
  text-align: left;
}

.setting-select {
  padding: var(--space-md) var(--space-lg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--text-base);
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  min-width: 200px;
}

.setting-select:hover {
  border-color: var(--accent-hover);
}

.setting-select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.hamburger {
  display: flex;
  flex-direction: column;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-sm);
}

.hamburger span {
  width: 20px;
  height: 2px;
  background: var(--text-primary);
  margin: var(--space-sm) 0;
}

/* Main Content */

/* Form Controls */
.employee-controls,
.site-controls {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.search-input {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  min-width: 12rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.search-input:hover {
  border-color: var(--accent-hover);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.sort-select {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.sort-select:hover {
  border-color: var(--accent-hover);
}

.sort-select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}


/* Base Button */
.btn {
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
}

.btn:hover {
}

.add-btn {
  background: var(--accent);
}

.add-btn:hover {
  background: var(--accent-hover);
}

/* Timesheet Controls */
.timesheet-controls {
  display: flex;
  gap: 12px;
}

.timesheet-controls select {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid rgba(224, 224, 224, 0.3) !important;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  background: var(--bg-secondary);
  color: var(--text-primary);
  box-sizing: border-box;
}

.pdf-btn {
  background: var(--error);
}

.pdf-btn:hover {
  background: var(--error);
}

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
  color: var(--text-tertiary);
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

.period-selector select {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  background: var(--bg-secondary);
  color: var(--text-primary);
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

.hours-table th,
.hours-table td {
  padding: 4px 6px;
  height: 32px;
  border-bottom: 1px solid var(--border);
  word-wrap: break-word;
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
  background: var(--text-tertiary);
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
  color: var(--text-tertiary);
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
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 4px 6px;
  font-size: 12px;
  margin: 1px 0;
  text-align: center;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.time-input:focus {
  outline: none;
  border-color: var(--accent);
}

.bonus-input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 2px 4px;
  font-size: 9px;
  margin: 1px 0;
  text-align: center;
  background: rgba(245, 158, 11, 0.1);
  color: var(--text-primary);
  -webkit-appearance: none;
  -moz-appearance: textfield;
}

.bonus-input::-webkit-outer-spin-button,
.bonus-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.bonus-input:focus {
  outline: none;
  border-color: var(--warning);
}

.time-input:disabled,
.status-select:disabled,
.bonus-input:disabled {
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.status-select {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 3px 4px;
  font-size: 11px;
  margin: 1px 0;
  background: var(--bg-secondary);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-select:focus {
  outline: none;
  border-color: var(--accent);
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
  margin-right: 2px;
}

/* Employee Table */
/* Table Containers */
.table-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.employee-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.employee-table thead {
  background: var(--bg-secondary);
}

.employee-table th {
  padding: var(--space-md) var(--space-lg);
  height: 3rem;
  text-align: left;
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--bg-secondary);
}

.employee-table th:nth-child(5) {
  text-align: right;
}

.employee-table td {
  padding: var(--space-md) var(--space-lg);
  height: 3.5rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
  color: var(--text-primary);
}

.employee-table tbody tr:nth-child(even) {
  background: var(--bg-secondary);
}

.employee-table tr:hover {
  background: rgba(139, 92, 246, 0.1);
  transition: background-color 0.15s ease;
}

.name-cell {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.rate-cell {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  font-weight: var(--font-semibold);
  color: var(--success);
  text-align: right;
}

.status-badge {
  padding: var(--space-sm) var(--space-md);
  border-radius: 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
}

.status-badge.active {
  background: var(--success-50);
  color: var(--success);
}

.status-badge.inactive {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.role-cell {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  gap: 8px;
  white-space: nowrap;
}

.action-btn {
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  text-transform: uppercase;
  min-width: 60px;
  letter-spacing: 0.025em;
}

.edit-btn {
  background: var(--accent);
  color: white;
}

.edit-btn:hover {
  background: var(--accent-hover);
}

.fire-btn {
  background: var(--warning);
  color: white;
}

.fire-btn:hover {
  background: var(--warning);
}

.hire-btn {
  background: var(--success);
  color: white;
}

.hire-btn:hover {
  background: var(--success);
}

.delete-btn {
  background: var(--error);
  color: white;
}

.delete-btn:hover {
  background: var(--error);
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: var(--space-lg);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg) var(--space-lg) var(--space-lg);
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: var(--space-sm);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--error);
}

.modal-form {
  padding: var(--space-lg);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: var(--space-md);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-family: inherit;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.form-group select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.form-group input:hover,
.form-group textarea:hover,
.form-group select:hover {
  border-color: var(--accent-hover);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}


.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  cursor: pointer;
  font-weight: var(--font-semibold);
}

.cancel-btn:hover {
  background: var(--bg-secondary);
}

.save-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  cursor: pointer;
  font-weight: var(--font-semibold);
}

.save-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: var(--shadow);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Toast Messages */
.toast {
  position: fixed;
  bottom: var(--space-lg);
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-lg) var(--space-lg);
  border-radius: var(--radius);
  color: white;
  font-weight: var(--font-semibold);
  box-shadow: var(--shadow);
  z-index: 1001;
  max-width: 400px;
  animation: fadeOut 3s ease-out;
}

@keyframes fadeOut {
  0%, 60% { opacity: 1; }
  100% { opacity: 0; }
}

.toast.success {
  background: var(--success);
}

.toast.error {
  background: var(--error);
}

.toast.info {
  background: #4BC0D9;
}

.hamburger.active span:nth-child(1) {
  transform: rotate(-45deg) translate(-5px, 6px);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  transform: rotate(45deg) translate(-5px, -6px);
}

/* Screen/Print Visibility */
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
  
  .header, .pdf-container .nav-arrow, .pdf-counter, .pdf-controls {
    display: none !important;
  }
}

/* Responsive Design - Mobile First Approach */
@media (max-width: 640px) {
  .main-content {
    padding: var(--space-md);
  }
  
  .content-header {
    flex-direction: column;
    gap: var(--space-md);
    align-items: stretch;
  }
  
  .content-header h2 {
    font-size: var(--text-lg);
  }
  
  .employee-controls,
  .site-controls,
  .timesheet-controls {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-sm);
  }
  
  .search-input {
    min-width: auto;
  }
  
  .table-container {
    border-radius: var(--radius);
  }
  
  .employee-table th,
  .employee-table td {
    padding: var(--space-sm);
    font-size: var(--text-sm);
  }
  
  .timesheet-table th {
    min-width: 3rem;
    padding: var(--space-sm) var(--space-sm);
  }
  
  .timesheet-table th:first-child {
    min-width: 10rem;
    width: 10rem;
  }
  
  .timesheet-cell {
    min-width: 3rem;
    width: 3rem;
    padding: var(--space-sm);
  }
  
  .actions-cell {
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .action-btn {
    font-size: 0.6rem;
    padding: var(--space-sm) var(--space-sm);
  }
  
  .modal {
    width: 95%;
    margin: var(--space-md);
  }
  
  .modal-header,
  .modal-form {
    padding: var(--space-lg);
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .main-content {
    padding: var(--space-lg);
  }
  
  .content-header {
    flex-wrap: wrap;
    gap: var(--space-md);
  }
  
  .employee-table th,
  .employee-table td {
    padding: var(--space-sm) var(--space-md);
  }
}

@media (min-width: 1025px) {
  .nav-menu {
    display: flex;
    position: static;
    flex-direction: row;
    padding: 0;
    box-shadow: none;
    background: transparent;
    gap: var(--space-lg);
    border: none;
  }
  
  .hamburger {
    display: none;
  }
}
</style>