<template>
  <CrudView :config="crudConfig" />
</template>

<script>
import CrudView from './CrudView.vue'
import axios from 'axios'
import { inject, computed } from 'vue'

const API_BASE = '/api'

export default {
  name: 'EmployeeView',
  components: {
    CrudView
  },
  props: {
    roles: Array,
    sites: Array
  },
  setup(props) {
    const showMessage = inject('showMessage')
    const withLoading = inject('withLoading')
    
    const fireEmployee = async (employeeId) => {
      const fireDate = prompt('Entrez la date de licenciement (AAAA-MM-JJ):')
      if (!fireDate || !confirm('Êtes-vous sûr de vouloir licencier cet employé?')) {
        return
      }

      await withLoading(async () => {
        try {
          const response = await axios.put(`${API_BASE}/employees/${employeeId}/fire`, { fire_date: fireDate })
          showMessage(response.data.message, 'success')
        } catch (error) {
          showMessage('Erreur lors du licenciement: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    }

    const hireEmployee = async (employeeId) => {
      if (!confirm('Êtes-vous sûr de vouloir embaucher cet employé? Il sera marqué comme actif.')) {
        return
      }

      await withLoading(async () => {
        try {
          const response = await axios.put(`${API_BASE}/employees/${employeeId}/hire`)
          showMessage(response.data.message, 'success')
        } catch (error) {
          showMessage('Erreur lors de l\'embauche: ' + (error.response?.data?.detail || error.message), 'error')
        }
      })
    }

    const crudConfig = {
      endpoint: 'employees',
      entityName: 'Employé',
      entityType: 'employees',
      title: 'Liste des Employés',
      searchPlaceholder: 'Rechercher des employés...',
      addButtonText: 'Ajouter Employé',
      currencySymbol: 'FCFA',
      formDefaults: {
        name: '',
        last_name: '',
        role_id: '',
        construction_site_id: '',
        hourly_rate: ''
      },
      sortOptions: [
        { value: 'name', label: 'Trier par Nom' },
        { value: 'construction_site', label: 'Trier par Site' },
        { value: 'hourly_rate', label: 'Trier par Taux' },
        { value: 'status', label: 'Trier par Statut' }
      ],
      tableColumns: [
        { key: 'name', label: 'Nom', class: 'name-cell' },
        { key: 'last_name', label: 'Nom de Famille', class: 'name-cell' },
        { key: 'role', label: 'Rôle', class: 'role-cell' },
        { key: 'construction_site', label: 'Site de Construction' },
        { key: 'hourly_rate', label: 'Taux Horaire', class: 'rate-cell' },
        { key: 'status', label: 'Statut' },
        { key: 'actions', label: 'Actions', class: 'actions-cell' }
      ],
      searchFields: ['name', 'last_name', 'role', 'construction_site'],
      messages: {
        loadError: 'Erreur lors du chargement des employés',
        createSuccess: 'Employé créé avec succès',
        updateSuccess: 'Employé mis à jour avec succès',
        deleteSuccess: 'Employé supprimé avec succès',
        saveError: 'Erreur lors de la sauvegarde de l\'employé',
        deleteError: 'Erreur lors de la suppression de l\'employé'
      },
      customActions: {
        fire: fireEmployee,
        hire: hireEmployee
      },
      extraData: computed(() => ({
        roles: props.roles || [],
        sites: props.sites || []
      }))
    }

    return {
      crudConfig
    }
  }
}
</script>