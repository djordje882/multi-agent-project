<template>
  <div class="table-container">
    <table class="employee-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data" :key="item.id">
          <td v-for="column in columns" :key="column.key" :class="column.class">
            <template v-if="column.key === 'actions'">
              <div class="actions-cell">
                <button @click="$emit('edit', item)" class="action-btn edit-btn">Modifier</button>
                <button v-if="entityType === 'employees' && item.status === 'active'" @click="$emit('fire', item.id)" class="action-btn fire-btn">Licencier</button>
                <button v-if="entityType === 'employees' && item.status === 'inactive'" @click="$emit('hire', item.id)" class="action-btn hire-btn">Embaucher</button>
                <button @click="$emit('delete', item.id)" class="action-btn delete-btn">Supprimer</button>
              </div>
            </template>
            <span v-else-if="column.key === 'status'" :class="['status-badge', item.status]">{{ item.status }}</span>
            <span v-else-if="column.key === 'hourly_rate'">{{ currencySymbol }} {{ item.hourly_rate }}</span>
            <span v-else :title="getColumnValue(item, column.key)">{{ getColumnValue(item, column.key) }}</span>
          </td>
        </tr>
        <tr v-if="data.length === 0">
          <td :colspan="columns.length" class="no-data">{{ noDataMessage }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'TableComponent',
  props: {
    columns: {
      type: Array,
      required: true
    },
    data: {
      type: Array,
      required: true
    },
    entityType: {
      type: String,
      required: true
    },
    noDataMessage: {
      type: String,
      default: 'Aucune donnée trouvée'
    },
    currencySymbol: {
      type: String,
      default: 'FCFA'
    }
  },
  emits: ['edit', 'fire', 'hire', 'delete'],
  methods: {
    getColumnValue(item, key) {
      return item[key] || ''
    }
  }
}
</script>

<style scoped>
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
}

.name-cell {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rate-cell {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  font-weight: var(--font-semibold);
  color: var(--success);
  text-align: right;
  white-space: nowrap;
}

.status-badge {
  padding: var(--space-sm) var(--space-md);
  border-radius: 20px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
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
  gap: 4px;
  white-space: nowrap;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: var(--radius);
  font-size: 10px;
  font-weight: var(--font-semibold);
  cursor: pointer;
  text-transform: uppercase;
  min-width: 50px;
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

.hire-btn {
  background: var(--success);
  color: white;
}

.delete-btn {
  background: var(--error);
  color: white;
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: var(--space-lg);
}
</style>