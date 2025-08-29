<template>
  <div>
    <div class="content-header">
      <h2>{{ config.title }}</h2>
      <SearchControls
        :search-term="crud.searchTerm.value"
        :sort-by="crud.sortBy.value"
        :search-placeholder="config.searchPlaceholder"
        :sort-options="crud.sortOptions"
        :add-button-text="config.addButtonText"
        @search="crud.searchTerm.value = $event"
        @sort="crud.sortBy.value = $event"
        @add="crud.showAddModal"
      />
    </div>

    <TableComponent
      :columns="crud.tableColumns"
      :data="crud.filteredData.value"
      :entity-type="config.entityType"
      :no-data-message="crud.noDataMessage.value"
      :currency-symbol="config.currencySymbol"
      @edit="crud.editEntity"
      @delete="crud.deleteEntity"
      @fire="(id) => handleCustomAction('fire', id)"
      @hire="(id) => handleCustomAction('hire', id)"
    />

    <ModalComponent
      :show="crud.showModal.value"
      :title="crud.modalTitle.value"
      :entity-type="config.entityType"
      :form="crud.entityForm.value"
      :button-text="crud.buttonText.value"
      :loading="loading.value"
      :roles="config.extraData?.value?.roles || config.extraData?.roles"
      :sites="config.extraData?.value?.sites || config.extraData?.sites"
      @close="crud.closeModal"
      @save="crud.saveEntity"
    />
  </div>
</template>

<script>
import SearchControls from './SearchControls.vue'
import TableComponent from './TableComponent.vue'
import ModalComponent from './ModalComponent.vue'
import { useCrud } from '../composables/useCrud.js'
import { inject, ref } from 'vue'

export default {
  name: 'CrudView',
  components: {
    SearchControls,
    TableComponent,
    ModalComponent
  },
  props: {
    config: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const loading = inject('loading')
    const showMessage = inject('showMessage')
    const withLoading = inject('withLoading')
    
    const injectedProps = { loading, showMessage, withLoading }
    const crud = useCrud(props.config, injectedProps)
    
    const handleCustomAction = async (actionName, id) => {
      const action = props.config.customActions?.[actionName]
      if (action) {
        await action(id)
        await crud.loadData()
      }
    }
    
    return {
      crud,
      loading,
      handleCustomAction
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

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>