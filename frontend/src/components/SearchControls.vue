<template>
  <div class="controls">
    <input 
      :value="searchTerm" 
      @input="$emit('search', $event.target.value)"
      type="text" 
      :placeholder="searchPlaceholder" 
      class="search-input"
    >
    <select 
      :value="sortBy" 
      @change="$emit('sort', $event.target.value)"
      class="sort-select"
    >
      <option v-for="option in sortOptions" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <button @click="$emit('add')" class="btn add-btn">
      + {{ addButtonText }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'SearchControls',
  props: {
    searchTerm: {
      type: String,
      default: ''
    },
    sortBy: {
      type: String,
      default: 'name'
    },
    searchPlaceholder: {
      type: String,
      required: true
    },
    sortOptions: {
      type: Array,
      required: true
    },
    addButtonText: {
      type: String,
      required: true
    }
  },
  emits: ['search', 'sort', 'add']
}
</script>

<style scoped>
.controls {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.search-input {
  padding: var(--space-sm) var(--space-md);
  border: none !important;
  border-radius: var(--radius);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: var(--text-sm);
  outline: none !important;
}

.search-input:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}


.sort-select {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-sm);
  border-radius: var(--radius);
}

.sort-select:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.btn {
  padding: var(--space-sm) var(--space-lg);
  border: none;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  color: white;
}

.add-btn {
  background: var(--accent);
}

.add-btn:hover {
  background: var(--accent-hover);
}

.pdf-btn {
  background: var(--error);
  color: white;
}

@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-sm);
  }
}
</style>