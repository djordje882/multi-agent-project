<template>
  <CrudView :config="crudConfig" />
</template>

<script>
import CrudView from './CrudView.vue'

export default {
  name: 'RolesView',
  components: {
    CrudView
  },
  setup() {
    const crudConfig = {
      endpoint: 'roles',
      entityName: 'Rôle',
      entityType: 'roles',
      title: 'Rôles',
      searchPlaceholder: 'Rechercher des rôles...',
      addButtonText: 'Ajouter Rôle',
      formDefaults: {
        name: ''
      },
      sortOptions: [
        { value: 'name', label: 'Trier par Nom' }
      ],
      tableColumns: [
        { key: 'name', label: 'Nom', class: 'name-cell' },
        { key: 'actions', label: 'Actions', class: 'actions-cell' }
      ],
      searchFields: ['name'],
      messages: {
        loadError: 'Erreur lors du chargement des rôles',
        createSuccess: 'Rôle créé avec succès',
        updateSuccess: 'Rôle mis à jour avec succès',
        deleteSuccess: 'Rôle supprimé avec succès',
        saveError: 'Erreur lors de la sauvegarde du rôle',
        deleteError: 'Erreur lors de la suppression du rôle'
      }
    }

    return {
      crudConfig
    }
  }
}
</script>