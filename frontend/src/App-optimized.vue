<template>
  <div id="app">
    <!-- Header Navigation -->
    <header class="header">
      <div class="header-container">
        <div class="nav-brand">
          <h1>{{ t.value('employeeManagement') }}</h1>
        </div>
        <nav class="nav-menu" :class="{ 'active': menuOpen }">
          <a href="#" @click="showView('employees')" class="nav-link" :class="{ active: currentView === 'employees' }">{{ t.value('employees') }}</a>
          <a href="#" @click="showView('sites')" class="nav-link" :class="{ active: currentView === 'sites' }">{{ t.value('sites') }}</a>
          <a href="#" @click="showView('roles')" class="nav-link" :class="{ active: currentView === 'roles' }">{{ t.value('roles') }}</a>
          <a href="#" @click="showView('timesheet')" class="nav-link" :class="{ active: currentView === 'timesheet' }">{{ t.value('timesheet') }}</a>
          <a href="#" @click="showView('settings')" class="nav-link" :class="{ active: currentView === 'settings' }">{{ t.value('settings') }}</a>
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
      <EmployeeView 
        v-if="currentView === 'employees'"
        :loading="loading"
        :show-message="showMessage"
        :with-loading="withLoading"
        :roles="roles"
        :sites="sites" />
      
      <SitesView 
        v-if="currentView === 'sites'"
        :loading="loading"
        :show-message="showMessage"
        :with-loading="withLoading" />
      
      <RolesView 
        v-if="currentView === 'roles'"
        :loading="loading"
        :show-message="showMessage"
        :with-loading="withLoading" />
      
      <TimesheetView 
        v-if="currentView === 'timesheet'"
        :loading="loading"
        :show-message="showMessage"
        :with-loading="withLoading" />
      
      <SettingsView v-if="currentView === 'settings'" />
    </main>

    <!-- Message Toast -->
    <div v-if="message" class="toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useTranslations } from './composables/useTranslations'
import EmployeeView from './components/EmployeeView.vue'
import SitesView from './components/SitesView.vue'
import RolesView from './components/RolesView.vue'
import TimesheetView from './components/TimesheetView.vue'
import SettingsView from './components/SettingsView.vue'
import axios from 'axios'

const API_BASE = '/api'

export default {
  name: 'App',
  components: {
    EmployeeView,
    SitesView,
    RolesView,
    TimesheetView,
    SettingsView
  },
  setup() {
    const { t } = useTranslations()

    // State
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const menuOpen = ref(false)
    const currentView = ref('employees')
    const roles = ref([])
    const sites = ref([])

    // Methods
    const withLoading = async (asyncOperation) => {
      loading.value = true
      try {
        return await asyncOperation()
      } finally {
        loading.value = false
      }
    }

    const showMessage = (text, type = 'success') => {
      message.value = text
      messageType.value = type
      setTimeout(() => clearMessage(), 3000)
    }
    
    const clearMessage = () => {
      message.value = ''
    }

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
    }

    const showView = (view) => {
      currentView.value = view
      menuOpen.value = false
    }

    const loadRoles = async () => {
      try {
        const response = await axios.get(`${API_BASE}/roles`)
        roles.value = response.data
      } catch (error) {
        console.error('Error loading roles:', error)
        showMessage('Failed to load roles', 'error')
      }
    }

    const loadSites = async () => {
      try {
        const response = await axios.get(`${API_BASE}/construction-sites`)
        sites.value = response.data
      } catch (error) {
        showMessage('Error loading construction sites: ' + (error.response?.data?.detail || error.message), 'error')
      }
    }

    onMounted(async () => {
      await loadRoles()
      await loadSites()
    })

    return {
      t,
      loading,
      message,
      messageType,
      menuOpen,
      currentView,
      roles,
      sites,
      withLoading,
      showMessage,
      toggleMenu,
      showView
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* Core Colors */
  --primary-bg: #1A1A2E;
  --secondary-bg: #2C2C4E;
  --primary-accent: #8B5CF6;
  --secondary-accent: #4BC0D9;
  --text-primary: #E0E0E0;
  --text-secondary: #A0A0A0;
  
  /* Status Colors */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* Typography */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  
  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Inter, system-ui, -apple-system, sans-serif;
  background: var(--primary-bg);
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  background: var(--secondary-bg);
  box-shadow: var(--shadow-md);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
}

.nav-brand h1 {
  color: var(--primary-accent);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
}

.nav-menu {
  display: flex;
  gap: var(--space-lg);
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-medium);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
  color: var(--primary-accent);
  background: rgba(139, 92, 246, 0.1);
}

.hamburger {
  display: none;
  flex-direction: column;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-sm);
}

.hamburger span {
  width: 1.5rem;
  height: 2px;
  background: var(--text-primary);
  margin: 2px 0;
  transition: 0.3s;
}

/* Main Content */
.main-content {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  width: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.content-header h2 {
  color: var(--text-primary);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
}

/* Controls */
.employee-controls,
.site-controls,
.timesheet-controls {
  display: flex;
  gap: var(--space-md);
  align-items: center;
  flex-wrap: wrap;
}

.search-input,
.sort-select,
.setting-select {
  background: var(--secondary-bg);
  border: 1px solid rgba(224, 224, 224, 0.15);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.search-input:focus,
.sort-select:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--primary-accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

/* Buttons */
.btn {
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.add-btn {
  background: var(--primary-accent);
}

.pdf-btn {
  background: var(--error);
}

.action-btn {
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--text-xs);
  margin: 0 2px;
}

.edit-btn {
  background: var(--secondary-accent);
}

.fire-btn,
.delete-btn {
  background: var(--error);
}

.hire-btn {
  background: var(--success);
}

/* Tables */
.table-container {
  background: var(--secondary-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.employee-table {
  width: 100%;
  border-collapse: collapse;
}

.employee-table th,
.employee-table td {
  padding: var(--space-md);
  text-align: left;
  border-bottom: 1px solid rgba(224, 224, 224, 0.1);
}

.employee-table th {
  background: rgba(44, 44, 78, 0.8);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.name-cell {
  font-weight: var(--font-medium);
}

.role-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-cell {
  white-space: nowrap;
}

.status-badge {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: capitalize;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.status-badge.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: var(--space-xl);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: var(--secondary-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid rgba(224, 224, 224, 0.1);
}

.modal-header h3 {
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
  padding: var(--space-xs);
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
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  background: var(--primary-bg);
  border: 1px solid rgba(224, 224, 224, 0.15);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
  margin-top: var(--space-xl);
}

.cancel-btn {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid rgba(224, 224, 224, 0.15);
}

.save-btn {
  background: var(--primary-accent);
}

/* Settings */
.settings-container {
  max-width: 600px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.setting-item label {
  min-width: 120px;
  font-weight: var(--font-medium);
}

/* Toast */
.toast {
  position: fixed;
  bottom: var(--space-xl);
  right: var(--space-xl);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  color: white;
  font-weight: var(--font-medium);
  box-shadow: var(--shadow-lg);
  z-index: 3000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: var(--success);
}

.toast.error {
  background: var(--error);
}

.toast.warning {
  background: var(--warning);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Timesheet specific styles */
.timesheet-container {
  overflow: auto;
  cursor: grab;
}

.timesheet-container:active {
  cursor: grabbing;
}

.timesheet-table {
  min-width: 100%;
  white-space: nowrap;
}

.timesheet-table th:first-child,
.timesheet-table td:first-child {
  position: sticky;
  left: 0;
  background: var(--secondary-bg);
  z-index: 10;
}

.timesheet-cell {
  min-width: 120px;
  text-align: center;
}

.timesheet-cell.weekend {
  background: rgba(239, 68, 68, 0.1);
}

.employee-name {
  font-weight: var(--font-semibold);
}

.employee-role {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.status-select,
.time-input,
.bonus-input {
  width: 100%;
  margin: 2px 0;
  padding: 2px 4px;
  font-size: var(--text-xs);
  background: var(--primary-bg);
  border: 1px solid rgba(224, 224, 224, 0.15);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
}

.fixed-hours {
  font-size: var(--text-xs);
  padding: var(--space-xs);
  text-align: center;
  color: var(--text-secondary);
}

.justified-check {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 10px;
}

/* Responsive */
@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  .nav-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--secondary-bg);
    flex-direction: column;
    padding: var(--space-lg);
    box-shadow: var(--shadow-md);
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
  }

  .nav-menu.active {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  .content-header {
    flex-direction: column;
    align-items: stretch;
  }

  .employee-controls,
  .site-controls,
  .timesheet-controls {
    justify-content: center;
  }

  .table-container {
    overflow-x: auto;
  }

  .modal {
    width: 95%;
  }
}
</style>