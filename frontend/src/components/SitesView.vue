<template>
  <CrudView :config="crudConfig" />
</template>

<script>
import CrudView from './CrudView.vue'

export default {
  name: 'SitesView',
  components: {
    CrudView
  },
  setup() {
    const crudConfig = {
      endpoint: 'construction-sites',
      entityName: 'Site de Construction',
      entityType: 'sites',
      title: 'Sites de Construction',
      searchPlaceholder: 'Rechercher des sites...',
      addButtonText: 'Ajouter Site',
      formDefaults: {
        name: '',
        address: ''
      },
      sortOptions: [
        { value: 'name', label: 'Trier par Nom' },
        { value: 'address', label: 'Trier par Adresse' }
      ],
      tableColumns: [
        { key: 'name', label: 'Nom', class: 'name-cell' },
        { key: 'address', label: 'Adresse' },
        { key: 'actions', label: 'Actions', class: 'actions-cell' }
      ],
      searchFields: ['name', 'address'],
      messages: {
        loadError: 'Erreur lors du chargement des sites',
        createSuccess: 'Site créé avec succès',
        updateSuccess: 'Site mis à jour avec succès',
        deleteSuccess: 'Site supprimé avec succès',
        saveError: 'Erreur lors de la sauvegarde du site',
        deleteError: 'Erreur lors de la suppression du site'
      }
    }

    return {
      crudConfig
    }
  }
}
</script>