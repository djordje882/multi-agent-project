import { computed } from 'vue'

const translations = {
  en: {
    employeeManagement: 'Employee Management',
    employees: 'Employees',
    sites: 'Sites',
    roles: 'Roles',
    timesheet: 'Timesheet'
  },
  fr: {
    employeeManagement: 'Gestion des Employés',
    employees: 'Employés',
    sites: 'Sites',
    roles: 'Rôles',
    timesheet: 'Feuille de Temps'
  }
}

export function useTranslations() {
  const t = computed(() => ({
    value: (key) => translations.fr[key] || key
  }))

  const getCurrencySymbol = () => 'FCFA'

  return {
    t,
    getCurrencySymbol
  }
}