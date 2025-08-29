import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

export function useCrud(config, props) {
  if (!config) {
    throw new Error('useCrud: config is required')
  }
  
  const {
    endpoint,
    entityName,
    formDefaults = {},
    sortOptions = [],
    tableColumns = [],
    searchFields = [],
    messages = {}
  } = config

  // State
  const data = ref([])
  const searchTerm = ref('')
  const sortBy = ref('name')
  const showModal = ref(false)
  const editingEntity = ref(null)
  const entityForm = ref({ ...formDefaults })

  // Computed
  const filteredData = computed(() => {
    let filtered = data.value.filter(item => {
      const searchLower = searchTerm.value.toLowerCase()
      return searchFields.some(field => 
        (item[field] || '').toLowerCase().includes(searchLower)
      )
    })

    return filtered.sort((a, b) => {
      if (sortBy.value === 'hourly_rate') {
        return parseFloat(a.hourly_rate || 0) - parseFloat(b.hourly_rate || 0)
      }
      return (a[sortBy.value] || '').localeCompare(b[sortBy.value] || '')
    })
  })

  const modalTitle = computed(() => (editingEntity.value ? 'Modifier' : 'Ajouter') + ` ${entityName}`)
  const buttonText = computed(() => editingEntity.value ? 'Mettre à Jour' : 'Créer')
  const noDataMessage = computed(() => data.value.length === 0 ? `Aucun ${entityName.toLowerCase()} trouvé` : `Aucun ${entityName.toLowerCase()} ne correspond à votre recherche`)

  // Methods
  const loadData = async () => {
    await props.withLoading(async () => {
      try {
        const response = await axios.get(`${API_BASE}/${endpoint}`)
        data.value = response.data
      } catch (error) {
        props.showMessage(`${messages.loadError}: ` + (error.response?.data?.detail || error.message), 'error')
      }
    })
  }

  const showAddModal = () => {
    editingEntity.value = null
    entityForm.value = { ...formDefaults }
    showModal.value = true
  }

  const editEntity = (entity) => {
    editingEntity.value = entity
    entityForm.value = { ...entity }
    showModal.value = true
  }

  const closeModal = () => {
    showModal.value = false
    editingEntity.value = null
  }

  const saveEntity = async () => {
    await props.withLoading(async () => {
      try {
        if (editingEntity.value) {
          await axios.put(`${API_BASE}/${endpoint}/${editingEntity.value.id}`, entityForm.value)
          props.showMessage(messages.updateSuccess, 'success')
        } else {
          await axios.post(`${API_BASE}/${endpoint}`, entityForm.value)
          props.showMessage(messages.createSuccess, 'success')
        }
        closeModal()
        await loadData()
      } catch (error) {
        props.showMessage(`${messages.saveError}: ` + (error.response?.data?.detail || error.message), 'error')
      }
    })
  }

  const deleteEntity = async (entityId) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer ce ${entityName.toLowerCase()}? Cette action est irréversible.`)) {
      return
    }

    await props.withLoading(async () => {
      try {
        await axios.delete(`${API_BASE}/${endpoint}/${entityId}`)
        props.showMessage(messages.deleteSuccess, 'success')
        await loadData()
      } catch (error) {
        props.showMessage(`${messages.deleteError}: ` + (error.response?.data?.detail || error.message), 'error')
      }
    })
  }

  onMounted(() => {
    loadData()
  })

  return {
    // State
    data,
    searchTerm,
    sortBy,
    showModal,
    editingEntity,
    entityForm,
    
    // Config
    sortOptions,
    tableColumns,
    
    // Computed
    filteredData,
    modalTitle,
    buttonText,
    noDataMessage,
    
    // Methods
    loadData,
    showAddModal,
    editEntity,
    closeModal,
    saveEntity,
    deleteEntity
  }
}