<template>
  <div id="app">
    <!-- Header Navigation -->
    <header class="header">
      <div class="header-container">
        <div class="nav-brand">
          <h1>{{ t.value('employeeManagement') }}</h1>
        </div>
        <nav class="nav-menu" :class="{ 'active': menuOpen }">
          <a v-for="nav in navItems" :key="nav.view" href="#" @click="showView(nav.view)" class="nav-link" :class="{ active: currentView === nav.view }">{{ t.value(nav.key) }}</a>
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
        :roles="roles"
        :sites="sites" />
      
      <SitesView v-if="currentView === 'sites'" />
      
      <RolesView v-if="currentView === 'roles'" />
      
      <TimesheetView 
        v-if="currentView === 'timesheet'"
        @generate-pdf="handleGeneratePDF" />
      
      
      <PDFView 
        v-if="currentView === 'pdf'"
        :pdf-data="pdfData" />
    </main>

    <!-- Message Toast -->
    <div v-if="message" class="toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, provide } from 'vue'
import { useTranslations } from './composables/useTranslations'
import EmployeeView from './components/EmployeeView.vue'
import SitesView from './components/SitesView.vue'
import RolesView from './components/RolesView.vue'
import TimesheetView from './components/TimesheetView.vue'
import PDFView from './components/PDFView.vue'
import axios from 'axios'

const API_BASE = '/api'

export default {
  name: 'App',
  components: {
    EmployeeView,
    SitesView,
    RolesView,
    TimesheetView,
    PDFView
  },
  setup() {
    const { t } = useTranslations()

    // Navigation configuration
    const navItems = [
      { view: 'employees', key: 'employees' },
      { view: 'sites', key: 'sites' },
      { view: 'roles', key: 'roles' },
      { view: 'timesheet', key: 'timesheet' }
    ]

    // State
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const menuOpen = ref(false)
    const currentView = ref('employees')
    const roles = ref([])
    const sites = ref([])
    const pdfData = ref(null)

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
      setTimeout(() => { message.value = '' }, 3000)
    }

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
    }

    const showView = (view) => {
      currentView.value = view
      menuOpen.value = false
    }

    const handleGeneratePDF = (data) => {
      pdfData.value = data
      currentView.value = 'pdf'
    }

    const loadData = async (endpoint, dataRef, errorMessage) => {
      try {
        const response = await axios.get(`${API_BASE}/${endpoint}`)
        dataRef.value = response.data
      } catch (error) {
        showMessage(`${errorMessage}: ` + (error.response?.data?.detail || error.message), 'error')
      }
    }

    // Provide shared utilities to all child components
    provide('loading', loading)
    provide('showMessage', showMessage)
    provide('withLoading', withLoading)

    onMounted(async () => {
      await loadData('roles', roles, 'Failed to load roles')
      await loadData('construction-sites', sites, 'Error loading construction sites')
    })

    return {
      t,
      navItems,
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
      showView,
      handleGeneratePDF,
      pdfData
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

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

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-sm);
  min-width: 200px;
  box-shadow: var(--shadow);
}

.nav-menu.active {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.nav-link:hover,
.nav-link.active {
  color: var(--accent);
  background: rgba(139, 92, 246, 0.1);
}

.hamburger {
  display: flex;
  flex-direction: column;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-sm);
  gap: 4px;
}

.hamburger span {
  width: 20px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
}

/* Main Content */
.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-lg);
  width: 100%;
}

/* Toast */
.toast {
  position: fixed;
  bottom: var(--space-lg);
  right: var(--space-lg);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius);
  color: white;
  font-weight: var(--font-semibold);
  box-shadow: var(--shadow);
  z-index: 1000;
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


/* Responsive */
@media (max-width: 768px) {
  .header-container {
    padding: 0 var(--space-md);
  }

  .main-content {
    padding: var(--space-md);
  }

  .toast {
    bottom: var(--space-md);
    right: var(--space-md);
    left: var(--space-md);
  }
}
</style>